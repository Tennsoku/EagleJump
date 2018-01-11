#Copyright (C) 2011 by Peter Goodman
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import urllib2
import urlparse
from BeautifulSoup import *
from collections import defaultdict
import re
import sqlite3 as lite
import threading
from pagerank import *
import pprint
from selenium import webdriver
import base64
import time

class crawerThread(threading.Thread):
    def __init__(self, threadID, name, func, nargs,nkwargs, *args, **kwargs):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.func = func
        self.nargs = nargs
        self.nkwargs = nkwargs
        self.args = args
        self.kwargs = kwargs

    # can directly -> if self.args/kwargs
    def run(self):
        print "Thread "+self.name+" started."
        if self.nargs & self.nkwargs:
            self.func(self.args,self.kwargs)
            return

        if self.nargs:
            self.func(self.args)
            return

        if self.nkwargs:
            self.func(self.kwargs)
            return

        self.func()

        print "Thread "+self.name+" finished."


def attr(elem, attr):
    """An html attribute from an html element. E.g. <a href="">, then
    attr(elem, "href") will get the href or an empty string."""
    try:
        return elem[attr]
    except:
        return ""

WORD_SEPARATORS = re.compile(r'\s|\n|\r|\t|[^a-zA-Z0-9\-_]')

class crawler(object):
    """Represents 'Googlebot'. Populates a database by crawling and indexing
    a subset of the Internet.

    This crawler keeps track of font sizes and makes it simpler to manage word
    ids and document ids."""

    def __init__(self, db_conn, url_file):

        """Initialize the crawler with a connection to the database to populate
        and with the file containing the list of seed URLs to begin indexing."""
        self._url_queue = [ ]
        self._doc_id_cache = { }                #key url,value doc_id
        self._word_id_cache = { }               #key word string, value word_id
        self.doc_wordlist = { }                  #stores document index as key, and a list of words corresponding to the document as value, in the order of document index
        self.inverted_index = {}
        self.resolved_inverted_index = {}
        self.links = []                     #data structure link relations between pages
        self.pagerank = {}                  #stores score of webpage
        self.web_screenshot = {}            #stores screenshots of top ranked websites
        self.url_title = {}

        # functions to call when entering and exiting specific tags
        self._enter = defaultdict(lambda *a, **ka: self._visit_ignore)
        self._exit = defaultdict(lambda *a, **ka: self._visit_ignore)

        # add a link to our graph, and indexing info to the related page
        self._enter['a'] = self._visit_a

        # record the currently indexed document's title an increase
        # the font size
        def visit_title(*args, **kargs):
            self._visit_title(*args, **kargs)
            self._increase_font_factor(7)(*args, **kargs)

        # increase the font size when we enter these tags
        self._enter['b'] = self._increase_font_factor(2)
        self._enter['strong'] = self._increase_font_factor(2)
        self._enter['i'] = self._increase_font_factor(1)
        self._enter['em'] = self._increase_font_factor(1)
        self._enter['h1'] = self._increase_font_factor(7)
        self._enter['h2'] = self._increase_font_factor(6)
        self._enter['h3'] = self._increase_font_factor(5)
        self._enter['h4'] = self._increase_font_factor(4)
        self._enter['h5'] = self._increase_font_factor(3)
        self._enter['title'] = visit_title

        # decrease the font size when we exit these tags
        self._exit['b'] = self._increase_font_factor(-2)
        self._exit['strong'] = self._increase_font_factor(-2)
        self._exit['i'] = self._increase_font_factor(-1)
        self._exit['em'] = self._increase_font_factor(-1)
        self._exit['h1'] = self._increase_font_factor(-7)
        self._exit['h2'] = self._increase_font_factor(-6)
        self._exit['h3'] = self._increase_font_factor(-5)
        self._exit['h4'] = self._increase_font_factor(-4)
        self._exit['h5'] = self._increase_font_factor(-3)
        self._exit['title'] = self._increase_font_factor(-7)

        # never go in and parse these tags
        self._ignored_tags = set([
            'meta', 'script', 'link', 'meta', 'embed', 'iframe', 'frame', 
            'noscript', 'object', 'svg', 'canvas', 'applet', 'frameset', 
            'textarea', 'style', 'area', 'map', 'base', 'basefont', 'param',
        ])

        # set of words to ignore
        self._ignored_words = set([
            '', 'the', 'of', 'at', 'on', 'in', 'is', 'it',
            'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j',
            'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z', 'and', 'or',
        ])

        # TODO remove me in real version
        self._mock_next_doc_id = 1
        self._mock_next_word_id = 1

        # keep track of some info about the page we are currently parsing
        self._curr_depth = 0
        self._curr_url = ""
        self._curr_doc_id = 0
        self._font_size = 0
        self._curr_words = None

        # lock for multithreading
        self.crawlLock = threading.Lock()

        # get all urls into the queue
        try:
            with open(url_file, 'r') as f:
                for line in f:
                    self._url_queue.append((self._fix_url(line.strip(), ""), 0))
        except IOError:
            pass
    
    # TODO remove me in real version
    def _mock_insert_document(self, url):
        """A function that pretends to insert a url into a document db table
        and then returns that newly inserted document's id."""
        ret_id = self._mock_next_doc_id                                 
        self._mock_next_doc_id += 1
        return ret_id
    
    # TODO remove me in real version
    def _mock_insert_word(self, word):
        """A function that pretends to inster a word into the lexicon db table
        and then returns that newly inserted word's id."""
        ret_id = self._mock_next_word_id
        self._mock_next_word_id += 1
        return ret_id
    
    def word_id(self, word):
        """Get the word id of some specific word."""
        if word in self._word_id_cache:
            return self._word_id_cache[word]
        
        # TODO: 1) add the word to the lexicon, if that fails, then the
        #          word is in the lexicon
        #       2) query the lexicon for the id assigned to this word, 
        #          store it in the word id cache, and return the id.

        word_id = self._mock_insert_word(word)
        self._word_id_cache[word] = word_id                                 #insert entries into word_id_cache
        return word_id
    
    def document_id(self, url):
        """Get the document id for some url."""
        if url in self._doc_id_cache:
            return self._doc_id_cache[url]
        
        # TODO: just like word id cache, but for documents. if the document     Already Done
        #       doesn't exist in the db then only insert the url and leave
        #       the rest to their defaults.
        
        doc_id = self._mock_insert_document(url)
        self._doc_id_cache[url] = doc_id                                    #insert entries into doc_id_cache
        return doc_id
    
    def _fix_url(self, curr_url, rel):
        """Given a url and either something relative to that url or another url,
        get a properly parsed url."""

        rel_l = rel.lower()
        if rel_l.startswith("http://") or rel_l.startswith("https://"):
            curr_url, rel = rel, ""
            
        # compute the new url based on import 
        curr_url = urlparse.urldefrag(curr_url)[0]
        parsed_url = urlparse.urlparse(curr_url)
        return urlparse.urljoin(parsed_url.geturl(), rel)

    def add_link(self, from_doc_id, to_doc_id):
        """Add a link into the database, or increase the number of links between
        two pages in the database."""
        self.links.append((from_doc_id,to_doc_id))          #add tuple entry to the database 

    def _visit_title(self, elem):
        """Called when visiting the <title> tag."""
        title_text = self._text_of(elem).strip()
        print "document title="+ repr(title_text).encode("utf-8")
        self.url_title[self._curr_url] = repr(title_text).encode("utf-8")

        # TODO update document title for document id self._curr_doc_id
    
    def _visit_a(self, elem):                           
        """Called when visiting <a> tags."""

        dest_url = self._fix_url(self._curr_url, attr(elem,"href"))

        #print "href="+repr(dest_url), \
        #      "title="+repr(attr(elem,"title")), \
        #      "alt="+repr(attr(elem,"alt")), \
        #      "text="+repr(self._text_of(elem))

        # add the just found URL to the url queue
        self._url_queue.append((dest_url, self._curr_depth))
        
        # add a link entry into the database from the current document to the
        # other document
        self.add_link(self._curr_doc_id, self.document_id(dest_url))

        # TODO add title/alt/text to index for destination url
    
    def _add_words_to_document(self):
        # TODO: knowing self._curr_doc_id and the list of all words and their
        #       font sizes (in self._curr_words), add all the words into the
        #       database for this document
        self.doc_wordlist[self._curr_doc_id] = self._curr_words #add list of words belonging to each document
        print "    num words="+ str(len(self._curr_words))

    def _increase_font_factor(self, factor):
        """Increade/decrease the current font size."""
        def increase_it(elem):
            self._font_size += factor
        return increase_it
    
    def _visit_ignore(self, elem):
        """Ignore visiting this type of tag"""
        pass

    def _add_text(self, elem):
        """Add some text to the document. This records word ids and word font sizes
        into the self._curr_words list for later processing."""
        words = WORD_SEPARATORS.split(elem.string.lower())
        for word in words:
            word = word.strip()
            if word in self._ignored_words:
                continue
            self._curr_words.append((self.word_id(word), self._font_size))
        
    def _text_of(self, elem):
        """Get the text inside some element without any tags."""
        if isinstance(elem, Tag):
            text = [ ]
            for sub_elem in elem:
                text.append(self._text_of(sub_elem))
            
            return " ".join(text)
        else:
            return elem.string

    def _index_document(self, soup):
        """Traverse the document in depth-first order and call functions when entering
        and leaving tags. When we come accross some text, add it into the index. This
        handles ignoring tags that we have no business looking at."""
        class DummyTag(object):
            next = False
            name = ''
        
        class NextTag(object):
            def __init__(self, obj):
                self.next = obj
        
        tag = soup.html
        stack = [DummyTag(), soup.html]

        while tag and tag.next:
            tag = tag.next

            # html tag
            if isinstance(tag, Tag):

                if tag.parent != stack[-1]:
                    self._exit[stack[-1].name.lower()](stack[-1])
                    stack.pop()

                tag_name = tag.name.lower()

                # ignore this tag and everything in it
                if tag_name in self._ignored_tags:
                    if tag.nextSibling:
                        tag = NextTag(tag.nextSibling)
                    else:
                        self._exit[stack[-1].name.lower()](stack[-1])
                        stack.pop()
                        tag = NextTag(tag.parent.nextSibling)
                    
                    continue
                
                # enter the tag
                self._enter[tag_name](tag)
                stack.append(tag)

            # text (text, cdata, comments, etc.)
            else:
                self._add_text(tag)

