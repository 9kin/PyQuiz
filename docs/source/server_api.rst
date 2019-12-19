server_api
===========

**server_api** - клиент, написанный с использованием библиотеки `fastapi <https://github.com/tiangolo/fastapi>`_.

Для реализации удобного взаимодейтвия есть файл  ``api.py`` который  содержит PlayerAPI, HostAPI. Оеализованный с помощью запросов на сервер.

В данном файле 

.. code-block:: python3
	
	host_map = {} # словарь ключ которого pin
	empty_hosts = list([i for i in range(100001, 1000000)]) # свободные хосты


Пример ``hostmap`` при одной открытой игре и одном игроке подключенном к ней.

.. code-block:: json

	{
	  "100001": {
	    "key": "c14c536d2c09dbb59d279ec0cd4bffa20b2615db",
	    "last_active": "2019-12-19T22:02:03.591276",
	    "question_cnt": -1,
	    "peoples": {
	      "7b6e01d931302c93899756bb5f34e1c8fdc777a8": {
	        "score": 0,
	        "last_active": "2019-12-19T22:02:17.455739",
	        "name": "9kin",
	        "last": {
	          "ans": -1,
	          "res": false,
	          "add": 0
	        }
	      }
	    },
	    "quiz": {
	      "0": {
	        "answers": [
	          "3",
	          "4",
	          "5"
	        ],
	        "question": "2 + 2 = ?",
	        "score": 100,
	        "time": 10,
	        "true": 1
	      },
	      "1": {
	        "answers": [
	          "6",
	          "7"
	        ],
	        "question": "2 * 2 + 2 = ?",
	        "score": 100,
	        "time": 10,
	        "true": 0
	      }
	    }
	  }
	}


``key`` - код 20 знаков для подтверждения действий

``last_active`` - удобно для дебага

``question_cnt`` - текущий вопрос. (-1 ожидание игроков)

``peoples`` - Словарь подключенных людей.ключ ``key`` которыый даётся при подключенние к игре.

	
	``score`` - текущие очки (до этого вопроса)

	``last_active`` - удобно для дебага

	``name`` - имя

	``last`` - словарь последнего ответа

		``ans`` - ответ на последний вопрос (n/-1; -1 не ответил)

		``res`` - результат (True/False)

		``add`` - изменение рейтинга после окончание данного вопроса

``quiz`` - словарь с содержимом викторины

	``n`` - n вопрос 0,1,2,3....

		``answers`` - массив ответов

		``question`` - вопрос

		``score`` - max балл за этот вопрос

		``time`` - время на вопрос

		``true`` - правильный ответ индекс


В сервере на неправильные данные или если ошибка возвращается ``HTTPException(status_code=404, detail="error")``

host
"""""

.. function::  @app.get("/status") 
	
	:game_id: (int) pin игры

	:key: (str) ключ хоста

	Возвращает все данные игры с номером ``game_id``

.. function:: @app.get("/host")
	
	:quiz: (str) json объект который в примере находитса в ``quiz``

	возвращает ``pin`` и ``host_key``

.. function:: @app.get("/{game_id}/play")
	
	:game_id: (int) pin игры

	:key: (str) ключ сервера

	запуск игры

.. function:: @app.get("/{game_id}/next")
	
	:game_id: (int) pin игры

	:key: (str) ключ сервера

	следующий вопрос



client
""""""""

.. function::  @app.get("/{game_id}/connect")

	:game_id: (int) pin  игры
	
	:name: (str) имя игрока

	возвращает:

		* если игры нет или она уже идёт ``game``
		 
		* если такое  имя уже используется ``name``

		* если всё нормально ``key``



.. function:: @app.get("/{game_id}/validate")
	
	:game_id: (int) pin  игры
	
	:key: (str) ключ игрока

	Ожидание ота=вета на последний вопрос используется sleep

.. function:: @app.get("/{game_id}/reply")
	
	:game_id: (int) pin  игры
	
	:key: (str) ключ игрока

	:ans: (int) индес ответа

	отвечает на текущий вопрос


.. function:: @app.get("/{game_id}/wait")

	:game_id: (int) pin  игры
	
	:key: (str) ключ игрока

	ожидание следующего вопроса/начала игры


.. function:: @app.get('/{game_id}/question_info')

	:game_id: (int) pin  игры
	
	:key: (str) ключ игрока

	возвращает количество ответов и время на  его решение


.. function:: @app.get('/{game_id}/game_info')

	:game_id: (int) pin  игры
	
	:key: (str) ключ игрока

	возвращает количество вопросов в игре

