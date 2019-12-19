.. py:module:: Host
.. py:currentmodule:: Host


.. class: HostThread()

    Поток для управления окном

.. function:: delete_all_windgets

        Удаляет все виджеты вызывая все функции:

        .. function:: delete_person_waiting_widgets()
        
        .. function:: delete_true_answer_widgets()
        
        .. function:: delete_raiting_widgets()
        
        .. function:: delete_question_widgets()


.. function:: raiting_window(raiting: List[Tuple[int, str]]):

    :raiting: ``List[Tuple[int, str]]``

    Отрисовка окна с рейтингом, используя ``QVBoxLayout`` и ``QTableWidget``.


.. function:: question_window(question, answer_array, time=10):
    
    :question: текст вопроса

    :answer_array: массив ответов 
    
    :time: время на вопрос

    Отрисовка окна с вопросом, используя ``QVBoxLayout`` и ``QTableWidget()`` и ``QProgressBar()`` и ``QBasicTimer()``.


.. function:: timerEvent(self, e):


    функция ``question_window`` ProgressBar после нужного времени меняет его на кнопку


.. function:: true_answer_window(question, answer, index):

    :question: вопрос

    :answer: правильный ответ

    :index: индекс правильного ответа

    Отрисовка окна с правильным вопросом, используя ``QVBoxLayout`` и ``QLabel()``.

.. code-block: python3

    def to_raiting(self):
        self.curent_window = self.raiting_window

    def to_question(self):
        self.curent_window = self.question_window

    def to_true_false(self):
        self.curent_window = self.true_answer_window

    def person_waiting_window(self, quiz_title, pin, peoples):
        QVBoxLayout()
        QTableWidget()
        
        Окно ожидание игроков. Показывает подключенных игроков.

    def play(self):
        if self.person_waiting_table.rowCount() < PLAYERS_NUM_MIN:
            showMsg('нет людей')
            return
        self.curent_window = self.question_window


.. function:: thread_signal()

    Подключени к серверу. Открытие потока `HostThread``. После завершения работы потока вызывается ``on_finished()``

.. function:: change_window()

    .. code-block:: python3

        def change_window(self, value):
            func = value[0]s
            arguments = value[1:]
            func(*arguments)

    :value: ``list [function, param1, param2, ..]``

    Запускает вункцию, нужна для управления из потока с помощью ``pyqtSignal(list)``

.. function:: on_finished()

    Функция, которая запускается после завершения работы потока. Вызывает ``exit()``


.. function:: exit()
    
    Открывает новое окно ``QuizSelectionWindow()`
