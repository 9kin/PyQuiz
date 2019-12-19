.. py:module:: PlayerGameWindow
.. py:currentmodule:: PlayerGameWindow

:py:mod:`PlayerGameWindow` Module
======================


Класс :py:mod:`~PlayerGameWindow` включает в себя отрисовку окон игрока таких как:

* Подключение

* Ответ (кнопки разного цвета)

* Результат (правильно/неправильно, рейтинг и место игрока)

* Ожидание



.. function:: delete_all_windgets()

    Удляет все виджеты вызывая все функции:

        .. function:: delete_answer_windgets()

            Удаляет все виджеты окна с ответами

        .. function:: delete_waiting_wingets()

            Удаляет все виджеты окна ожидания

        .. function:: delete_true_false_wingets()

            Удаляет все виджеты окна с результатом


        .. function:: delete_connect_windgets()

            Удляет все виджеты окна подключения



.. function:: answer_window()
    
    Отрисовка окна ответа (кнопки разного цвета), используя ``QPushButton``.


.. function:: waiting_window()
    
    Отрисовка ожидания, используя ``QVBoxLayout`` и ``QLabel``.

.. function:: true_false_window()
    
    Отрисовка Результата (правильно/неправильно, рейтинг и место игрока), используя ``QVBoxLayout`` и ``QLabel``.


.. function:: connect_window()
    
    Отрисовка Результата (правильно/неправильно, рейтинг и место игрока), используя ``QVBoxLayout`` и ``QPushButton`` и ``QLineEdit``


.. function:: game_end()

    Открывает новое окно ``StartWindow``


.. function:: thread_signal(game, name)

    :game: pin игры 6 значный

    :name: имя игрока

    Подключени к серверу. Открытие потока ``PlayerThread``. После завершения работы потока вызывается ``on_finished()``

.. function:: change_window()

    .. code-block:: python3

        def change_window(self, value):
            func = value[0]s
            arguments = value[1:]
            func(*arguments)

    :value: ``list [function, param1, param2, ..]``

    Запускает вункцию, нужна для управления из потока с помощью ``pyqtSignal(list)``

.. function:: on_finished()

    Функция, которая запускается после завершения работы потока. Вызывает ``connect_window()``

.. function:: click()

    .. code-block:: python3

        def click(self):
            i = int(self.sender().objectName())
            self.waiting_window()
            self.API.ans(i)

    Запускается при нажатие кнопки ответа

.. function:: connect()
    
    Запускает ``self.thread_signal(game, name)`` ``game`` и ``name`` взятые из окна ``connect_window``
        

.. function:: exit()
    
    Открывает новое окно ``StartWindow``


.. class:: PlayerThread()

    .. code-block:: python3

        class PlayerThread(QThread):
            Signal = pyqtSignal(list)

            def __init__(self, game, name, window):
                super().__init__()
                self.window = window
                self.game = game
                self.name = name


            def run(self):
                self.window.API = api.PlayerAPI(URL, self.game, self.name)
                if self.window.API.hash_error():
                    self.window.error = self.window.API.error
                    return
                self.Signal.emit([self.window.waiting_window])

                self.window.API.wait()
                question_cnt = self.window.API.game_info()
                for i in range(question_cnt):
                    info = self.window.API.question_info()
                    self.Signal.emit([self.window.answer_window, info[0]])
                    QtTest.QTest.qWait(info[1] * 1000)
                    res = self.window.API.validate()
                    self.Signal.emit([self.window.true_false_window, res["valid"], res["place"], res['score']])
                    if i + 1 != question_cnt:
                        self.window.API.wait()
                QtTest.QTest.qWait(2000) # 2 s