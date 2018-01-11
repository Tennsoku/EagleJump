from crawler import crawler
from pagerank import page_rank
import pprint

if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)

    # print "bot.links: "
    # print bot.links
