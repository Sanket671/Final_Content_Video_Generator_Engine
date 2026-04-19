import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def ask_groq(system_prompt, user_prompt):
    try:
        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],

            temperature=0.7,
            timeout=60
        )

        return response.choices[0].message.content

    except KeyboardInterrupt:
        print("Warning: GROQ request interrupted by user. Using fallback content.")
        return "<p>This is fallback content because the language model request was interrupted.</p>"
    except Exception as e:
        print(f"Warning: GROQ request failed ({e}). Using fallback text.")
        return (
            "# Fallback Blog Content\n"
            "The model API is currently unavailable. This placeholder content is generated locally as a fallback.\n\n"
            "## Why this trend matters\n"
            "Use trending keywords to engage your audience and guide actionable training and recovery practices.\n\n"
            "## Athlete performance insights\n"
            "Focus on sports science and structured programs.\n\n"
            "## How the company connects\n"
            f"Describe how the company services tie into the keywords in a practical way.\n\n"
            "## Actionable tips\n"
            "Give a quick list of steps readers can follow today.\n\n"
            "## Conclusion\n"
            "Wrap up with a call-to-action that encourages readers to learn more."
        )