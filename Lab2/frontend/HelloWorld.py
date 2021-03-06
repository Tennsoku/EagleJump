import collections
import httplib2
import bottle
import re
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
    
    # check if cookies can cause Error 500
    if id not in history:
        login = False
        session.delete()
        response.set_cookie('login', "False")
        response.set_cookie('login_id', "None")

    if login == False:
        return dict(login=login, name=name, ico=ico, link=link)
	# Sort the dictionary to be ordered
    ordered = collections.OrderedDict(sorted(history[id].items(), key=lambda t: t[1], reverse=True))
    # get first 20 elements
    topWords = list(islice(ordered.iteritems(), 20))

    return dict(historyList=topWords, login=login, name=name, ico=ico, link=link)

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

    # remove duplicated words
    unique_words = set(words)
    
    unique_words_copy = unique_words.copy()

    # update recent search dict
    if login:
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
            if login:
                if history[id].has_key(word):
                    history[id][word] += count
                else:
                    history[id].update({word:count})
            # remove this word in unique_word since it has shown
            unique_words.remove(word)

    if login:
        # Sort the dictionary to be ordered
        ordered = collections.OrderedDict(sorted(history[id].items(), key=lambda t: t[1], reverse=True))
        # get first 20 elements
        topWords = list(islice(ordered.iteritems(), 20))
    else: 
        return dict(login=login,input=input, words=words, unique_words=unique_words_copy)
    

    return dict(historyList=topWords, 
                input=input, 
                login=login, 
                name=name, 
                ico=ico, 
                link=link, 
                words=words, 
                unique_words=unique_words_copy,
                recentSearch = recentSearch[id])

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
def error404(error):
    return '404: Page not found.'

run(host='localhost', port=8080, debug=True, app=app)
# run(host='0.0.0.0', port=80, debug=True, app=app)



