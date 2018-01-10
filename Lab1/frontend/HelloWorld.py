import collections
from itertools import islice
from bottle import route, run, template, error, post, get, request, view, static_file
#global dictionary
history = {}

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

@route('/')
@view('index')

def search():
    # check initial
    if len(history) == 0:
        return dict(historyList=list(history))

    # Sort the dictionary to be ordered
    ordered = collections.OrderedDict(sorted(history.items(), key=lambda t: t[1], reverse=True))
    # get first 20 elements
    topWords = list(islice(ordered.iteritems(), 20))

    return dict(historyList=topWords)

def input_analysis():
    input_string = request.get('keywords')

    #corner case test
    if len(input_string) == 0:
        return "Oops, you input nothing!"

    #split into seperate words
    words = input_string.split()
    unique_words = set(words)
    returnTable = """
        <table id="results">
        <tr><td> Word </td><td> Count </td></tr>
    """
    #generate html in string
    for word in unique_words:
        returnTable = returnTable + "<tr><td>" + word +"</td>"
        count = input_string.count(word)
        returnTable = returnTable + "<td> %u </td><tr>" % (count)

        #insert word to dictionary History
        global history
        if history.has_key(word):
            history[word] += count
        else:
            history.update({word:count})

    returnTable = returnTable + "</table>"

    return returnTable


@route('/history')
def printHistory():
    #check initial
    if len(history) == 0:
        return "No History Yet."

    #Sort the dictionary to be ordered
    ordered = collections.OrderedDict(sorted(history.items(), key=lambda t:t[1], reverse=True))
    #get first 20 elements
    topWords = list(islice(ordered.iteritems(),20))
    #build up table
    returnTable = """
            <table id="history">
        """
    for topWord in topWords:
        returnTable = returnTable + "<tr><td>" + topWord[0] + "</td>"
        returnTable = returnTable + "<td> %u </td><tr>" % (topWord[1])

    returnTable = returnTable + "</table>"
    return returnTable

@route('/<name>')
def hello(name='Stranger'):
    return  template('Hi,{{name}}, this is a test page.', name = name)

@error(404)
def error404(error):
    return '404: Page not found.'

run(host='localhost', port=8080, debug=True)