######################################################################################## lab1

    def get_inverted_index(self):

        for key1 in self._word_id_cache:

            docID = set();
            wordID = self._word_id_cache[key1]              #iterates through all the words to get wordID

            for key2 in self.doc_wordlist:

                wordlist = self.doc_wordlist[key2]      #get list of words for each document
                #print wordlist
                wordIDlist = [i[0] for i in wordlist]   #the first element in each tuple element in wordlist is the ID of the word
                #print wordIDlist           #create a list of wordID

                for j in wordIDlist:

                    if wordID == j:         #compare the desired wordID with every element in the wordIDlist
                        docID.add(key2)     #if matches, note down the document ID in which the word is found

            self.inverted_index[wordID]=docID           #inserts entry into the inverted_index dictionary

        return self.inverted_index

    def get_resolved_inverted_index(self):

        doc_url_cache = dict(zip(self._doc_id_cache.values(),self._doc_id_cache.keys()))    #create dictionary where docID is key, and url is value

        id_word_cache = dict(zip(self._word_id_cache.values(), self._word_id_cache.keys())) #create dictionary where wordID is key, and word string is value

        for key1 in self._word_id_cache:            #do the same thing as get_inverted_index() except store the word string as key and document URL as value

            docName = set();
            wordID = self._word_id_cache[key1]

            for key2 in self.doc_wordlist:

                wordlist = self.doc_wordlist[key2]
                wordIDlist = [i[0] for i in wordlist]

                for j in wordIDlist:

                    if wordID == j:
                        docName.add(doc_url_cache[key2])

            self.resolved_inverted_index[id_word_cache[wordID]]=docName

        return self.resolved_inverted_index

