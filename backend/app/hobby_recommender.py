import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import numpy as np

def preprocess_lifestyle_data(df: pd.DataFrame):
    """
    Preprocess the lifestyle dataset for hobby recommendations.
    Handles one-hot encoding for categorical features, normalization for numeric.
    """
    # Identify column types
    numeric_cols = ['age', 'height', 'weight', 'spice_tolerance', 'social_media_hours']
    categorical_cols = ['favorite_cuisines', 'movie_genres', 'series_genres', 'gaming_platforms',
                       'music_genres', 'reading_genres', 'shopping_preferences', 'travel_destinations',
                       'hobbies', 'clubs']

    # Handle missing values
    df = df.fillna('')

    # One-hot encode categorical columns
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    encoded_cats = encoder.fit_transform(df[categorical_cols])
    encoded_cat_df = pd.DataFrame(encoded_cats, columns=encoder.get_feature_names_out(categorical_cols))

    # Normalize numeric columns
    scaler = StandardScaler()
    scaled_nums = scaler.fit_transform(df[numeric_cols])
    scaled_num_df = pd.DataFrame(scaled_nums, columns=numeric_cols)

    # Combine processed features
    processed_df = pd.concat([scaled_num_df, encoded_cat_df], axis=1)

    return processed_df, encoder, scaler

def recommend_hobbies(df: pd.DataFrame, user_id, top_k=5):
    """
    Recommend new hobbies/clubs for a user based on similar users' preferences.
    """
    # Preprocess data
    processed_df, encoder, scaler = preprocess_lifestyle_data(df)

    # Find similar users using cosine similarity
    sim_matrix = cosine_similarity(processed_df)
    sim_df = pd.DataFrame(sim_matrix, index=df['user_id'], columns=df['user_id'])

    user_id = int(user_id)
    if user_id not in sim_df.index:
        return []

    # Get similar users
    similar_users = sim_df[user_id].sort_values(ascending=False).index[1:top_k+1]  # Exclude self

    # Collect hobbies/clubs from similar users
    user_hobbies = set(df[df['user_id'] == user_id]['hobbies'].str.split(',').explode().str.strip())
    user_clubs = set(df[df['user_id'] == user_id]['clubs'].str.split(',').explode().str.strip())

    recommendations = {}
    for sim_user in similar_users:
        sim_hobbies = df[df['user_id'] == sim_user]['hobbies'].str.split(',').explode().str.strip()
        sim_clubs = df[df['user_id'] == sim_user]['clubs'].str.split(',').explode().str.strip()

        for hobby in sim_hobbies:
            if hobby not in user_hobbies and hobby:
                recommendations[hobby] = recommendations.get(hobby, 0) + 1

        for club in sim_clubs:
            if club not in user_clubs and club:
                recommendations[club] = recommendations.get(club, 0) + 1

    # Sort by frequency and return top recommendations
    sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    return [rec[0] for rec in sorted_recs[:top_k]]
