import os
import random

from supabase import create_client


SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


response = (
    supabase
    .table("quiz_questions")
    .select(
        "id,"
        "question,"
        "choice_a,"
        "choice_b,"
        "choice_c,"
        "choice_d,"
        "correct_answer"
    )
    .order("id", desc=True)
    .limit(5)
    .execute()
)


questions = response.data or []


# Make sure the five questions do not
# all end up with the same correct letter.
positions = ["A", "B", "C", "D"]

while len(positions) < len(questions):
    positions.append(
        random.choice(["A", "B", "C", "D"])
    )

random.shuffle(positions)


for i, q in enumerate(questions):

    old_choices = {
        "A": q["choice_a"],
        "B": q["choice_b"],
        "C": q["choice_c"],
        "D": q["choice_d"]
    }

    old_correct = str(
        q["correct_answer"]
    ).strip()

    # Get the actual correct answer text
    if old_correct.upper() in old_choices:
        correct_text = old_choices[
            old_correct.upper()
        ]

    else:
        correct_text = old_correct

    # Get the wrong answers
    wrong_answers = []

    for letter, text in old_choices.items():
        if text != correct_text:
            wrong_answers.append(text)

    random.shuffle(wrong_answers)

    new_correct_letter = positions[i]

    new_choices = {
        "A": None,
        "B": None,
        "C": None,
        "D": None
    }

    new_choices[new_correct_letter] = correct_text

    wrong_index = 0

    for letter in ["A", "B", "C", "D"]:

        if new_choices[letter] is None:
            new_choices[letter] = (
                wrong_answers[wrong_index]
            )

            wrong_index += 1

    (
        supabase
        .table("quiz_questions")
        .update({
            "choice_a": new_choices["A"],
            "choice_b": new_choices["B"],
            "choice_c": new_choices["C"],
            "choice_d": new_choices["D"],
            "correct_answer":
                new_correct_letter
        })
        .eq("id", q["id"])
        .execute()
    )

    print(
        f"Question {q['id']} -> "
        f"correct answer is now "
        f"{new_correct_letter}"
    )


print("Finished shuffling current quiz.")