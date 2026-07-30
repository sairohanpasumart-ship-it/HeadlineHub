import feedparser
import sqlite3

def main():
    feed_url = "https://feeds.texastribune.org/feeds/main/"
    news_feed = feedparser.parse(feed_url)
    connection = sqlite3.connect("headlinelab.db")
    cursor = connection.cursor()
    added = 0
    for article in news_feed.entries:
        cursor.execute("""
            INSERT OR IGNORE INTO articles
            (title, link, source, published, summary)
            VALUES (?, ?, ?, ?, ?)
        """, (
            article.title,
            article.link,
            "Texas Tribune",
            article.get("published", ""),
            article.get("summary", "")
        ))
        if cursor.rowcount == 1:
            added += 1

    connection.commit()
    connection.close()

    print(f"Added {added} new articles")



if __name__ == "__main__":
    main()