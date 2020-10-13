from flask import Flask, request, url_for
import simplejson as json
import text_processor
import elastic
import logging
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
    limit = request.args.get('limit',20)
    timeout = request.args.get('timeout','5s')
    lemmatize = request.args.get('lemmatize',True)
    from_date = request.args.get('from_date','2000-01-01')
    to_date = request.args.get('to_date','2030-01-01')

    if lemmatize!="false":
        o = text_processor.process_text(text, clear=True)
        text = o.get('lemmatized_text','')
    else:
        logging.warning('NOT lemmatized !!!!')

    search_result = elastic.search(text, skip=skip, limit=limit, field=field, timeout=timeout, from_date=from_date, to_date=to_date)
    return make_response(search_result)


# https://medium.com/@dkhd/handling-multiple-requests-on-flask-60208eacc154
if __name__ == '__main__':
    print("MAIN!!!!!  TEXT-PROCESSOR started.  ")
    # app.run(host= '0.0.0.0',  port=5000, debug=True) # threaded=True, processes=3
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)    