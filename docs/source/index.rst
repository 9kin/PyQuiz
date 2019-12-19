PyQuiz
======

PyQuiz - система проведения онлайн-викторин, написанная на Python 3 с использованием библиотек `PyQt <https://riverbankcomputing.com/software/pyqt/intro>`_, `fastapi <https://github.com/tiangolo/fastapi>`_.

.. image:: https://readthedocs.org/projects/pyquiz2/badge/?version=latest
	target: https://pyquiz2.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Status

installation
"""""""""""""

``pip3 install -r requirements.txt``


run server
""""""""""""

``uvicorn server_api:app``

doc
""""

`server_api.py <server_api.html>`_

Класс `Player <player.html>`_

Класс `Host <host.html>`_.

.. class:: CreateQuizWindow():

	Окно создание вопроса поддерживает: 

	* Изменение количества блоков, воросов, ответов.

	* Выбор правильного ответа.

	* Ограничение по времени и баллам на блок

	Использует: ``QPushButton``, ``QLineEdit``, ``QLabel``, ``QListWidget``, ``QVBoxLayout``, ``QHBoxLayout``

.. class:: QuizSelectionWindow():
 
 	Окно выбора игры и создания новой викторины. 

 	Использует: ``QPushButton``, ``QListWidget``, ``QVBoxLayout``, ``QHBoxLayout``.

    .. function:: play()
	   	
	   	Запускает выбранную викторину

	.. function:: exit()

		Открытие ``StartWindow``
	     
	.. function:: create_new_game()

	    Открытие ``CreateQuizWindow()``

.. class:: StartWindow():
	
	Стартовое окно.

	Использует: `QPushButton`
        
	.. function:: open_settings(self):
	    
	    Диалог настроек ``QInputDialog`` (настройка url).
	    
	.. function:: open_help():

	    Открывает `HelpWindow()`
	    
	.. function::  start_game():
	    
	    Открывает PlayerGameWindow()
	        
	.. function:: create_game()
	  		
	    открывает QuizSelectionWindow()
  

.. class:: HelpWindow():

    Класс в котороый описывает что такое данная программа. Использует ``QHBoxLayout``, ``QPixmap``, ``Label``, ``QPushButton``, ``QVBoxLayout``.

    Открывает браузер ``webbrowser.open('https://github.com/9kin/PyQuiz')``
