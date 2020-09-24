import logging
import socket
from collections import defaultdict
import json
import re
from bs4 import BeautifulSoup
import time

def strip(html):
    h = re.sub(r'<','\n<',html)
    return BeautifulSoup(h,features="html.parser").get_text()   

stop_words = { 'и', 'в', 'не', 'на', 'я', 'с', 'он', 'что', 'а', 'это', 'этот', 'по', 'к', 'но', 
'они', 'мы', 'она', 'как', 'то', 'который', 'из', 'у', 'свой', 'вы', 'весь', 'за', 'для', 'от', 'так', 
'ты', 'о', 'что', 'же', 'такой', 'тот', 'или', 'если', 'только', 'его', 'один', 'бы', 'себя', 'другой', 
'когда', 'до', 'мой', 'наш', 'чтобы', 'самый', 'вот', 'кто', 'при', 'сам', 'даже', 'их', 'какой', 'со', 
'там', 'после', 'ли', 'где', 'её', 'под', 'каждый', 'без', 'ну', 'просто', 'чем', 'ваш', 'здесь', 'потом', 
'да', 'ничто', 'сейчас', 'через', 'теперь', 'ни', 'тогда', 'тут', 'тоже', 'также', 'всегда', 'между', 
'хотя', 'перед', 'лишь', 'именно', 'поэтому', 'почему', 'любой', 'однако', 'никто', 'над', 'некоторый', 
'многие', 'всё', 'твой', 'пока', 'что-то', 'ведь', 'никогда', 'никакой', 'оно', 'про', 'кроме', 'всякий', 
'данный', 'иной', 'куда', 'против', 'среди', 'поскольку', 'из-за', 'около', 'либо', 'сей', 'зачем', 
'остальной', 'туда', 'пусть', 'какой-то', 'всё-таки', 'как-то', 'хоть', 'причём', 'словно', 'лучше', 
'кто-то', 'вместо', 'ибо', 'сюда', 'всего', 'разве', 'вокруг', 'столь', 'откуда', 'иначе', 'пожалуйста', 
'будто', 'некий', 'прежде', 'спасибо', 'никак', 'благодаря', 'многое', 'где-то', 'ради', 'зато', 'вроде', 
'чего', 'что-нибудь', 'ладно', 'прочий', 'нечто', 'сквозь', 'согласно', 'отсюда', 'возле', 'чей', 'внутри', 
'почему-то', 'спустя', 'неужели', 'таков', 'мимо', 'нечего', 'оттуда', 'вне', 'когда-то', 'каков', 'вдоль', 
'везде', 'таковой', 'включая', 'помимо', 'давай', 'насчёт', 'из-под', 'какой-нибудь', 'куда-то', 'вон', 
'угодно', 'никуда', 'кто-нибудь', 'когда-нибудь', 'нигде', 'по-другому', 'плюс', 'что-либо', 'якобы', 
'где-нибудь', 'вследствие', 'всюду', 'нисколько', 'ах', 'ниже', 'себе', 'ой', 'увы', 'ура', 'поверх', 
'стоп', 'вблизи', 'поперёк' }
# --------------------------------------------------------------------------
from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    PER,
    NamesExtractor,
    DatesExtractor,
    MoneyExtractor,
    AddrExtractor,

    Doc
)

segmenter = Segmenter()
morph_vocab = MorphVocab()

emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
syntax_parser = NewsSyntaxParser(emb)
ner_tagger = NewsNERTagger(emb)

# names_extractor = NamesExtractor(morph_vocab)
# dates_extractor = DatesExtractor(morph_vocab)
# money_extractor = MoneyExtractor(morph_vocab)
# addr_extractor = AddrExtractor(morph_vocab)
# ------------------------------------------------------------------------------------------
def get_doc(text):
    "Порождает предобработанный документ из данного текта"
    doc = Doc(text)
    # Делим на токены и предложения     
    doc.segment(segmenter)
    # Морфологический анализ токенов. Определяем часть речи (pos), одушевленность, падеж, род, число (feats)
    doc.tag_morph(morph_tagger)
    # Синаксический разбор. id, head_id, rel. Спецификация: https://universaldependencies.org/
    # Внимание: Без этого этапа нормализация названий сущностей иногда выполняется неправильно.
    doc.parse_syntax(syntax_parser) 
    return doc

