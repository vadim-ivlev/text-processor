# text-processor

Сервер для морфологического и синтаксического анализа текстов, лемматизации, 
нормализации выражений, выделения именованных сущностей.

Это часть проекта по построению рекомендательной системы RG.

-----------------------------------------


Код программ находится в директории deploy/

API
----
Защищено auth-proxy.


Требования к системе
---------

- docker
- python > 3.7.6
- go > 1.14.2
- pip install -r requirements.txt 

Чтобы не засорять компьютер лишними библиотеками, 
рекомендуется создать окружение питона и работать в нем.
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





Тест библиотек

      python tests/test-text-processor.py 


Тесты запросов к серверу

      tests/test-post.sh   
      python tests/test-post.py 

