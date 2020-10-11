from flask import Flask, request, url_for
import simplejson as json
import text_processor
import elastic
app = Flask(__name__)

def get_text():
    content = request.get_json(silent=True)
    return content['text']

def make_response(o):
    response_text = json.dumps(o, indent=2,  ensure_ascii=False)
    return response_text, 200, {'Content-Type': 'application/json; charset=utf-8'}

# ---------------------------------------------------
@app.route('/')
def index():
    s = ''
    s = url_for('index')+'\n'
    s += url_for('lemmas_entities')+'\n'
    s += url_for('clear_lemmas_entities')+'\n'
    s += url_for('entities')+'\n'

    return s, 200, {'Content-Type': 'text/css; charset=utf-8'}


@app.route('/lemmas-entities', methods=['POST'])
def lemmas_entities():
    text = get_text()
    o = text_processor.process_text(text)
    return make_response(o)

@app.route('/clear-lemmas-entities', methods=['POST'])
def clear_lemmas_entities():
    text = get_text()
    o = text_processor.process_text(text, clear=True)
    return make_response(o)

@app.route('/entities', methods=['POST'])
def entities():
    text = get_text()
    o = text_processor.process_entities(text)
    return make_response(o)

@app.route('/search', methods=['POST'])
def search():
    text = get_text()
    field = request.args.get('field','lemmatized_text')
    skip = request.args.get('skip', 0)
    limit = request.args.get('limit',50)
    timeout = request.args.get('timeout','5s')
    lemmatize = request.args.get('lemmatize',True)

    if lemmatize:
        o = text_processor.process_text(text, clear=True)
        text = o.get('lemmatized_text','')

    search_result = elastic.search(text, skip=skip, limit=limit, field=field, timeout=timeout)
    return make_response(search_result)


# https://medium.com/@dkhd/handling-multiple-requests-on-flask-60208eacc154
if __name__ == '__main__':
    print("MAIN!!!!!  TEXT-PROCESSOR started.  ")
    # app.run(host= '0.0.0.0',  port=5000, debug=True) # threaded=True, processes=3
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)    