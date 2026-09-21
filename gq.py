import os
import json
import re
import html
import time

from dotenv import load_dotenv
from supabase import create_client
from google import genai
from google.genai import types


MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash"
]


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


def generate_quiz(prompt):

    for model in MODELS:

        print(f"Trying {model}...")

        # Try each model up to 2 times
        for attempt in range(2):

            try:

                response = gemini.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.2
                    )
                )

                print(f"Success with {model}")

                return json.loads(response.text)

            except Exception as error:

                error_text = str(error)

                print(
                    f"{model} attempt {attempt + 1} failed:"
                )
                print(error)

                # Temporary Gemini problems
                if (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                    or "429" in error_text
                    or "RESOURCE_EXHAUSTED" in error_text
                ):

                    if attempt == 0:
                        print("Waiting 5 seconds and trying again...")
                        time.sleep(5)
                        continue

                # Stop retrying this model and try next model
                break

    print("All Gemini models failed.")
    return None


def main():

    # get newest articles
    response = (
        supabase.table("articles")
        .select("id,title,link,source,summary")
        .order("date_added", desc=True)
        .limit(30)
        .execute()
    )

    articles = response.data


    # get articles already used for questions
    used_response = (
        supabase.table("quiz_questions")
        .select("article_id")
        .execute()
    )

    used_ids = {
        item["article_id"]
        for item in used_response.data
        if item["article_id"] is not None
    }


    # only keep unused articles
    unused_articles = []

    for article in articles:

        if article["id"] in used_ids:
            continue

        unused_articles.append({
            "id": article["id"],
            "title": article["title"],
            "source": article["source"],
            "summary": clean_summary(article["summary"])
        })

        if len(unused_articles) >= 20:
            break


    if len(unused_articles) == 0:
        print("No new articles available")
        return


    prompt = f"""
You are creating a daily quiz for high school UIL Current Events students.

Below are recent news articles.

Choose the 5 most important and useful articles for a current events quiz.

Good topics include:
- major government or political events
- international affairs
- economics and business
- major science or technology developments
- important Texas news
- major national news

Avoid:
- entertainment
- celebrity news
- sports
- lifestyle stories
- random facts
- opinion pieces
- weak or trivial stories

Only use facts clearly supported by the title and summary.

For each selected article, make ONE multiple-choice question.

Requirements:
- exactly four choices
- only one correct answer
- believable wrong answers
- question should test an important fact from the story
- do not ask which news source reported it
- do not invent information
- return the article id exactly as provided

Return JSON like this:

[
    {{
        "article_id": 123,
        "question": "Question here?",
        "choice_a": "Choice A",
        "choice_b": "Choice B",
        "choice_c": "Choice C",
        "choice_d": "Choice D",
        "correct_answer": "A"
    }}
]

ARTICLES:

{json.dumps(unused_articles)}
"""


    results = generate_quiz(prompt)


    if results is None:
        print("Quiz generation failed.")
        return


    article_lookup = {
        article["id"]: article
        for article in articles
    }


    added = 0


    for result in results:

        if added >= 5:
            break

        article_id = result.get("article_id")

        if article_id not in article_lookup:
            continue

        if result.get("correct_answer") not in [
            "A",
            "B",
            "C",
            "D"
        ]:
            continue


        article = article_lookup[article_id]


        question_data = {
            "question": result["question"],
            "choice_a": result["choice_a"],
            "choice_b": result["choice_b"],
            "choice_c": result["choice_c"],
            "choice_d": result["choice_d"],
            "correct_answer": result["correct_answer"],
            "source_link": article["link"],
            "article_id": article_id
        }


        try:

            supabase.table(
                "quiz_questions"
            ).insert(
                question_data
            ).execute()

            print("Added:", result["question"])

            added += 1


        except Exception as error:

            print("Could not save question:")
            print(error)


    print(f"Added {added} questions")


if __name__ == "__main__":
    main()