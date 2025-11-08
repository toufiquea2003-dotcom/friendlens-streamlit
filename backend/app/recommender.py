import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def get_recommendations(df: pd.DataFrame, user_id, top_k=5):
    # If dataset has 'User' and 'Friend' columns (edge list), build user-friend matrix
    if 'User' in df.columns and 'Friend' in df.columns:
        pivot = pd.crosstab(df['User'].astype(str), df['Friend'].astype(str))
    else:
        # fallback: use first column as user id and numeric attributes for similarity
        idx_col = df.columns[0]
        pivot = df.set_index(idx_col).select_dtypes(include=['number']).fillna(0)

    try:
        sim = cosine_similarity(pivot)
        sim_df = pd.DataFrame(sim, index=pivot.index, columns=pivot.index)
    except Exception as e:
        return []

    user_id = str(user_id)
    if user_id not in sim_df.index:
        # try interpret as integer index
        if user_id.isdigit():
            idx = int(user_id)
            if idx < len(sim_df):
                user_id = sim_df.index[idx]
            else:
                return []
        else:
            return []

    scores = sim_df[user_id].sort_values(ascending=False)
    scores = scores[scores.index != user_id]
    return scores.head(top_k).index.tolist()
