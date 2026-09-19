const SUPABASE_URL = "https://prbewrckgggyoxvcondb.supabase.co";
const SUPABASE_KEY = "sb_publishable_Sjkn68PoI9lofqFk92D-Ow_iye2A874";

const newsGrid = document.getElementById("news-grid");
const dateInput = document.getElementById("news-date");
const dateLabel = document.getElementById("date-label");
const prevButton = document.getElementById("prev-day");
const nextButton = document.getElementById("next-day");

let selectedDate = new Date();


function dateToInput(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
}


function inputToDate(value) {
    const parts = value.split("-");

    return new Date(
        Number(parts[0]),
        Number(parts[1]) - 1,
        Number(parts[2])
    );
}


async function loadNews() {

    newsGrid.innerHTML = "<p>Loading news...</p>";

    const start = new Date(selectedDate);
    start.setHours(0, 0, 0, 0);

    const end = new Date(start);
    end.setDate(end.getDate() + 1);

    dateLabel.textContent = selectedDate.toLocaleDateString(
        "en-US",
        {
            weekday: "long",
            month: "long",
            day: "numeric",
            year: "numeric"
        }
    );

    try {

        const response = await fetch(
            `${SUPABASE_URL}/rest/v1/articles?select=title,link,source,summary,date_added&date_added=gte.${encodeURIComponent(start.toISOString())}&date_added=lt.${encodeURIComponent(end.toISOString())}&order=date_added.desc`,
            {
                headers: {
                    apikey: SUPABASE_KEY
                }
            }
        );

        if (!response.ok) {
            throw new Error("Could not load news");
        }

        const articles = await response.json();

        newsGrid.innerHTML = "";

        if (articles.length === 0) {
            newsGrid.innerHTML =
                "<p>No articles were collected on this day.</p>";
            return;
        }


        articles.forEach(function(article) {

            const card = document.createElement("div");
            card.className = "card";


            const title = document.createElement("h3");
            title.className = "title";
            title.textContent = article.title;


            const source = document.createElement("p");
            source.className = "description";
            source.textContent = article.source;


            const summary = document.createElement("p");
            summary.className = "summary";

            if (article.summary) {

                const page = new DOMParser().parseFromString(
                    article.summary,
                    "text/html"
                );

                let text = page.body.textContent.trim();

                if (text.length > 220) {
                    text = text.substring(0, 220) + "...";
                }

                summary.textContent = text;
            }


            const button = document.createElement("button");
            button.className = "cta";
            button.textContent = "Read More";

            button.addEventListener("click", function() {
                window.open(article.link, "_blank");
            });


            card.appendChild(title);
            card.appendChild(source);
            card.appendChild(summary);
            card.appendChild(button);

            newsGrid.appendChild(card);
        });


    } catch (error) {

        console.error(error);

        newsGrid.innerHTML =
            "<p>Could not load news right now.</p>";
    }
}


prevButton.addEventListener("click", function() {

    selectedDate.setDate(selectedDate.getDate() - 1);

    dateInput.value = dateToInput(selectedDate);

    loadNews();
});


nextButton.addEventListener("click", function() {

    const tomorrow = new Date(selectedDate);
    tomorrow.setDate(tomorrow.getDate() + 1);

    const today = new Date();
    today.setHours(23, 59, 59, 999);

    if (tomorrow <= today) {

        selectedDate = tomorrow;

        dateInput.value = dateToInput(selectedDate);

        loadNews();
    }
});


dateInput.addEventListener("change", function() {

    selectedDate = inputToDate(dateInput.value);

    loadNews();
});


dateInput.value = dateToInput(selectedDate);

loadNews();