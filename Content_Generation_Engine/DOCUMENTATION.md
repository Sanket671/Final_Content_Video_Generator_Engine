# Content Generation Engine — Documentation

**Project Overview:**
- **Purpose:** Generate SEO-optimized blogs using trending keywords and a language model, convert them to HTML using a reusable template, and save timestamped outputs to `generated_blogs/`.
- **Key capabilities:** Fetch trends, analyze them with prompts, produce blog text via a language model API, convert to HTML, and persist results.

**Repository Layout (important files):**
- **`main.py`**: [main.py](main.py#L1) — Orchestrates the full pipeline: fetch trends, analyze, generate blog.
- **`trends_fetcher.py`**: [trends_fetcher.py](trends_fetcher.py#L1) — Uses `pytrends` to collect trending queries; falls back to built-in keywords when unavailable.
- **`trend_analyzer.py`**: [trend_analyzer.py](trend_analyzer.py#L1) — Wraps the analysis prompt and sends keywords + optional company info to the model via `groq_client.ask_groq`.
- **`blog_generator.py`**: [blog_generator.py](blog_generator.py#L1) — Builds the blog prompt, requests the model, converts markdown to HTML, injects into the template, and writes the file into `generated_blogs/`.
- **`groq_client.py`**: [groq_client.py](groq_client.py#L1) — Minimal client wrapper for the Groq API; reads `GROQ_API_KEY` from `.env` and provides `ask_groq(system_prompt, user_prompt)`.
- **`prompts.py`**: [prompts.py](prompts.py#L1) — Contains the system prompts used for trend analysis and blog generation.
- **`company_config.json`**: [company_config.json](company_config.json#L1) — Company metadata used when generating targeted blogs.
- **`templates/blog_template.html`**: [templates/blog_template.html](templates/blog_template.html#L1) — HTML shell; `{{BLOG_CONTENT}}` is replaced by generated HTML.
- **`requirements.txt`**: [requirements.txt](requirements.txt#L1) — Python dependencies.

Pipeline / Full Data Flow:
1. Run `main.py` ([main.py](main.py#L1)).
2. `trends_fetcher.get_trending_keywords()` obtains trending queries via Google Trends (`pytrends`). If Google Trends fails or rate-limits, a fallback set of keywords is returned.
3. `trend_analyzer.analyze_trends(keywords, company_info)` calls `groq_client.ask_groq` with `TREND_ANALYSIS_SYSTEM_PROMPT` (from `prompts.py`) to get a short analysis and content opportunities.
4. `blog_generator.generate_blog(keywords, company_info)` builds a user prompt including company metadata and the top keywords, then calls `groq_client.ask_groq` with `BLOG_GENERATION_SYSTEM_PROMPT` to obtain the blog text.
5. If the returned content is Markdown, it is converted to HTML with the `markdown` package. If conversion fails, a simple fallback replacement is used.
6. The HTML is injected into `templates/blog_template.html` replacing `{{BLOG_CONTENT}}` and saved under `generated_blogs/` using the naming pattern: `{slug}_blog_{YYYYMMDD_HHMMSS}.html`.

Inputs and Configuration:
- `.env` — must contain `GROQ_API_KEY` for the Groq client to call the model.
- `company_config.json` — supplies `company_name`, `industry`, `target_audience`, and `services`.
- `requirements.txt` — install dependencies via `pip install -r requirements.txt`.

Outputs and Formats:
- Primary outputs: HTML blog files in `generated_blogs/` (e.g., `netflix_blog_20260313_094001.html`). These are full HTML documents created from the template.
- Secondary output: plain text fallback files (e.g., `reticulo_trending_blog.txt`) — produced if the project or user saved raw text instead of HTML.
- Filenames include company slug and timestamp. The HTML contains an embedded footer `Powered by Reticulo Sports AI Content Engine` from the template.

Sample outputs (observed):
- [generated_blogs/netflix_blog_20260313_094001.html](generated_blogs/netflix_blog_20260313_094001.html#L1): Full HTML blog using keywords about streaming and athlete training (example of company-specific content).
- [generated_blogs/nike_blog_20260310_131908.html](generated_blogs/nike_blog_20260310_131908.html#L1): Another company-specific HTML blog (sports apparel context).
- [generated_blogs/reticulo_blog.html](generated_blogs/reticulo_blog.html#L1): General blog for the Reticulo brand.
- [generated_blogs/reticulo_trending_blog.txt](generated_blogs/reticulo_trending_blog.txt#L1): Plain-text blog content that demonstrates the raw text output before templating.

How the model integration works (behavioral notes):
- `groq_client.ask_groq` sends a two-message chat (system + user) and returns the model's content. If the API call fails it returns static fallback markup/text so the pipeline still produces an output file.
- The model used in the wrapper is configured as `llama-3.3-70b-versatile` with `temperature=0.7`.

Failure modes and fallbacks:
- Google Trends may return a 429 TooManyRequests error — `trends_fetcher` catches this and uses a static fallback keyword list.
- Groq API network or key errors are caught in `groq_client.py`, which returns a built-in fallback blog text so that `blog_generator` can still write a file.

How to run (quick start):
1. Create and activate a Python virtual environment.
2. Install deps: `pip install -r requirements.txt`.
3. Add your Groq key to `.env`: `GROQ_API_KEY=your_key_here`.
4. Optionally edit `company_config.json` with target company info.
5. Run: `python main.py`.

Troubleshooting tips:
- If `pytrends` fails due to network or rate limits, the script logs a warning and uses fallback keywords — no crash.
- If you get empty or placeholder blogs, check `.env` and confirm `GROQ_API_KEY` is set and valid.
- To inspect the raw generated text (before templating), open `generated_blogs/*.txt` files if present.

Conclusions & observations (derived):
- The pipeline is robust to API failures: both trend fetching and model calls have fallbacks so the user will receive content even when external services fail.
- Output quality depends heavily on the LLM response; the built-in fallback ensures continuity but is generic.
- The templating approach keeps presentation separate from content, enabling easy customization of look-and-feel via `templates/blog_template.html`.
- The project is ideal for rapid prototyping of content generation workflows but should add structured tests, logging, and more configurable prompts for production use.

Suggested next improvements:
- Add CLI flags to choose output format (HTML vs. plain text) and to supply company metadata via command-line.
- Store metadata about generated files (keywords used, prompt, model response) in a small JSON index to enable auditing.
- Add unit tests for `trends_fetcher` and `blog_generator` (mock the model and pytrends).

---
Generated by the Content Generation Engine — see `README.md` for quick start.
