# Content Generation Engine

This repository contains a small pipeline that generates SEO-optimized blog posts using trending keywords and a language model, then renders them into complete HTML files using a reusable template.

Full technical documentation is included in `DOCUMENTATION_FULL.md` (recommended reading for maintainers).

Quick start
-----------

1. Create and activate a Python virtual environment.

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Provide your Groq API key in `.env`:

```text
GROQ_API_KEY=your_key_here
```

4. Optionally edit `company_config.json` with the target company metadata.

5. Run the pipeline:

```bash
python main.py
```

What the pipeline does
----------------------
- Fetches trending keywords using `pytrends` (`trends_fetcher.py`), with a built-in fallback list.
- Produces a short trend analysis via `trend_analyzer.py` (LLM-driven).
- Generates a full SEO blog via `blog_generator.py` using the prompts in `prompts.py` and the LLM (`groq_client.py`).
- Converts model output (Markdown) to HTML, injects it into `templates/blog_template.html`, and writes the file to `generated_blogs/`.

Important files
---------------
- `main.py` — orchestrator that runs the end-to-end flow.
- `trends_fetcher.py` — collects trending queries from Google Trends.
- `trend_analyzer.py` — analyzes keywords using the LLM.
- `blog_generator.py` — builds prompts, converts content to HTML, and writes the output.
- `groq_client.py` — Groq API wrapper (reads `GROQ_API_KEY` from `.env`).
- `prompts.py` — system prompts used to steer the model.
- `templates/blog_template.html` — HTML shell with `{{BLOG_CONTENT}}` placeholder.
- `DOCUMENTATION_FULL.md` — in-depth technical documentation for this project.

Folder Structure

