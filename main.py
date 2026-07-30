import feedparser


def main():
    feed_url = "https://feeds.texastribune.org/feeds/main/"
    news_feed = feedparser.parse(feed_url)

    for article in news_feed.entries[:5]:
        print(f"Title: {article.get('title', 'No title')}")
        print(f"Link: {article.get('link', 'No link')}")
        print(f"Published: {article.get('published', 'No date')}")
        print()


if __name__ == "__main__":
    main()