import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF
import os

# Set page config
st.set_page_config(
    page_title="FriendLens",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: #ffffff;
    }
    .sidebar .sidebar-content {
        background-color: #1a1c23;
    }
    .stButton>button {
        background-color: #4f46e5;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #3730a3;
    }
    .card {
        background-color: #1a1c23;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #4f46e5;
    }
    h1, h2, h3 {
        color: #4f46e5;
    }
</style>
""", unsafe_allow_html=True)

# Load preloaded dataset
@st.cache_data
def load_data():
    # Use the friendlens data as preloaded dataset
    data_path = "friendlens_data.csv"
    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
    else:
        # Fallback to a sample dataset if file not found
        data = {
            'Spice_Tolerance': np.random.randint(1, 6, 100),
            'Sweet_Tooth_Level': np.random.randint(1, 6, 100),
            'Ethical_Shopping': np.random.randint(1, 6, 100),
            'Travel_Planning_Pref': np.random.randint(1, 6, 100),
            'Introversion_Extraversion': np.random.randint(1, 6, 100),
            'Risk_Taking': np.random.randint(1, 6, 100),
            'Conscientiousness': np.random.randint(1, 6, 100),
            'Open_to_New_Exp': np.random.randint(1, 6, 100),
            'Teamwork_Preference': np.random.randint(1, 6, 100),
            'Diet': np.random.choice(['Veg', 'Non-Veg'], 100),
            'Tea_vs_Coffee': np.random.choice(['Tea', 'Coffee', 'Both'], 100),
            'Hobby_Top1': np.random.choice(['Reading', 'Sports', 'Gaming', 'Coding', 'Traveling', 'Cooking'], 100),
            'Club_Top1': np.random.choice(['BookClub', 'SportsClub', 'GamingClub', 'CodingClub', 'TravelClub', 'CookingClub'], 100)
        }
        df = pd.DataFrame(data)
    return df

df = load_data()

# Title and description
st.title("🔍 FriendLens")
st.markdown("**Discover connections, insights, and personalized recommendations from your data.**")

# Sidebar
st.sidebar.header("🎯 Your Profile")

spice_tolerance = st.sidebar.slider("Spice Tolerance", 1, 5, 3)
sweet_tooth_level = st.sidebar.slider("Sweet Tooth Level", 1, 5, 3)
ethical_shopping = st.sidebar.slider("Ethical Shopping", 1, 5, 3)
travel_planning_pref = st.sidebar.slider("Travel Planning Preference", 1, 5, 3)
introversion_extraversion = st.sidebar.slider("Introversion-Extraversion", 1, 5, 3)
risk_taking = st.sidebar.slider("Risk Taking", 1, 5, 3)
conscientiousness = st.sidebar.slider("Conscientiousness", 1, 5, 3)
open_to_new_exp = st.sidebar.slider("Open to New Experiences", 1, 5, 3)
teamwork_preference = st.sidebar.slider("Teamwork Preference", 1, 5, 3)
diet = st.sidebar.selectbox("Diet", ['Veg', 'Non-Veg'])
tea_vs_coffee = st.sidebar.selectbox("Tea vs Coffee", ['Tea', 'Coffee', 'Both'])
hobby_top1 = st.sidebar.selectbox("Top Hobby", ['Reading', 'Sports', 'Gaming', 'Coding', 'Traveling', 'Cooking'])
club_top1 = st.sidebar.selectbox("Top Club", ['BookClub', 'SportsClub', 'GamingClub', 'CodingClub', 'TravelClub', 'CookingClub'])

analyze_button = st.sidebar.button("✨ Analyze My Profile")

# Main content
if analyze_button:
    user_profile = {
        'Spice_Tolerance': spice_tolerance,
        'Sweet_Tooth_Level': sweet_tooth_level,
        'Ethical_Shopping': ethical_shopping,
        'Travel_Planning_Pref': travel_planning_pref,
        'Introversion_Extraversion': introversion_extraversion,
        'Risk_Taking': risk_taking,
        'Conscientiousness': conscientiousness,
        'Open_to_New_Exp': open_to_new_exp,
        'Teamwork_Preference': teamwork_preference,
        'Diet': diet,
        'Tea_vs_Coffee': tea_vs_coffee,
        'Hobby_Top1': hobby_top1,
        'Club_Top1': club_top1
    }

    # Summary Card
    st.header("📊 Your Profile Summary")
    summary_cols = st.columns(2)
    with summary_cols[0]:
        st.markdown(f"""
        <div class="card">
            <h3>Attributes</h3>
            <p>Spice Tolerance: {spice_tolerance}/5</p>
            <p>Sweet Tooth Level: {sweet_tooth_level}/5</p>
            <p>Ethical Shopping: {ethical_shopping}/5</p>
            <p>Travel Planning Pref: {travel_planning_pref}/5</p>
            <p>Introversion-Extraversion: {introversion_extraversion}/5</p>
        </div>
        """, unsafe_allow_html=True)
    with summary_cols[1]:
        st.markdown(f"""
        <div class="card">
            <h3>Preferences</h3>
            <p>Diet: {diet}</p>
            <p>Tea vs Coffee: {tea_vs_coffee}</p>
            <p>Top Hobby: {hobby_top1}</p>
            <p>Top Club: {club_top1}</p>
        </div>
        """, unsafe_allow_html=True)

    # Recommendations
    st.header("🤝 Personalized Recommendations")

    # Prepare data for similarity calculation
    numeric_cols = ['Spice_Tolerance', 'Sweet_Tooth_Level', 'Ethical_Shopping', 'Travel_Planning_Pref', 'Introversion_Extraversion', 'Risk_Taking', 'Conscientiousness', 'Open_to_New_Exp', 'Teamwork_Preference']
    user_vector = np.array([user_profile[col] for col in numeric_cols]).reshape(1, -1)
    dataset_vectors = df[numeric_cols].values

    # Calculate cosine similarity
    similarities = cosine_similarity(user_vector, dataset_vectors)[0]

    # Get top 5 similar users
    top_indices = similarities.argsort()[-5:][::-1]
    recommendations = df.iloc[top_indices].copy()
    recommendations['similarity'] = similarities[top_indices]

    st.markdown("""
    <div class="card">
        <h3>Top 5 Similar Profiles</h3>
        <p>Based on your attributes, here are the most similar users in our dataset:</p>
    </div>
    """, unsafe_allow_html=True)

    for i, (_, row) in enumerate(recommendations.iterrows()):
        st.markdown(f"""
        <div class="card">
            <h4>#{i+1} - Profile {i+1}</h4>
            <p>Similarity: {row['similarity']:.2f}</p>
            <p>Diet: {row['Diet']}, Tea vs Coffee: {row['Tea_vs_Coffee']}, Hobby: {row['Hobby_Top1']}, Club: {row['Club_Top1']}</p>
        </div>
        """, unsafe_allow_html=True)

    # Data Preview
    st.header("📋 Data Preview")
    st.markdown("""
    <div class="card">
        <h3>First 10 Rows of Dataset</h3>
    </div>
    """, unsafe_allow_html=True)
    st.dataframe(df.head(10))

    # Visualizations
    st.header("📈 Visualizations")

    # Comparison Chart
    st.subheader("Your Profile vs Dataset Average")
    user_values = [user_profile[col] for col in numeric_cols]
    avg_values = df[numeric_cols].mean().values

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(numeric_cols))
    width = 0.35

    ax.bar(x - width/2, user_values, width, label='Your Profile', color='#4f46e5')
    ax.bar(x + width/2, avg_values, width, label='Dataset Average', color='#7c3aed')

    ax.set_xlabel('Attributes')
    ax.set_ylabel('Scores')
    ax.set_title('Profile Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels([col.replace('_', ' ') for col in numeric_cols])
    ax.legend()

    st.pyplot(fig)

    # Radar Chart
    st.subheader("Your Profile Radar")
    categories = numeric_cols
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))

    angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
    user_values_radar = user_values + user_values[:1]
    angles += angles[:1]

    ax.fill(angles, user_values_radar, 'o-', linewidth=2, label='Your Profile', color='#4f46e5')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([col.replace('_', ' ') for col in categories])
    ax.set_ylim(0, 5)
    ax.set_title('Your Profile Attributes')
    ax.grid(True)

    st.pyplot(fig)

    # Create Visualization Button
    if st.button("🎨 Create Additional Visualization"):
        st.subheader("Dataset Trends")
        fig = px.scatter(df, x='Spice_Tolerance', y='Sweet_Tooth_Level', color='Diet',
                        title='Spice Tolerance vs Sweet Tooth Level by Diet')
        st.plotly_chart(fig)

    # Download Report
    if st.button("📄 Download My Report"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, txt="FriendLens Profile Report", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Spice Tolerance: {spice_tolerance}", ln=True)
        pdf.cell(200, 10, txt=f"Sweet Tooth Level: {sweet_tooth_level}", ln=True)
        pdf.cell(200, 10, txt=f"Ethical Shopping: {ethical_shopping}", ln=True)
        pdf.cell(200, 10, txt=f"Travel Planning Pref: {travel_planning_pref}", ln=True)
        pdf.cell(200, 10, txt=f"Introversion-Extraversion: {introversion_extraversion}", ln=True)
        pdf.cell(200, 10, txt=f"Risk Taking: {risk_taking}", ln=True)
        pdf.cell(200, 10, txt=f"Conscientiousness: {conscientiousness}", ln=True)
        pdf.cell(200, 10, txt=f"Open to New Exp: {open_to_new_exp}", ln=True)
        pdf.cell(200, 10, txt=f"Teamwork Preference: {teamwork_preference}", ln=True)
        pdf.cell(200, 10, txt=f"Diet: {diet}", ln=True)
        pdf.cell(200, 10, txt=f"Tea vs Coffee: {tea_vs_coffee}", ln=True)
        pdf.cell(200, 10, txt=f"Top Hobby: {hobby_top1}", ln=True)
        pdf.cell(200, 10, txt=f"Top Club: {club_top1}", ln=True)

        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(
            label="Download PDF",
            data=pdf_output,
            file_name="friendlens_report.pdf",
            mime="application/pdf"
        )

else:
    st.info("👈 Use the sidebar to input your profile and click 'Analyze My Profile' to get started!")

# Footer
st.markdown("---")
st.markdown("Made with ❤ using Streamlit | FriendLens © 2025")
