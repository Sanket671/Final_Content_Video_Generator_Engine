import os
from markdown import markdown
from groq_client import ask_groq
from prompts import BLOG_GENERATION_SYSTEM_PROMPT

OUTPUT_DIR = "generated_blogs"


def _slugify(value):
    return ''.join(c.lower() if c.isalnum() else '_' for c in value).strip('_')


def generate_blog(keywords, company_info):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    company_name = company_info.get("company_name", "Company")
    industry = company_info.get("industry", "General")
    target_audience = company_info.get("target_audience", "audience")
    services = company_info.get("services", "services")

    keyword_text = ", ".join(keywords)

    user_prompt = f"""
Write a blog for {company_name}.

Industry:
{industry}

Target audience:
{target_audience}

Services:
{services}

Use trending keywords:
{keyword_text}

Write a full SEO optimized blog for {company_name}.
Use proper headings and paragraphs.
"""

    blog = ask_groq(
        BLOG_GENERATION_SYSTEM_PROMPT,
        user_prompt
    )

    # Convert markdown content to HTML if needed
    try:
        blog_html = markdown(blog)
    except Exception:
        blog_html = blog.replace("**", "<b>").replace("\n", "<br>")

    # Load template
    with open("templates/blog_template.html", "r", encoding="utf-8") as f:
        template = f.read()

    final_html = template.replace("{{BLOG_CONTENT}}", blog_html)

    timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
    slug = _slugify(company_name)
    filename = f"{slug}_blog_{timestamp}.html"
    path = os.path.join(OUTPUT_DIR, filename)

    with open(path, "w", encoding="utf-8") as f:
        f.write(final_html)

    return path