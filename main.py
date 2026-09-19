import feedparser
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")


supabase = create_client(url, key)

def main():
    added = 0
    feeds = [
        (
            "Texas Tribune",
            "https://feeds.texastribune.org/feeds/main/"
        ),
        (
            "BBC World",
            "https://feeds.bbci.co.uk/news/world/rss.xml"
        ),
        (
            "BBC Business",
            "https://feeds.bbci.co.uk/news/business/rss.xml"
        ),
        (
            "BBC Technology",
            "https://feeds.bbci.co.uk/news/technology/rss.xml"
        )
    ]
    for source, feed_url in feeds:
        news_feed = feedparser.parse(feed_url)

        for article in news_feed.entries:
            link = article.get("link", "")
            title = article.get("title", "")
            summary = article.get("summary", "")

            if skip_article(title, link, summary):
                continue
            article_data = {
                "title": article.title,
                "link": article.link,
                "source": source,
                "published": article.get("published", ""),
                "summary": article.get("summary", "")
            }

            response = (
                supabase.table("articles")
                .upsert(
                    article_data,
                    on_conflict="link",
                    ignore_duplicates=True
                )
                .execute()
            )

            if response.data:
                added += 1
        
    print(f"Added {added} new articles")


def skip_article(title, link, summary):
    title_lower = title.lower()
    link_lower = link.lower()
    text = (title + " " + summary).lower()

    bad_links = [
        "/videos/",
        "/sounds/",
        "/programmes/",
        "/iplayer/",
        "/live/",
        "/newsround/"
    ]

    bad_titles = [
        "watch:",
        "listen:",
        "quiz:",
        "in pictures:",
        "what is ",
        "who is ",
        "how to "
    ]

    if any(word in link_lower for word in bad_links):
        return True

    if any(title_lower.startswith(word) for word in bad_titles):
        return True

    if "podcast" in text or "bbc sounds" in text:
        return True

    return False

if __name__ == "__main__":
    main()