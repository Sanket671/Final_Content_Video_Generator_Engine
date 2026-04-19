import json
from schemas.product import CinematographyProduct
from llm.groq_client import call_groq


def generate_script(product: CinematographyProduct, hook_duration: int):
    prompt = f"""
You are generating structured script CONTENT ONLY
for a faceless sports product explainer video.

DO NOT assign timings.
DO NOT mention seconds.
DO NOT estimate duration.

Your job is ONLY to produce clean, neutral, factual narration blocks.

VERY IMPORTANT NARRATIVE RULE:
- The HOOK and PROBLEM together must form
  ONE continuous, detailed narrative which should last till {hook_duration} seconds.
- This opening narration should feel complete on its own,
  setting up the concern clearly before any solution appears.
- Do NOT mention the product or brand in hook or problem.
- Do NOT welcome the viewer.
- Do NOT mention Reticulo.
- Start directly with the real-world concern or physical challenge.

PRODUCT DATA (FOR LATER SECTIONS ONLY):
Name: {product.name}
Brand: {product.brand}
Description: {product.description}
Reviews: {product.user_reviews}
Total Reviews Count: {product.reviews}

SCRIPT STRUCTURE (STRICT ORDER):

- hook:
  Emotional but neutral opening that introduces
  the everyday physical challenge or training concern faced by athletes, 
  gym-goers, or active individuals.
  This should be descriptive and situation-based.

- problem:
  Continue the same thought by clearly explaining
  why this challenge matters for performance, recovery, 
  endurance, form, or injury prevention.
  This MUST feel like a continuation of the hook,
  not a new idea.

- product_intro:
  MUST naturally follow the problem and
  logically start with a phrase like
  "To address this training need" or "To help with this challenge",
  then explain what the product is.
  This is the FIRST time the product is mentioned.

- social_proof:
  Mention that many athletes and active users have rated
  the product 4+ stars, based on review count,
  in a neutral and factual way.

- features:
  Exactly 4 extremely short factual keywords or phrases. 
  Example: "Moisture-wicking fabric", "Ergonomic grip", "Shock absorption".
  Do NOT include descriptions, sentences, or explanations.

- outro:
  Sponsorship disclosure for Reticulo.

STRICT RULES:
- No exaggeration
- No marketing hype
- No medical claims
- No prices or discounts
- Neutral Indian audience tone
- Short sentences
- Spoken English
- No greetings, no calls to action in hook/problem

OUTPUT FORMAT (JSON ONLY):
{{
  "hook": "...",
  "problem": "...",
  "product_intro": "...",
  "social_proof": "...",
  "features": ["...", "...", "...", "..."],
  "outro": "..."
}}
"""
    response_raw = call_groq(prompt)
    clean_json = response_raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean_json)
