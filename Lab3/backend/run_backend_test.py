from crawler import crawler
from pagerank import page_rank
import pprint

if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)

    # print "bot.links: "
    # print bot.links

    pageranks = page_rank(bot.links)				#calculates the page rank score and stores the data on disk
    
    pprint.pprint(pageranks)

