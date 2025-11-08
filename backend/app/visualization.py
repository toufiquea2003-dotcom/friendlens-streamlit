import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os

CHART_DIR = os.path.join(os.path.dirname(__file__), "charts")
os.makedirs(CHART_DIR, exist_ok=True)

def create_visualizations(df):
    # Simple visualization: top users count or numeric histogram fallback
    if 'User' in df.columns:
        plt.figure(figsize=(10,6))
        sns.countplot(data=df, x='User', order=df['User'].value_counts().index)
        plt.xticks(rotation=90)
        path = os.path.join(CHART_DIR, "user_count.png")
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return path
    else:
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        if not num_cols:
            return None
        col = num_cols[0]
        # Sanitize column name for filename
        safe_col_name = "".join(c for c in col if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_col_name = safe_col_name.replace(' ', '_').replace('-', '_')
        path = os.path.join(CHART_DIR, f"{safe_col_name}_hist.png")
        plt.figure(figsize=(8,5))
        sns.histplot(df[col].dropna(), bins=30)
        plt.tight_layout()
        plt.savefig(path)
        plt.close()
        return path