##################################################################################  lab3

    def store_doc_index (self):                        #stores document index on disk
        con = lite.connect("document_index.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS DocIndex (url text,doc_id integer)")
        for url in self._doc_id_cache:
            cur.execute("INSERT INTO DocIndex VALUES (?,?)", (url,self._doc_id_cache[url]))
        
        con.commit()
        con.close()


    def store_lexicon (self):                            #stores lexicon on disk

        con = lite.connect("lexicon.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Lexicon (word text, word_id integer)")
        for word in self._word_id_cache:
            cur.execute("INSERT INTO Lexicon VALUES (?,?)", (word,self._word_id_cache[word]))

        con.commit()
        con.close()


    def store_inverted_index(self):                        #stores inverted index on disk

        con = lite.connect("inverted_index.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS InvertedIndex (word_id integer, doc_id integer)")
        for wordID in self.inverted_index:
            for docID in self.inverted_index[wordID]:
                cur.execute("INSERT INTO InvertedIndex VALUES (?,?)", (wordID,docID))

        con.commit()
        con.close()

    def store_page_rank(self): #stores page rank on disk

        self.pagerank = page_rank(self.links)
        #pprint.pprint(self.pagerank)


    def store_screenshot(self):            #stores screenshot of top five ranked webpages

        i=1    
        doc_url_cache = dict(zip(self._doc_id_cache.values(),self._doc_id_cache.keys()))
        br = webdriver.PhantomJS("./backend")
        br.set_window_size(1024,768)

        for key in self.pagerank:            
            br.get(doc_url_cache[self.pagerank[key]])
            time.sleep(2)
            br.save_screenshot('%d.png'%self.pagerank[key])        

            # if i==5:
            #     break
        
            i+=1
        
        br.quit

    def store_doc_title(self):
        con = lite.connect("document_title.db")
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS DocumentTitle (url string, title string)")
        for url in self.url_title:
            cur.execute("INSERT INTO DocumentTitle VALUES (?,?)", (url.encode("utf-8"),self.url_title[url].encode("utf-8")))
        con.commit()
        con.close()

