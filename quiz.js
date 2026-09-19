const SUPABASE_URL = "https://prbewrckgggyoxvcondb.supabase.co";
const SUPABASE_KEY = "sb_publishable_Sjkn68PoI9lofqFk92D-Ow_iye2A874";

let questions = [];
let currentQuestion = 0;
let score = 0;
let selectedAnswer = null;

const question = document.getElementById("question");
const questionNumber = document.getElementById("question-number");
const answers = document.getElementById("answers");
const nextButton = document.getElementById("next-button");
const answerResult = document.getElementById("answer-result");
const quizCard = document.querySelector(".quiz-card");


async function loadQuestions() {
    try {
        const response = await fetch(
            `${SUPABASE_URL}/rest/v1/quiz_questions?select=question,choice_a,choice_b,choice_c,choice_d,correct_answer&order=id.desc&limit=5`,
            {
                headers: {
                    apikey: SUPABASE_KEY
                }
            }
        );

        if (!response.ok) {
            throw new Error("Could not load questions");
        }

        const data = await response.json();

        questions = data.map(function(item) {
            return {
                question: item.question,

                answers: [
                    item.choice_a,
                    item.choice_b,
                    item.choice_c,
                    item.choice_d
                ],

                correct: item.correct_answer
            };
        });

        if (questions.length === 0) {
            quizCard.innerHTML = "<p>No quiz questions available right now.</p>";
            return;
        }

        showQuestion();

    } catch (error) {
        console.error(error);
        quizCard.innerHTML = "<p>Could not load quiz questions.</p>";
    }
}


function showQuestion() {
    selectedAnswer = null;

    nextButton.disabled = true;
    answerResult.textContent = "";

    questionNumber.textContent =
        `Question ${currentQuestion + 1} of ${questions.length}`;

    question.textContent =
        questions[currentQuestion].question;

    answers.innerHTML = "";

    const letters = ["A", "B", "C", "D"];

    questions[currentQuestion].answers.forEach(function(answer, index) {

        const button = document.createElement("button");

        button.className = "answer-button";

        button.textContent =
            letters[index] + ". " + answer;


        button.addEventListener("click", function() {

            selectedAnswer = letters[index];

            const correctLetter =
                questions[currentQuestion].correct;

            const correctIndex =
                letters.indexOf(correctLetter);

            const correctText =
                questions[currentQuestion].answers[correctIndex];

            const allButtons =
                document.querySelectorAll(".answer-button");


            allButtons.forEach(function(answerButton) {
                answerButton.disabled = true;
            });


            if (selectedAnswer === correctLetter) {

                button.classList.add("correct");

                answerResult.textContent =
                    `Correct! Answer: ${correctLetter}. ${correctText}`;

            } else {

                button.classList.add("wrong");

                allButtons[correctIndex].classList.add("correct");

                answerResult.textContent =
                    `Correct answer: ${correctLetter}. ${correctText}`;
            }

            nextButton.disabled = false;
        });


        answers.appendChild(button);
    });
}


nextButton.addEventListener("click", function() {

    if (selectedAnswer === questions[currentQuestion].correct) {
        score++;
    }

    currentQuestion++;


    if (currentQuestion < questions.length) {

        showQuestion();

    } else {

        showResults();

    }
});


function showResults() {

    questionNumber.textContent = "Quiz Complete";

    quizCard.innerHTML = `
        <h2>Your Score: ${score}/${questions.length}</h2>

        <p>
            You answered ${score} out of
            ${questions.length} questions correctly.
        </p>

        <button onclick="location.reload()" id="next-button">
            Try Again
        </button>
    `;
}


loadQuestions();