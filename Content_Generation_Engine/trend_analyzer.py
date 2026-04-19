from groq_client import ask_groq
from prompts import TREND_ANALYSIS_SYSTEM_PROMPT


def analyze_trends(keywords, company_info=None):

    keyword_text = ", ".join(keywords)
    company_section = ""

    if company_info:
        company_section = f"\nCompany: {company_info.get('company_name', 'Unknown')}\nIndustry: {company_info.get('industry', 'N/A')}\n"

    user_prompt = f"""
These are trending sports keywords from Google Trends:{company_section}

{keyword_text}

Analyze them and identify the best content opportunities.
"""

    result = ask_groq(
        TREND_ANALYSIS_SYSTEM_PROMPT,
        user_prompt
    )

    return result