def lemmatize_doc(doc):
    "Лематизирует токены документа"
    for token in doc.tokens:
        token.lemmatize(morph_vocab)    

def get_lemmatized_cleared_text(doc):
    "Возвращает лематизированный и очищенный от предлогов и других частиц текст"
    lm = [token.lemma for token in doc.tokens if token.lemma not in stop_words ]
    # print(f'Удалено {len(doc.tokens)-len(lm)} из {len(doc.tokens)} лем')
    return " ".join(lm), len(doc.tokens), len(lm)

def get_lemmatized_text(doc):
    "Возвращает лематизированный текст из документа"
    lm = [token.lemma for token in doc.tokens]
    return " ".join(lm), len(doc.tokens), len(doc.tokens)

def stringify(obj):
    return json.dumps(obj, indent=2,  ensure_ascii=False).encode('utf8').decode()



def get_entities_dict(doc):
    return {  sp.normal: sp.type  for sp in doc.spans}

def get_entities_list(doc):
    return [{'type':sp.type, 
            #'name': doc.text[sp.start:sp.stop], 
            'name':sp.normal} for sp in doc.spans]

def get_entities_agg_list(doc):
    dd = defaultdict(lambda: {'type':'', 'count':0})
    for sp in doc.spans:
        dd[sp.normal]['type'] = sp.type
        dd[sp.normal]['counter'] += 1
    
    lis = [ {'name':k, 'type':v['type'], 'count':v['count']} for k,v in dd.items() ]
    return lis

def get_entities_grouped_by_type(doc):
    dd = defaultdict(lambda: {})
    for sp in doc.spans:
        dd[sp.type][sp.normal] = dd[sp.type].get(sp.normal, 0) + 1
    return dd



def get_entities(doc):
    "Возвращает нормализованные сущности из документа"
    doc.tag_ner(ner_tagger)
    
    for span in doc.spans:
        span.normalize(morph_vocab)

    entities = get_entities_grouped_by_type(doc)
    return entities


def process_text(html, clear=False):
    start = time.time()
    text = strip(html)
    lemmatized_text = None
    lem0 = None
    lem1 = None
    entities_grouped = None
    entities_list = None
    process_status = 'success'

    # try:
    doc = get_doc(text)
    lemmatize_doc(doc)
    if clear:
        lemmatized_text, lem0, lem1 = get_lemmatized_cleared_text(doc)
    else:
        lemmatized_text, lem0, lem1 = get_lemmatized_text(doc)
    entities_grouped = get_entities(doc)
    entities_list = get_entities_list(doc)
    # except Exception as ex:
    #     process_status  = "ERROR: " + str(ex)
    #     logging.warning(process_status)
    #     print(process_status)

    end = time.time()
    return {
        'entities_grouped': entities_grouped,
        'entities_list': entities_list,
        'cleared': clear,
        'lemm_num': lem0,
        'lemm_num_cleared': lem1,
        'lemmatized_text': lemmatized_text,
        'time': int((end-start)*1000)/1000,
        'host': socket.gethostname(),
        'process_status':'success1',
    }


def process_entities(html):
    start = time.time()
    text = strip(html)
    entities = None
    process_status = 'success'
    try:
        doc = get_doc(text)
        entities = get_entities(doc)

    except Exception as ex:
        process_status  = "ERROR: " + str(ex)
        logging.warning(process_status)
        print(process_status)

    end = time.time()
    return {
        'entities': entities,
        'time': int((end-start)*1000)/1000,
        'host': socket.gethostname(),
        'process_status': process_status
    }