###################################################################################################

    def multithread_crawl(self, depth=2, timeout=3):
        seen = set()
        _depth = depth[0]

        while 1:

            self.crawlLock.acquire()
            if not len(self._url_queue):
                self.crawlLock.release()
                break
            url, depth_ = self._url_queue.pop()

            # skip this url; it's too deep
            if depth_ > _depth:
                self.crawlLock.release()
                continue

            doc_id = self.document_id(url)

            # we've already seen this document
            if doc_id in seen:
                self.crawlLock.release()
                continue

            seen.add(doc_id) # mark this document as haven't been visited
            self.crawlLock.release()
            
            socket = None
            try:
                socket = urllib2.urlopen(url, timeout=timeout)
                soup = BeautifulSoup(socket.read())
                
                self.crawlLock.acquire()
                self._curr_depth = depth_ + 1
                self._curr_url = url
                self._curr_doc_id = doc_id
                self._font_size = 0
                self._curr_words = [ ]
                self._index_document(soup)
                self._add_words_to_document()
                print "    url="+repr(self._curr_url)
                self.crawlLock.release()

            except Exception as e:
                print e
                pass
            finally:
                if socket:
                    socket.close()


###################################################################################################

    def crawl(self, depth=2, timeout=3):
        """Crawl the web!"""
        crawlThread1 = crawerThread(1,"crawlThread1",self.multithread_crawl,1,0,depth)
        crawlThread2 = crawerThread(2,"crawlThread2",self.multithread_crawl,1,0,depth)
        crawlThread3 = crawerThread(3,"crawlThread3",self.multithread_crawl,1,0,depth)
        crawlThread4 = crawerThread(4,"crawlThread4",self.multithread_crawl,1,0,depth)

        crawlThread1.start()
        crawlThread2.start()
        crawlThread3.start()
        crawlThread4.start()

        crawlThread1.join()
        crawlThread2.join()
        crawlThread3.join()
        crawlThread4.join()


        # print self.get_inverted_index()
        # print self.get_resolved_inverted_index()

        storeThread1 = crawerThread(1,"storeDocIndex",self.store_doc_index,0,0,None,None)
        storeThread2 = crawerThread(2,"storeLexicon",self.store_lexicon,0,0,None,None)
        storeThread3 = crawerThread(3,"storeInvertedIndex",self.store_inverted_index,0,0,None,None)
        storeThread4 = crawerThread(4,"storePageRank",self.store_page_rank,0,0,None,None)
        
        storeThread6 = crawerThread(6,"storeDocTitle",self.store_doc_title,0,0,None,None)

        storeThread1.start()
        storeThread2.start()
        storeThread3.start()
        storeThread4.start()
        storeThread6.start()

        storeThread1.join()
        storeThread2.join()
        storeThread3.join()
        storeThread4.join()
        storeThread6.join()
        self.store_screenshot()


    #self.store_screenshot()
    #print "screenshots saved"
    #print self.web_screenshot

    # self.store_doc_index()                                #stores data structures on disk
    # self.store_lexicon()
    # self.store_inverted_index()
    # print sorted(self.pagerank.items(),key = lambda x:x[0],reverse=True)

if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)


