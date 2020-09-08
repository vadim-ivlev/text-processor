#coding=utf-8
"""
Тест выполняет несколько последовательных запросов к серверу, 
а затем несколько параллельных запросов. 
Показывается время исполнения каждой серии.
"""


import requests
import json
import time
import asyncio
import timeit

# API Конечная точка
url = 'http://localhost:9555/process/lemmas-entities' # local test
# url = 'http://localhost:5000/lemmas-entities' # local direct  to flask
# url = 'https://text-processor.rg.ru/process/process'  # deploy server

# Данные для посылки на сервер.
data = {
    "text": "\n<p>Глава государства начал встречу сразу с проблемных вопросов: в регионе сокращается сельхозпроизводство \nна фоне солидного роста по стране. Голубев выразил надежду, что в этом году тенденцию удастся переломить. \nПрезидент заметил: если необходима поддержка, то нужно сформулировать просьбы. \"И по стройке: сокращаются \nи объемы строительства. Здесь что?\" - уточнил он. Собеседник рассказал о заметном сокращении индивидуального \nжилищного строительства. В целом строительная программа \"плюсует\", но жилье \"минусует\", признал Голубев. \n\"Поэтому это стало нашим приоритетом\", - заверил региональный лидер.</p><p>\"Вы человек очень опытный, знаете, \nмы последнее время, последние годы большое внимание обращаем на проблемы демографии\", - заметил Путин. \nПо его словам, после определенного подъема у нас сейчас наблюдается сокращение численности постоянного населения. \n\"Но в Ростовской области, несмотря на то, что это южный, благоприятный климатически регион, \nсокращение происходит даже в большем объеме, чем в среднем по стране\", - сказал президент и назвал возможные \nпричины: недостаточное количество врачей и мест в детсадах. \"Это очень важный фактор для того, чтобы люди себя \nчувствовали уверенно и комфортно\", - объяснил глава государства.</p><p>Важен и такой показатель, как уровень \nбезработицы. \"Ясно, что это сегодня одна из главных проблем в стране, это совершенно очевидно\", - заметил Путин. \nНо Ростовская область развита и в промышленном отношении, и в отношении возможностей для сельского хозяйства. \n\"Конечно, нужно обратить внимание на рынок труда\", - указал президент.</p><p>\"У нас действительно \"выскочила\" \nреально безработица - 96 с лишним тысяч человек (4,6 процента) при том, что до определенного времени уровень \nбезработицы был не выше или на уровне среднероссийского, - признал губернатор. - Мы предпринимаем сейчас меры \nдля того, чтобы максимально запустить те механизмы, которые позволяют людям работать\". \"Мы будем искать \nновые решения. Я думаю, что для нас это важнейшая задача, усилия будем прилагать для того, чтобы здесь ситуацию \nпереломить\", - заверил он.</p><div class=\"incut\">В Ростовской области минимальная долговая нагрузка, низкий \nуровень аварийного жилья и очень хорошие перспективы с точки зрения инвестпроектов&nbsp;</div><p>Глава государства \nтакже заявил, что опережающий темп роста промышленного производства - заслуга самого Голубева и его команды. \nЗа первое полугодие, конечно, есть спад, но он меньше, чем по стране. В нормальном состоянии и региональные финансы, \nв области минимальная долговая нагрузка, низкий уровень аварийного жилья и очень хорошие перспективы с точки \nзрения инвестпроектов, оценил Путин. Президент призвал поддержать усилия бизнеса по созданию новых, хорошо \nоплачиваемых, качественных и современных высокотехнологичных рабочих мест. Голубев также сообщил, что \nселяне прекрасно сработали по уборке ранних зерновых, и президент одобрил предложение наградить их.</p><div \nclass=\"Section\">Между тем</div><p>Состоялся телефонный разговор Владимира Путина с президентом Республики \nБеларусь Александром Лукашенко, сообщили в пресс-службе Кремля. Александр Лукашенко проинформировал о предпринимаемых \nмерах в целях нормализации обстановки в стране. Затрагивалась также тематика двустороннего сотрудничества в вопросах \nпротиводействия коронавирусной инфекции.</p>\n"
}

# Количество запросов  в серии.
N = 100

responses = []

# Делаем один запрос.
def request(i,data):
    print(f'{i} req started')
    r = requests.post(url, json=data)
    j = r.json()
    s = json.dumps(j, indent=2, ensure_ascii=False)
    # summary = f'{i} host={j["host"]} time={j["time"]:.2} len={len(s)}'
    summary = f'{i} req finished. {j.get("host","")} {j.get("time",-1):.2} sec. {len(s)} bytes.'
    print(summary)
    return summary
    

# Делаем последовательные запросы.
def make_sequential_requests(N): 
    global responses  
    responses = [request(i,data) for i in range(N)]
    return responses


# Делаем параллельные запросы.
async def make_concurrent_requests(N):
    loop = asyncio.get_event_loop()
    futures = [loop.run_in_executor(None, request, i, data) for i in range(N)]
    responses = [await f for f in futures]
    return responses
    
# Начинаем серию параллельных запросов.
def start_make_concurrent_requests(N):
    global responses
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(make_concurrent_requests(N))

# ----------------------------------------------------

# Код основной программы.


# t = timeit.timeit(lambda: make_sequential_requests(N), number=1)
# print(f'{N} Последовательных запросов закончены за {t:.3} sec. Среднее время на запрос {t/N:.3} sec.')

t = timeit.timeit(lambda: start_make_concurrent_requests(N), number=1)
print(f'{N} Параллельных запросов закончены за {t:.3} sec. Среднее время на запрос {t/N:.3} sec.')

s = json.dumps(responses, indent=2, ensure_ascii=False)
# print(s)
