from flask import Flask, request
import simplejson as json
import text_processor
app = Flask(__name__)

def get_text():
    content = request.get_json(silent=True)
    return content['text']

def make_response(o):
    response_text = json.dumps(o, indent=2,  ensure_ascii=False)
    return response_text, 200, {'Content-Type': 'text/css; charset=utf-8'}

# ---------------------------------------------------
@app.route('/')
def hello_world():
    return 'TEXT-PROCESSOR'


@app.route('/lemmas-entities', methods=['POST'])
def text_entities():
    text = get_text()
    o = text_processor.process_text(text)
    return make_response(o)

@app.route('/clear-lemmas-entities', methods=['POST'])
def clear_text_entities():
    text = get_text()
    o = text_processor.process_text(text, clear=True)
    return make_response(o)

@app.route('/entities', methods=['POST'])
def entities():
    text = get_text()
    o = text_processor.process_entities(text)
    return make_response(o)


# https://medium.com/@dkhd/handling-multiple-requests-on-flask-60208eacc154
if __name__ == '__main__':
    print("MAIN!!!!!  TEXT-PROCESSOR started.  ")
    # app.run(host= '0.0.0.0',  port=5000, debug=False) # threaded=True, processes=3
    from waitress import serve
    serve(app, host="0.0.0.0", port=5000)    