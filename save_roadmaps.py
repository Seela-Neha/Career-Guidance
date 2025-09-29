import json
import requests
from markdown import markdown
from bs4 import BeautifulSoup
from serpapi import GoogleSearch

# List of careers to fetch roadmaps for
careers = ["Software Engineer", "Data Scientist", "UI/UX Designer", "Content Writer", "Graphic Designer"]

def fetch_roadmap(career_name):
    # Try GitHub first
    mapping = {
        "Software Engineer": "frontend",
        "Data Scientist": "data-science",
        "UI/UX Designer": "frontend",
        "Content Writer": "content",
        "Graphic Designer": "frontend"
    }
    key = mapping.get(career_name, None)
    
    if key:
        raw_url = f"https://raw.githubusercontent.com/kamranahmedse/developer-roadmap/main/roadmaps/{key}.md"
        try:
            r = requests.get(raw_url, timeout=5)
            r.raise_for_status()
            html = markdown(r.text)
            soup = BeautifulSoup(html, "html.parser")
            items = [h.get_text() for h in soup.find_all(["h1","h2","h3","li"])]
            if items:
                return items[:20]
        except:
            pass

    # Fallback: SerpAPI
    try:
        api_key = "7ad04449399e91028e0a5e8a5d8add84ea6dda116528ca5bb5530154b4810128"
        params = {
            "engine": "google",
            "q": f"{career_name} career roadmap",
            "api_key": api_key,
            "num": 3
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        roadmap_links = []
        if "organic_results" in results:
            for res in results["organic_results"]:
                if "link" in res:
                    roadmap_links.append(res["link"])
        return roadmap_links if roadmap_links else ["No roadmap found online."]
    except:
        return ["Roadmap fetch failed."]

# Load existing roadmaps
try:
    with open("roadmaps.json", "r") as f:
        roadmap_data = json.load(f)
except FileNotFoundError:
    roadmap_data = {}

# Fetch and save
for career in careers:
    roadmap_data[career] = fetch_roadmap(career)

with open("roadmaps.json", "w") as f:
    json.dump(roadmap_data, f, indent=4)

print("Roadmaps saved successfully!")