📦Content_Generation_Engine
 ┣ 📂.git
 ┃ ┣ 📂hooks
 ┃ ┃ ┣ 📜applypatch-msg.sample
 ┃ ┃ ┣ 📜commit-msg.sample
 ┃ ┃ ┣ 📜fsmonitor-watchman.sample
 ┃ ┃ ┣ 📜post-update.sample
 ┃ ┃ ┣ 📜pre-applypatch.sample
 ┃ ┃ ┣ 📜pre-commit.sample
 ┃ ┃ ┣ 📜pre-merge-commit.sample
 ┃ ┃ ┣ 📜pre-push.sample
 ┃ ┃ ┣ 📜pre-rebase.sample
 ┃ ┃ ┣ 📜pre-receive.sample
 ┃ ┃ ┣ 📜prepare-commit-msg.sample
 ┃ ┃ ┣ 📜push-to-checkout.sample
 ┃ ┃ ┣ 📜sendemail-validate.sample
 ┃ ┃ ┗ 📜update.sample
 ┃ ┣ 📂info
 ┃ ┃ ┗ 📜exclude
 ┃ ┣ 📂logs
 ┃ ┃ ┣ 📂refs
 ┃ ┃ ┃ ┣ 📂heads
 ┃ ┃ ┃ ┃ ┗ 📜main
 ┃ ┃ ┃ ┗ 📂remotes
 ┃ ┃ ┃ ┃ ┗ 📂origin
 ┃ ┃ ┃ ┃ ┃ ┗ 📜main
 ┃ ┃ ┗ 📜HEAD
 ┃ ┣ 📂objects
 ┃ ┃ ┣ 📂02
 ┃ ┃ ┃ ┗ 📜55fd7ca335b1ad4f2a7b8efdc939eb0fb98383
 ┃ ┃ ┣ 📂0a
 ┃ ┃ ┃ ┗ 📜cf81301c906ea806cc2db4f626eea4f985ce78
 ┃ ┃ ┣ 📂0d
 ┃ ┃ ┃ ┗ 📜c9a819622a66e09f76dbe8133b9e148f999044
 ┃ ┃ ┣ 📂13
 ┃ ┃ ┃ ┣ 📜9ed4acff63a92b18010477ffa7961d00d085b7
 ┃ ┃ ┃ ┗ 📜d2320eea3e379c8c6708297eebb6d8ee5c48e2
 ┃ ┃ ┣ 📂17
 ┃ ┃ ┃ ┗ 📜b991f11bfbfe7aefbab568a9b626789610b89b
 ┃ ┃ ┣ 📂43
 ┃ ┃ ┃ ┗ 📜246d3fb2dc6232fde293541af7cb0732fb847a
 ┃ ┃ ┣ 📂44
 ┃ ┃ ┃ ┗ 📜b3e1ba588fb3ab52d9d9bb76a11a92f7f6dcb0
 ┃ ┃ ┣ 📂56
 ┃ ┃ ┃ ┗ 📜8c71b13b8ac26f8ef1d485ed55b5c117063ec0
 ┃ ┃ ┣ 📂58
 ┃ ┃ ┃ ┗ 📜dd995b100930520edc3d5f3cdc317da3402986
 ┃ ┃ ┣ 📂5c
 ┃ ┃ ┃ ┗ 📜b39377c8a69d92237c7896b03356dba286071a
 ┃ ┃ ┣ 📂5e
 ┃ ┃ ┃ ┗ 📜a5b47a1167481f245645fe87943d6f1429596b
 ┃ ┃ ┣ 📂6a
 ┃ ┃ ┃ ┗ 📜f6d4ca9818275e26db197365484bf54433a654
 ┃ ┃ ┣ 📂89
 ┃ ┃ ┃ ┗ 📜97e6ed3079331441b29fb1e4f01555db59d693
 ┃ ┃ ┣ 📂8f
 ┃ ┃ ┃ ┗ 📜ca58398805048ad7cd3147eb35b17d9d6bc08f
 ┃ ┃ ┣ 📂93
 ┃ ┃ ┃ ┗ 📜30a470132886ac675267b3d4b833f6417ca308
 ┃ ┃ ┣ 📂94
 ┃ ┃ ┃ ┗ 📜3f0aa066a6523e6b5ee78b40b4c17aa6404c59
 ┃ ┃ ┣ 📂96
 ┃ ┃ ┃ ┗ 📜4970066d40f91062f6c0c5fa05a3d166dcdf06
 ┃ ┃ ┣ 📂9d
 ┃ ┃ ┃ ┗ 📜cff37e0fb7e0df449b7a3112384797f954f729
 ┃ ┃ ┣ 📂9f
 ┃ ┃ ┃ ┗ 📜61032ed7938200f6e1a44c8c11ee535bdc4b9a
 ┃ ┃ ┣ 📂af
 ┃ ┃ ┃ ┗ 📜15c1d12ea1f739aa81a233e37a6d0d2927798f
 ┃ ┃ ┣ 📂b2
 ┃ ┃ ┃ ┗ 📜bf4e63ae08f62ecb0870d7930e452dfc480bdf
 ┃ ┃ ┣ 📂b5
 ┃ ┃ ┃ ┗ 📜525fcdacbfb6f3133c23ac015449818a2d9872
 ┃ ┃ ┣ 📂b9
 ┃ ┃ ┃ ┗ 📜4d9fe14dadcb56a9cc329e16e8926a0371b2f2
 ┃ ┃ ┣ 📂c3
 ┃ ┃ ┃ ┗ 📜d2a4ed704f16c1596d8b8015051f5bdf49fde6
 ┃ ┃ ┣ 📂ca
 ┃ ┃ ┃ ┗ 📜0553eac86ba8652f740620475c4a84ab610058
 ┃ ┃ ┣ 📂cf
 ┃ ┃ ┃ ┗ 📜43947d3472893037220330648a14e736da2e30
 ┃ ┃ ┣ 📂d7
 ┃ ┃ ┃ ┗ 📜2aa9499d7907a6a9a242f82c785580a4a9d398
 ┃ ┃ ┣ 📂dc
 ┃ ┃ ┃ ┗ 📜c33286fe94077c732950e12c96e16c89014a0b
 ┃ ┃ ┣ 📂de
 ┃ ┃ ┃ ┗ 📜af1c9b03b6f6cbd7b67e5aef184752f92e3d8b
 ┃ ┃ ┣ 📂e9
 ┃ ┃ ┃ ┗ 📜86bfb49cba8f7bea7f363f29b7a70d4b1a4970
 ┃ ┃ ┣ 📂ea
 ┃ ┃ ┃ ┗ 📜b1c3bafcfa830fa2a119cb02673e56eed98597
 ┃ ┃ ┣ 📂f8
 ┃ ┃ ┃ ┗ 📜92d0eb318fd37ee59a31ad71ee887651d8162c
 ┃ ┃ ┣ 📂f9
 ┃ ┃ ┃ ┗ 📜031ca9fce0c4bd3955fb6af0ae99486ca0dae5
 ┃ ┃ ┣ 📂fe
 ┃ ┃ ┃ ┗ 📜d1d703dc8f7331f38fa49c61c6621bbc1537c4
 ┃ ┃ ┣ 📂ff
 ┃ ┃ ┃ ┗ 📜60de15d9b4ba8d3b2e4f7d5b4516b405fca99a
 ┃ ┃ ┣ 📂info
 ┃ ┃ ┗ 📂pack
 ┃ ┣ 📂refs
 ┃ ┃ ┣ 📂heads
 ┃ ┃ ┃ ┗ 📜main
 ┃ ┃ ┣ 📂remotes
 ┃ ┃ ┃ ┗ 📂origin
 ┃ ┃ ┃ ┃ ┗ 📜main
 ┃ ┃ ┗ 📂tags
 ┃ ┣ 📜COMMIT_EDITMSG
 ┃ ┣ 📜config
 ┃ ┣ 📜description
 ┃ ┣ 📜HEAD
 ┃ ┗ 📜index
 ┣ 📂generated_blogs
 ┃ ┣ 📜netflix_blog_20260313_094001.html
 ┃ ┣ 📜nike_blog_20260310_131908.html
 ┃ ┣ 📜reticulo_blog.html
 ┃ ┣ 📜reticulo_sports_blog_20260310_131617.html
 ┃ ┣ 📜reticulo_sports_blog_20260310_131635.html
 ┃ ┗ 📜reticulo_trending_blog.txt
 ┣ 📂templates
 ┃ ┗ 📜blog_template.html
 ┣ 📂__pycache__
 ┃ ┣ 📜blog_generator.cpython-311.pyc
 ┃ ┣ 📜groq_client.cpython-311.pyc
 ┃ ┣ 📜main.cpython-311.pyc
 ┃ ┣ 📜prompts.cpython-311.pyc
 ┃ ┣ 📜trends_fetcher.cpython-311.pyc
 ┃ ┗ 📜trend_analyzer.cpython-311.pyc
 ┣ 📜.env
 ┣ 📜.gitignore
 ┣ 📜blog_generator.py
 ┣ 📜company_config.json
 ┣ 📜DOCUMENTATION.md
 ┣ 📜DOCUMENTATION_FULL.md
 ┣ 📜groq_client.py
 ┣ 📜main.py
 ┣ 📜prompts.py
 ┣ 📜README.md
 ┣ 📜requirements.txt
 ┣ 📜testcases.txt
 ┣ 📜trends_fetcher.py
 ┗ 📜trend_analyzer.py

Notes & caveats
--------------
- Ensure `.env` contains a valid `GROQ_API_KEY` when you want live model responses. If the key is missing or invalid, the system falls back to a built-in placeholder blog.
- Google Trends (`pytrends`) may rate-limit requests. The code handles this by returning fallback keywords; consider adding retry/backoff for production use.
- Generated HTML files are saved to `generated_blogs/` with filenames like `netflix_blog_20260313_094001.html`.

Next steps (recommended)
------------------------
- Read `DOCUMENTATION_FULL.md` for detailed architecture, prompts, failure modes, and suggested improvements.
- I can add an audit index (`generated_blogs/index.json`), stricter prompt contracts (YAML frontmatter), unit tests, or sanitization for model output — tell me which to prioritize.

