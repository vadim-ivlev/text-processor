sample_text = """
<p>Глава государства начал встречу сразу с проблемных вопросов: в регионе сокращается сельхозпроизводство 
на фоне солидного роста по стране. Голубев выразил надежду, что в этом году тенденцию удастся переломить. 
Президент заметил: если необходима поддержка, то нужно сформулировать просьбы. "И по стройке: сокращаются 
и объемы строительства. Здесь что?" - уточнил он. Собеседник рассказал о заметном сокращении индивидуального 
жилищного строительства. В целом строительная программа "плюсует", но жилье "минусует", признал Голубев. 
"Поэтому это стало нашим приоритетом", - заверил региональный лидер.</p><p>"Вы человек очень опытный, знаете, 
мы последнее время, последние годы большое внимание обращаем на проблемы демографии", - заметил Путин. 
По его словам, после определенного подъема у нас сейчас наблюдается сокращение численности постоянного населения. 
"Но в Ростовской области, несмотря на то, что это южный, благоприятный климатически регион, 
сокращение происходит даже в большем объеме, чем в среднем по стране", - сказал президент и назвал возможные 
причины: недостаточное количество врачей и мест в детсадах. "Это очень важный фактор для того, чтобы люди себя 
чувствовали уверенно и комфортно", - объяснил глава государства.</p><p>Важен и такой показатель, как уровень 
безработицы. "Ясно, что это сегодня одна из главных проблем в стране, это совершенно очевидно", - заметил Путин. 
Но Ростовская область развита и в промышленном отношении, и в отношении возможностей для сельского хозяйства. 
"Конечно, нужно обратить внимание на рынок труда", - указал президент.</p><p>"У нас действительно "выскочила" 
реально безработица - 96 с лишним тысяч человек (4,6 процента) при том, что до определенного времени уровень 
безработицы был не выше или на уровне среднероссийского, - признал губернатор. - Мы предпринимаем сейчас меры 
для того, чтобы максимально запустить те механизмы, которые позволяют людям работать". "Мы будем искать 
новые решения. Я думаю, что для нас это важнейшая задача, усилия будем прилагать для того, чтобы здесь ситуацию 
переломить", - заверил он.</p><div class="incut">В Ростовской области минимальная долговая нагрузка, низкий 
уровень аварийного жилья и очень хорошие перспективы с точки зрения инвестпроектов&nbsp;</div><p>Глава государства 
также заявил, что опережающий темп роста промышленного производства - заслуга самого Голубева и его команды. 
За первое полугодие, конечно, есть спад, но он меньше, чем по стране. В нормальном состоянии и региональные финансы, 
в области минимальная долговая нагрузка, низкий уровень аварийного жилья и очень хорошие перспективы с точки 
зрения инвестпроектов, оценил Путин. Президент призвал поддержать усилия бизнеса по созданию новых, хорошо 
оплачиваемых, качественных и современных высокотехнологичных рабочих мест. Голубев также сообщил, что 
селяне прекрасно сработали по уборке ранних зерновых, и президент одобрил предложение наградить их.</p><div 
class="Section">Между тем</div><p>Состоялся телефонный разговор Владимира Путина с президентом Республики 
Беларусь Александром Лукашенко, сообщили в пресс-службе Кремля. Александр Лукашенко проинформировал о предпринимаемых 
мерах в целях нормализации обстановки в стране. Затрагивалась также тематика двустороннего сотрудничества в вопросах 
противодействия коронавирусной инфекции.</p>
"""


import os, sys
sys.path.insert(1, os.path.dirname(sys.path[0])) 

from deploy import text_processor
import simplejson as json

o = text_processor.process_text(sample_text)
print(json.dumps(o,indent=2, ensure_ascii=False))