# text-processor

<https://text-processor.rg.ru>

Сервер для морфологического и синтаксического анализа текстов, лемматизации, 
нормализации выражений, выделения именованных сущностей.


Часть проекта по построению рекомендательной системы RG.

-----------------------------------------



API
----

**Конечные точки**

- /lemmas-entities - возвращает лемматизированный текст и список сущностей 
- /clear-lemmas-entities - возвращает лемматизированный, очищенный от стоп-слов текст и список сущностей
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
            "PER": {              // Персоны
                  "Голубев": 4,   // 4 - количество вхождений в текст
                  "Путин": 3,
                  "Владимир Путин": 1,
                  "Александр Лукашенко": 2
            },
            "LOC": {             // Места
                  "Ростовская область": 3,
                  "Республика  Беларусь": 1,
                  "Кремль": 1
            }
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


Билд сервера

      docker-compose -f deploy/docker-compose.yml build  

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
      go run tests/*.go  

Код 
----

находится в директории deploy/


Замечания
---------

Похоже библиотеки обработки текстов используют все доступные процессоры.
Поэтому никакие ухищрения по распараллеливанию операций, 
например организация нескольких реплик серверов не приводит к значимым результатам.
Похоже даже параллельные запросы становятся в очередь.
Максимум чего удалось добиться путём организации четырёх реплик и балансера нагрузки 
в docker-compose, это снижение времени исполнения запроса с 0.28 до 0.18 секунды 
на локальном компьютере с четырьмя процессорами.


Запуск программы
------------

Go to deploy/ directory.

**To start web app with API in docker:**
      
      docker-compose up

open http://localhost:9555

To start without docker

      python server.py

open http://localhost:5000

**To begin processing articles**

      docker-compose -f docker-compose-worker.yml up

or 

      python process_articles.py

To build the image and upload it to docker hub :

      ./build-worker-image.sh

## Notes

Sometimes process_articles.py crushes because of lack of memory. This happens when processed text is big.
Then docker restarts the container and process_articles.py continues leaving several records in the database unprocessed with 
process_status = 'processing'.




