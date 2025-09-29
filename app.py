import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import requests
from markdown import markdown
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

# Enhanced CSS with colors, animations, and styles
st.markdown("""
<style>
body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
.fade-in {
  animation: fadeIn 1.5s ease forwards;
  opacity: 0;
}
@keyframes fadeIn {
  to {
    opacity: 1;
  }
}
.slide-in-left {
  animation: slideInLeft 1s ease forwards;
  opacity: 0;
}
@keyframes slideInLeft {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
.slide-in-right {
  animation: slideInRight 1s ease forwards;
  opacity: 0;
}
@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
.button-glow {
  background-color: #ff6b6b !important;
  color: white !important;
  border: none;
  padding: 10px 20px;
  border-radius: 5px;
  transition: all 0.3s ease;
}
.button-glow:hover {
  background-color: #ff5252 !important;
  box-shadow: 0 0 20px 4px #ff6b6b;
  transform: scale(1.05);
}
.streamlit-expanderHeader {
  background-color: #4ecdc4 !important;
  color: white !important;
  border-radius: 5px;
  padding: 10px;
  transition: all 0.3s ease;
}
.streamlit-expanderHeader:hover {
  background-color: #45b7aa !important;
  color: #fff !important;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}
.tab-content {
  background-color: rgba(255,255,255,0.1);
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 20px;
}
.career-card {
  background-color: rgba(255,255,255,0.9);
  color: black;
  padding: 15px;
  border-radius: 10px;
  margin-bottom: 20px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  transition: transform 0.3s ease;
}
.career-card:hover {
  transform: translateY(-5px);
}
.skill-match-green {
  background-color: #4caf50 !important;
}
.skill-match-red {
  background-color: #f44336 !important;
}
h1, h2, h3 {
  color: #ffeb3b !important;
}
.stRadio label, .stSelectbox label, .stMultiselect label {
  color: white !important;
}
.stButton button {
  background-color: #ff6b6b !important;
  color: white !important;
}
</style>
""", unsafe_allow_html=True)

# --- Load datasets ---
df = pd.read_csv("occupations_genz.csv")

# --- Load or initialize roadmap JSON ---
json_file = "roadmaps.json"
try:
    with open(json_file, "r") as f:
        roadmap_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    roadmap_data = {}

# --- Streamlit page setup ---
st.set_page_config(page_title="Career Guidance", layout="wide")
st.title("🚀 Career Recommendation Engine")
st.write("Answer a few questions and get your personalized career recommendation and roadmap!")

# Initialize session state for results
if 'results' not in st.session_state:
    st.session_state.results = []

# --- Recommendation function ---
def recommend_top_careers(skills, interests, personality, work_style, domains, top_n=3):
    skills = [s.lower() for s in skills]
    interests = [i.lower() for i in interests]
    personality = personality.lower()
    work_style = work_style.lower()
    domains = [d.lower() for d in domains]
    scored_careers = []
    for _, row in df.iterrows():
        row_skills = [s.strip().lower() for s in str(row['Required_Skills']).split(";")]
        row_interests = [row['Domain'].strip().lower()]
        row_personality = row['Personality_Fit'].strip().lower()
        row_work_style = row['Work_Style'].strip().lower()
        row_domain = row['Domain'].strip().lower()
        skill_matches = [skill for skill in skills if skill in row_skills]
        interest_match = any(interest in row_interests for interest in interests)
        personality_match = (personality == row_personality)
        work_style_match = (work_style == row_work_style)
        domain_match = row_domain in domains
        score = len(skill_matches) + interest_match + personality_match + work_style_match + domain_match
        if score > 0:
            scored_careers.append({
                'Occupation': row['Occupation'],
                'Industry': row['Industry'],
                'Domain': row['Domain'],
                'Average_Salary_Range': row['Average_Salary_Range'],
                'Required_Education': row['Required_Education'],
                'Required_Skills': row['Required_Skills'],
                'Skill_Matches': skill_matches,
                'Score': score
            })
    top_careers = sorted(scored_careers, key=lambda x: x['Score'], reverse=True)[:top_n]
    return top_careers

