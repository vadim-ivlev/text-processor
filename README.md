# text-processor

<https://text-processor.rg.ru>

Сервер для морфологического и синтаксического анализа текстов, лемматизации, 
нормализации выражений, выделения именованных сущностей.


Часть проекта по построению рекомендательной системы RG.

-----------------------------------------



API
----

**Конечные точки**

- /text-entities - возвращает лемматизированный текст и список сущностей 
- /clear-text-entities - возвращает лемматизированный, очищенный от стоп-слов текст и список сущностей
- /entities - возвращает список сущностей


**Запрос:**
```
POST

Content-Type: application/json

data='
{
    "text": "\n<p>Глава государства ..."
}
'
```

Текст может содержать HTML разметку.

**Ответ:**

```json
{
      "lemmatized_text": "глава государство  ...", // лемматизированный текст
      "cleared": true|false,      // очищен ли текст
      "entities": {               // Список  сущностей сгруппированный по типам
      },
      "time": 0.17,               // время в секундах, которое занял анализ текста
      "lemm_num": 524,            // Количество лемм в тексте
      "lemm_num_cleared": 396,    // Количество лемм после очистки
      "host": "text-processor-1", // Имя хоста обработавшего текст
}

```


Требования к системе
---------

- docker
- python > 3.7.6
- go > 1.14.2
- pip install -r requirements.txt 

Чтобы не засорять компьютер лишними библиотеками, 
рекомендуется создать python environment и работать в нем.
Например если на компьютере установлена anaconda можно выполнить команды:

      conda create -n text_processor python=3.7.6  
      conda deactivate 
      conda activate text_processor
      pip install -r requirements.txt 


Команды
--------
Выполняются из корневой директории.


Старт сервера

      docker-compose -f deploy/docker-compose.yml up -d  

Останов сервера
   
      docker-compose -f deploy/docker-compose.yml down  

Старт записных книжек

      docker-compose up -d

Останов записных книжек

      docker-compose down

или с помощью скриптов в директории sh/ .



Тест библиотек

      python tests/test-text-processor.py 


Тесты запросов к серверу

      tests/test-post.sh   
      python tests/test-post.py 

Код 
----

находится в директории deploy/

