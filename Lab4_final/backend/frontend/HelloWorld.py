import collections
import httplib2
import bottle
import re
import math
import sqlite3
import random
from itertools import islice
from bottle import route, run, template, error, post, get, request, view, static_file, hook, response

# Session Control
from beaker.middleware import SessionMiddleware

# For Google Client
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import flow_from_clientsecrets
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build


## global dictionary
history = {}
recentSearch = {}
#login = False
session_opts = {
    'session.type': 'file',
    'session.cookie_expires': 86400, # cookie will last for 24 hours
    'session.data_dir': './data',
    'session.auto': True,
    'session.user':None
}

app = SessionMiddleware(bottle.app(), session_opts)

## set static file path 
@route('/static/assets/css/<filename>')
def static(filename):
    return static_file(filename, root='static/assets/css/')

@route('/static/assets/js/<filename>')
def static(filename):
    return static_file(filename, root='static/assets/js/')

@route('/static/assets/ico/<filename>')
def static(filename):
    return static_file(filename, root='static/assets/ico/')

@route('/static/assets/img/<filename>')
def static(filename):
    return static_file(filename, root='static/assets/img/')

@route('/static/assets/img/background/<filename>')
def static(filename):
    return static_file(filename, root='static/assets/img/background/')

@route('/static/assets/bootstrap/<filename>')
def static(filename):
    return static_file(filename, root='static/assets/bootstrap/')

#hook to strip the trailing slashes
@hook('before_request')
def strip_path():
    request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')

    
#homepage
@route('/')
@view('index')
def search():
    # get session
    session = request.environ.get('beaker.session')

    # get login info
    login = 'user' in session
    if login:
        name = session['user']
        id = session['user_id']
        ico = session['user_ico']
        link = session['user_info_page']
    else:
        name = None
        ico = None
        link = None
        id = None

    id = 114514
    if 114514 not in history:
        history[114514] = {}
    if 114514 not in recentSearch:
        recentSearch[114514] = []

    
    # check if cookies can cause Error 500
    if id not in history:
        login = False
        session.delete()
        response.set_cookie('login', "False")
        response.set_cookie('login_id', "None")

    # get autocomplete words
    conn = sqlite3.connect("db/lexicon.db")
    c = conn.cursor()

    inputstring = "SELECT word from Lexicon"

    c.execute(inputstring)
    results = c.fetchall()

    conn.close()

    autocomplete = ""
    for result in results:
        autocomplete += result[0].encode("utf-8") + "***"

    if (random.random()<0.3):
        suggestion = "Find Your World!"
    else :
        suggestion = results[random.randint(0,len(results))][0].encode("utf-8")


    # get suggestion search
    # suggestion = {}
    # for uid in history:
    #     # if id == uid:
    #     #     continue
    #     if not history[uid]:
    #         continue
    #     suggestion.update({history[uid].keys()[0]:history[uid].values()[0]})

    # print suggestion

    # orderedSuggestion = collections.OrderedDict(sorted(suggestion.items(), key=lambda t: t[1], reverse=True))

    # if not orderedSuggestion:
    #     orderedSuggestion.update({"Find Your World!":1})



    # print list(orderedSuggestion)[0]

    # if login == False:
    #     return dict(login=login, name=name, ico=ico, link=link, autocomplete=autocomplete, suggestion=list(orderedSuggestion)[0])
	# Sort the dictionary to be ordered
    ordered = collections.OrderedDict(sorted(history[id].items(), key=lambda t: t[1], reverse=True))
    # get first 20 elements
    topWords = list(islice(ordered.iteritems(), 20))

    return dict(historyList=topWords, login=True, name="admin", ico="static/assets/img/logo2.png", link="https://www.utoronto.ca/", autocomplete=autocomplete,  suggestion=suggestion) # suggestion=list(orderedSuggestion)[0]


# logout page
@route('/logout')
def logout():
    # get session
    session = request.environ.get('beaker.session')
    # set cookies
    response.set_cookie("login", "False")
    response.set_cookie("login_id", "None")
    # remove session info
    session.delete()

    # redirect to logout page
    bottle.redirect('/')

