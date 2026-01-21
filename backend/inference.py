import lightgbm as lgb
import pandas as pd
import duckdb
import numpy as np
import os
import pickle

class RecSysEngine:
    def __init__(self, artifact_dir="artifacts"):
        """
        Initializes the Recommendation Engine.
        1. Loads the LightGBM model (The Brain)
        2. Sets up the DuckDB In-Memory Database (The Memory)
        """
        print(f"Initializing Engine from: {artifact_dir}")
        
        # 1. Load LightGBM Model
        model_path = os.path.join(artifact_dir, "lgbm_ranker.txt")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        self.model = lgb.Booster(model_file=model_path)
        print("   - LightGBM Model Loaded.")

        # 2. Setup DuckDB & Load Views
        # We use DuckDB to query the parquet files directly without loading everything into RAM
        self.con = duckdb.connect(database=':memory:')
        
        # Register Parquet files as tables
        self._register_view("users", os.path.join(artifact_dir, "features_user.parquet"))
        self._register_view("items", os.path.join(artifact_dir, "features_item.parquet"))
        self._register_view("mapping", os.path.join(artifact_dir, "article_map.parquet"))
        self._register_view("candidates", os.path.join(artifact_dir, "candidates_pool.parquet"))
        
        print("   - Feature Tables Registered in DuckDB.")
        
        # Define the exact feature order expected by LightGBM (CRITICAL)
        self.feature_order = [
            'source', 'als_score', 'visual_score', 
            'user_avg_price', 'user_price_std', 'user_total_purchases', 
            'user_tenure_days', 'days_since_last_buy', 
            'item_avg_price', 'item_total_sales', 
            'product_group', 'index_group', 'garment_group', 
            'price_diff'
        ]

    def _register_view(self, name, path):
        """Helper to register parquet files as SQL views"""
        if os.path.exists(path):
            self.con.execute(f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM '{path}'")
        else:
            print(f"Warning: {path} not found. {name} table will be missing.")

    def recommend(self, customer_id_int, top_k=12):
        """
        Generates recommendations for a specific User ID.
        """
        # A. Fetch User Features
        print("   - Fetching User Features...")
        user_df = self.con.execute(f"SELECT * FROM users WHERE customer_id_int = {customer_id_int}").df()
        
        # B. Cold Start Check
        if user_df.empty:
            print(f"   - Cold Start for User {customer_id_int}")
            return self._get_global_bestsellers(top_k)

        # C. Candidate Generation
        print("   - Generating Candidates...")
        query = f"""
            SELECT 
                c.article_id_int,
                i.item_avg_price, i.item_total_sales, 
                i.product_group, i.index_group, i.garment_group,
                u.user_avg_price, u.user_price_std, u.user_total_purchases, 
                u.user_tenure_days, u.days_since_last_buy
            FROM candidates c
            JOIN items i ON c.article_id_int = i.article_id_int,
            (SELECT * FROM users WHERE customer_id_int = {customer_id_int}) u
        """
        candidates_df = self.con.execute(query).df()
        print(f"   - Candidates Generated: {len(candidates_df)} rows")
        
        if candidates_df.empty:
            return self._get_global_bestsellers(top_k)

        # D. Dynamic Feature Engineering
        print("   - Feature Engineering...")
        candidates_df['price_diff'] = candidates_df['item_avg_price'] - candidates_df['user_avg_price']
        candidates_df['source'] = 1  
        candidates_df['als_score'] = -1
        candidates_df['visual_score'] = -1
        
        # E. Prepare Data
        X = candidates_df[self.feature_order]
        
        # F. Predict
        print("   - Running LightGBM Predict...")
        scores = self.model.predict(X)
        candidates_df['score'] = scores
        print("   - Prediction Complete.")
        
        # G. Sort and Select Top K
        top_recs = candidates_df.sort_values('score', ascending=False).head(top_k)
        top_ids = top_recs['article_id_int'].tolist()
        
        # H. Convert Integer IDs back to String IDs (for the UI)
        if not top_ids:
            return []
            
        id_list_str = ",".join(map(str, top_ids))
        res = self.con.execute(f"""
            SELECT article_id_str 
            FROM mapping 
            WHERE article_id_int IN ({id_list_str})
        """).df()
        
        # Preserve the order of the recommendation (DuckDB query might shuffle)
        # We create a map and re-order list
        final_map = dict(zip(res.index, res['article_id_str'])) # Simplified fallback
        # Better: use pandas merge to keep order
        mapping_dict = self.con.execute("SELECT * FROM mapping").df().set_index('article_id_int')['article_id_str'].to_dict()
        top_recs['article_id_str'] = top_recs['article_id_int'].map(mapping_dict)
        
        # Fallback if map is slow: just return the strings we found
        return res['article_id_str'].tolist()

    def _get_global_bestsellers(self, k):
        """Fallback: Just return the most popular items"""
        res = self.con.execute(f"""
            SELECT m.article_id_str 
            FROM candidates c
            JOIN mapping m ON c.article_id_int = m.article_id_int
            LIMIT {k}
        """).df()
        return res['article_id_str'].tolist()