# --- Fetch roadmap ---
def fetch_and_store_roadmap(career_name, api_key="7ad04449399e91028e0a5e8a5d8add84ea6dda116528ca5bb5530154b4810128"):
    if career_name in roadmap_data:
        return roadmap_data[career_name]
    roadmap_items = []
    mapping = {
        "Software Engineer": "frontend",
        "Data Scientist": "data-science",
        "UI/UX Designer": "frontend",
        "Content Writer": "content",
        "Graphic Designer": "frontend",
        "Animator": "frontend",
        "Product Manager": "product-management",
        "Business Analyst": "data-science"
    }
    key = mapping.get(career_name)
    if key:
        try:
            url = f"https://raw.githubusercontent.com/kamranahmedse/developer-roadmap/main/roadmaps/{key}.md"
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            html = markdown(r.text)
            soup = BeautifulSoup(html, "html.parser")
            roadmap_items = [h.get_text() for h in soup.find_all(["h1","h2","h3","li"])]
        except:
            pass
    if not roadmap_items:
        try:
            params = {
                "engine": "google",
                "q": f"{career_name} career roadmap",
                "api_key": api_key,
                "num": 3
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            for res in results.get("organic_results", []):
                if "link" in res:
                    roadmap_items.append(res["link"])
        except:
            roadmap_items = ["Roadmap fetch failed."]
    roadmap_data[career_name] = roadmap_items
    with open(json_file, "w") as f:
        json.dump(roadmap_data, f, indent=4)
    return roadmap_items

# --- Tabs for interactive UI ---
tab1, tab2 = st.tabs(["📝 About You", "🏆 Recommendations"])

with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.header("Step 1: About You")
    personality = st.radio("Choose your personality type:", ["Analytical", "Creative", "Social", "Technical"])
    work_style = st.radio("Preferred work style:", ["Remote", "Onsite", "Hybrid"])
    domain_filter = st.multiselect("Interested domains:", ["Tech", "Non-Tech", "Creative"], default=["Tech","Non-Tech","Creative"])
    skill_choices = ["Python", "Excel", "Photoshop", "Writing", "Leadership", "Java", "SQL", "Figma", "After Effects"]
    selected_skills = st.multiselect("Select the skills you enjoy using:", skill_choices)
    interests_choices = ["Technology", "Creative Arts", "Business/Finance", "Design", "Media", "Engineering", "Health", "Marketing"]
    selected_interests = st.multiselect("Choose your interests:", interests_choices)
    if st.button("Get My Career Recommendations", key="recommend-btn", help="Click to generate recommendations"):
        if not selected_skills and not selected_interests:
            st.warning("Please select at least some skills or interests.")
        else:
            results = recommend_top_careers(selected_skills, selected_interests, personality, work_style, domain_filter)
            st.session_state.results = results
            st.success("Recommendations generated! Switch to the Recommendations tab.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    results = st.session_state.results
    if results:
        st.markdown('<div class="fade-in">### 🏆 Top Career Matches:</div>', unsafe_allow_html=True)
        for i, career in enumerate(results):
            animation_class = "slide-in-left" if i % 2 == 0 else "slide-in-right"
            st.markdown(f'<div class="career-card {animation_class}">', unsafe_allow_html=True)
            col1, col2 = st.columns([2,3])
            with col1:
                st.markdown(f'<div class="fade-in"><h3>{career["Occupation"]} ({career["Domain"]})</h3></div>', unsafe_allow_html=True)
                st.write(f"**Industry:** {career['Industry']}")
                st.write(f"**Average Salary:** {career['Average_Salary_Range']}")
                st.write(f"**Required Education:** {career['Required_Education']}")
                st.write(f"**Skill Matches:** {', '.join(career['Skill_Matches'])}")
            with col2:
                all_skills = [s.strip() for s in career['Required_Skills'].split(";")]
                matches = [1 if s.lower() in [sk.lower() for sk in selected_skills] else 0 for s in all_skills]
                fig = go.Figure(go.Bar(
                    x=all_skills,
                    y=matches,
                    marker_color=['green' if m==1 else 'red' for m in matches]
                ))
                fig.update_layout(title="Skill Match", yaxis=dict(title="Match", tickvals=[0,1], ticktext=["No","Yes"]))
                st.plotly_chart(fig, use_container_width=True)
            roadmap_items = fetch_and_store_roadmap(career['Occupation'])
            with st.expander(f"Learning Roadmap for {career['Occupation']}"):
                for item in roadmap_items[:5]:
                    st.write(f"- {item}")
                if len(roadmap_items) > 5:
                    st.info(f"...and {len(roadmap_items)-5} more steps. Click above to view all.")
            st.markdown("---")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No recommendations yet. Go to the 'About You' tab and generate some!")
    st.markdown('</div>', unsafe_allow_html=True)