# login redirect page
@route('/login','GET')
def home():
    # get redirect uri
    flow = flow_from_clientsecrets("client_secret.json",
        scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email',
        redirect_uri="http://localhost:8080/redirect"
        # redirect_uri="htttp://ec2-54-156-190-30.compute-1.amazonaws.com/redirect"
        )
    uri = flow.step1_get_authorize_url()

    bottle.redirect(str(uri))

@route('/redirect')
def redirected_page():
    # get session
    session = bottle.request.environ.get('beaker.session')
    code = request.query.get('code', '')
    flow = OAuth2WebServerFlow(client_id='...',
                               client_secret='...',
                               scope='https://www.googleapis.com/auth/plus.me https://www.googleapis.com/auth/userinfo.email' ,
                               redirect_uri="http://localhost:8080/redirect"
                               # redirect_uri="htttp://ec2-54-156-190-30.compute-1.amazonaws.com/redirect"
                               )
    credentials = flow.step2_exchange(code)
    token = credentials.id_token['sub']

    http = httplib2.Http()
    http = credentials.authorize(http)

    # Get user info and store in session
    users_service = build('oauth2', 'v2', http=http)
    user_document = users_service.userinfo().get().execute()
    session['user_email'] = user_document['email']
    session['user_ico'] = user_document['picture']
    session['user'] = user_document['name']
    session['user_info_page'] = user_document['link']
    session['user_id'] = user_document['id']
    name = session['user']
    id = session['user_id']
    session.save()

    if session['user_id'] not in history:
        history[session['user_id']] = {}
    if session['user_id'] not in recentSearch:
        recentSearch[session['user_id']] = []

    # set cookies
    response.set_cookie("login", "True")
    response.set_cookie("login_id", session['user_id'])

    bottle.redirect('/')

#result page
@route('/result')
@view('searchResult')
def printHistory():
    # get session
    session = bottle.request.environ.get('beaker.session')

    # get login info
    login = 'user' in session


    if login:
        name = session['user']
        id = session['user_id']
        ico = session['user_ico']
        link = session['user_info_page']
    else:
        name = None
        ico = None
        link = None
        id = None

    id = 114514
    if 114514 not in history:
        history[114514] = {}
    if 114514 not in recentSearch:
        recentSearch[114514] = []

    # check if cookies can cause Error 500
    if id not in history:
        login = False
        session.delete()
        response.set_cookie('login', "False")
        response.set_cookie('login_id', "None")

    # convert all to lower case
    input = request.query.keywords.lower()
    # remove punctuations
    input_string = re.sub(r'[^\w\s]','',input)

    # split into seperate words
    #words = [w.strip(string.punctuation) for w in input_string.split()]
    words = input_string.split()

    if not words:
        return dict(login=login,input=[],page_num=0)

    # get total page number for AJAX
    urls = find_urls(words[0])

    titles = []
    doc_ids = []

    if not urls:
        nurl = 0
        script = None
        page_num = 0
    else:
        nurl = len(urls)
        page_num = int(nurl/5)
        if (nurl % 5) !=0:
            page_num +=1
        # print "page_num: "
        # print  page_num

        for url in urls:
            title = readDB("db/document_title.db","DocumentTitle","title","url",url)[0][0][2:-1]

            if title:
                # print title
                # print "title for " + url.encode("utf-8") +": "+title.encode("utf-8")
                titles.append(title.encode("utf-8").replace("&#x27;","\\\'"))
            else:
                titles.append("")

            doc_id = readDB("db/document_index.db","DocIndex","doc_id","url",url)[0][0]
            doc_ids.append(doc_id)
            print "doc_id for url: "+ url+" = " + str(doc_id)

        # print "titles: "
        # print  titles

        print "doc_ids: "
        print  doc_ids

        script = ""
        for i in range(nurl):
            if (i<3):
                script += "<img class=\"result_pic\" src=\"/static/assets/img/"+str(doc_ids[i]+1)+".png\" width=\"500\"></br>"

            script += "<b class=\"result_title\"> "+titles[i]+" </b><a href=\""+urls[i]+"\" class=\"result_url\" target=\"_blank\">"+urls[i]+"</a></br></br>"
            if (i<nurl-1):
                script +="***"

    # remove duplicated words
    unique_words = set(words)
    
    unique_words_copy = unique_words.copy()

    # update recent search dict
    if True:
        if recentSearch[id]:
            if input in recentSearch[id]:
                recentSearch[id].remove(input)
        recentSearch[id].insert(0, input)
        # resize list
        recentSearch[id] = recentSearch[id][:10]


    # to keep order, we have to use "for" method here
    for word in words:
        if word in unique_words:
            count = words.count(word)

            # insert word to global dictionary "History"
            if True:
                if history[id].has_key(word):
                    history[id][word] += count
                else:
                    history[id].update({word:count})
            # remove this word in unique_word since it has shown
            unique_words.remove(word)

    if True:
        # Sort the dictionary to be ordered
        ordered = collections.OrderedDict(sorted(history[id].items(), key=lambda t: t[1], reverse=True))
        # get first 20 elements
        topWords = list(islice(ordered.iteritems(), 20))
    else: 
        return dict(login=login,input=input, words=words, unique_words=unique_words_copy,page_num=page_num,urls=script)

    return dict(historyList=topWords, 
                input=input, 
                login=True, 
                name="admin", 
                ico="static/assets/img/logo2.png", 
                link="http://utoronto.ca", 
                words=words, 
                unique_words=unique_words_copy,
                recentSearch = recentSearch[id],
                page_num=page_num,
                urls=script)

