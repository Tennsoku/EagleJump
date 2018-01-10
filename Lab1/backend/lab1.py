from crawler import crawler

if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)

    inverted_index = bot.get_inverted_index()
    print inverted_index

    resolved_inverted_index = bot.get_resolved_inverted_index()
    print resolved_inverted_index
