import os
import json
import re
import html

from dotenv import load_dotenv
from supabase import create_client
from google import genai
from google.genai import types


load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

gemini = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


def clean_summary(summary):
    summary = html.unescape(summary or "")
    return re.sub("<[^>]+>", "", summary)


def already_used(article_id):
    response = (
        supabase.table("quiz_questions")
        .select("id")
        .eq("article_id", article_id)
        .limit(1)
        .execute()
    )

    return len(response.data) > 0


def make_question(article):
    summary = clean_summary(article["summary"])

    prompt = f"""
You are creating a practice question for high school UIL Current Events.

Decide if this article is useful enough for a current events quiz.

Good articles involve important:
- government or politics
- international events
- economics or business
- science or technology
- major Texas news
- major national news

Skip articles that are mostly entertainment, lifestyle, sports,
random facts, advice, or do not contain enough information.

Only use information supported by the title and summary below.

Title: {article["title"]}
Source: {article["source"]}
Summary: {summary}

If the article should be skipped, return:
{{
    "use": false
}}

If it is useful, return:
{{
    "use": true,
    "question": "question here",
    "choice_a": "answer",
    "choice_b": "answer",
    "choice_c": "answer",
    "choice_d": "answer",
    "correct_answer": "A"
}}

Make one clear factual multiple-choice question.
Make the wrong answers believable.
Do not ask which news source reported the story.
Do not make a question if the title and summary do not clearly support the answer.
"""

    response = gemini.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.2
        )
    )

    return json.loads(response.text)


def main():
    response = (
        supabase.table("articles")
        .select("id,title,link,source,summary")
        .order("date_added", desc=True)
        .limit(20)
        .execute()
    )

    articles = response.data

    added = 0

    for article in articles:

        if added >= 5:
            break

        if already_used(article["id"]):
            continue

        try:
            result = make_question(article)

            if not result.get("use"):
                print("Skipped:", article["title"])
                continue

            if result.get("correct_answer") not in ["A", "B", "C", "D"]:
                print("Bad question:", article["title"])
                continue

            question_data = {
                "question": result["question"],
                "choice_a": result["choice_a"],
                "choice_b": result["choice_b"],
                "choice_c": result["choice_c"],
                "choice_d": result["choice_d"],
                "correct_answer": result["correct_answer"],
                "source_link": article["link"],
                "article_id": article["id"]
            }

            supabase.table("quiz_questions").insert(question_data).execute()

            print("Added:", result["question"])
            added += 1

        except Exception as error:
            print("Error:", article["title"])
            print(error)

    print(f"Added {added} questions")


if __name__ == "__main__":
    main()