def readDB(dbFile, table, output, input, value):
    conn = sqlite3.connect(dbFile)
    c = conn.cursor()

    inputstring = "SELECT %s from %s where %s = '%s'" % (output, table, input, value)

    c.execute(inputstring)
    #c.execute("SELECT * FROM Lexicon")
    results = c.fetchall()

    conn.close()

    return results

def find_urls(key):
    # print "key: "+key
    word_id = readDB("db/lexicon.db","Lexicon","word_id","word",key)
    # print "word_id: "
    # print word_id

    if not word_id:
        return None

    doc_ids = readDB("db/inverted_index.db","InvertedIndex","doc_id","word_id", word_id[0][0])
    # print "doc_ids: "
    # print doc_ids

    if not doc_ids:
        return None

    doc_ids_list = [x[0] for x in doc_ids]
    # print "doc_ids_list: "
    # print doc_ids_list
    url_ranks = []
    for doc_id in doc_ids_list:
        rank = readDB("db/page_rank.db","PageRank","score","doc_id", doc_id)
        if rank:
            print rank
            print "rank for %d: %e" % (doc_id, rank[0][0])
            url_ranks.append(rank[0][0])
        else:
            print "No rank data for %d" % doc_id
            url_ranks.append(0)

    ranked_doc = zip(url_ranks, doc_ids_list)
    ranked_doc.sort(reverse=True)
    # print "Ranked_doc after sort: "
    # print ranked_doc

    urls=[]
    for id in ranked_doc:
        url = readDB("db/document_index.db","DocIndex","url","doc_id",id[1])
        # print "url for %d: " % id[1]
        # print url
        urls.append(url[0][0].encode("utf-8"))
    print "urls: "
    print urls
    return urls

#test page for backend
@route('/test')
@view('test')
def test():
    return None

@route('/<filename>')
def test_html(filename):
    return static_file(filename, root='./views')

#test page2
#@route('/<name>')
#def hello(name='Stranger'):
#    return  template('Hi,{{name}}, this is a test page.', name = name)

#404 error page
@error(404)
@view('404')
def error404(error):
    # get session
    session = bottle.request.environ.get('beaker.session')

    # get login info
    login = 'user' in session


    if login:
        name = session['user']
        id = session['user_id']
        ico = session['user_ico']
        link = session['user_info_page']
    else:
        name = None
        ico = None
        link = None
        id = None

    id = 114514

    # check if cookies can cause Error 500
    if id not in history:
        login = False
        session.delete()
        response.set_cookie('login', "False")
        response.set_cookie('login_id', "None")

    return dict(login=True, name="admin", ico="static/assets/img/logo2.png", link="https://www.utoronto.ca/")

run(host='localhost', port=8080, debug=True, app=app)
# run(host='0.0.0.0', port=80, debug=True, app=app)



