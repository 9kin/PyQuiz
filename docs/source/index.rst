PyQuiz
======

PyQuiz - система проведения онлайн-викторин, написанная на Python 3 с использованием библиотек `PyQt <https://riverbankcomputing.com/software/pyqt/intro>`_, `fastapi <https://github.com/tiangolo/fastapi>`_.

PLS: ``pip3 install uvicorn, fastapi, PyQt5``

run server: ``uvicorn server_api:app`` ``http://127.0.0.1:8000``

Класс `Player <player.html>`_

Класс `Host <host.html>`_.

.. class:: CreateQuizWindow():

	Окно создание вопроса поддержвает: 

	1. Изминение кол блоков

	2. Изминение кол воросов

	3. Изминение кол ответов

	4. Выюор правильного ответа

	5. Ограничение по времени и баламм на блок

	Использует:

	* ``QPushButton``
	* ``QLineEdit``
	* ``QLabel``
	* ``QListWidget``
	* ``QVBoxLayout``
	* ``QHBoxLayout``

.. class:: QuizSelectionWindow():
 
 	Окно выбора для игры и создания викторины. Использует ``QPushButton``, ``QListWidget``, ``QVBoxLayout``, ``QHBoxLayout``.

    .. function:: play()
	   	
	   	Запускает выбранную викторину

	.. function:: exit()

		Открытие ``StartWindow``
	     
	.. function:: create_new_game()

	    Открытие ``CreateQuizWindow()``

.. class:: StartWindow():
	
	Стартовое окно используя `QPushButton`
        
	.. function:: open_settings(self):
	    
	    Диалог настроек ``QInputDialog``.
	    
	.. function:: open_help():

	    Открывает `HelpWindow()`
	    
	.. function::  start_game():
	    
	    Открывает PlayerGameWindow()
	        
	.. function:: create_game()
	  		
	    открывает QuizSelectionWindow()
  

.. class:: HelpWindow():

    Класс в котороый описывает что тоакое данная программа. Использует ``QHBoxLayout``, ``QPixmap``, ``Label``, ``QPushButton``, ``QVBoxLayout``.

    Открывает браузер ``webbrowser.open('https://github.com/9kin/PyQuiz')``
