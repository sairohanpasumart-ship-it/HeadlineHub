import feedparser
import sqlite3

def main():
    connection = sqlite3.connect("headlinelab.db")
    cursor = connection.cursor()
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
            cursor.execute("""
                INSERT OR IGNORE INTO articles
                (title, link, source, published, summary)
                VALUES (?, ?, ?, ?, ?)
            """, (
                article.title,
                article.link,
                source,
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