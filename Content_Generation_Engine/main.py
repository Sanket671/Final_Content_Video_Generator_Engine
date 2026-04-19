import json
import os

from trends_fetcher import get_trending_keywords
from trend_analyzer import analyze_trends
from blog_generator import generate_blog

CONFIG_PATH = "company_config.json"


def load_company_config(path=CONFIG_PATH):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Company config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():

    print("Fetching Google Trends data...")

    keywords = get_trending_keywords()

    print("\nTrending Keywords:")
    print(keywords)

    company_info = load_company_config()

    print("\nAnalyzing trends using AI...\n")
    analysis = analyze_trends(keywords, company_info)
    print(analysis)

    print("\nGenerating SEO Blog...\n")
    blog_path = generate_blog(keywords, company_info)
    print("Blog saved at:", blog_path)


if __name__ == "__main__":
    main()