const SUPABASE_URL = "https://prbewrckgggyoxvcondb.supabase.co";
const SUPABASE_KEY = "sb_publishable_Sjkn68PoI9lofqFk92D-Ow_iye2A874";

const newsGrid = document.getElementById("news-grid");

async function loadNews() {
    try {
        const response = await fetch(
            `${SUPABASE_URL}/rest/v1/articles?select=title,link,source,summary,date_added&order=date_added.desc&limit=6`,
            {
                headers: {
                    apikey: SUPABASE_KEY
                }
            }
        );

        if (!response.ok) {
            throw new Error("Could not load articles");
        }

        const articles = await response.json();

        newsGrid.innerHTML = "";

        articles.forEach(function(article) {
            const card = document.createElement("div");
            card.className = "card";

            const title = document.createElement("div");
            title.className = "title";
            title.textContent = article.title;

            const source = document.createElement("div");
            source.className = "description";
            source.textContent = article.source;

            const summary = document.createElement("div");
            summary.className = "summary";
            summary.textContent = article.summary || "";

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
        newsGrid.innerHTML = "<p>Could not load news.</p>";
    }
}

loadNews();