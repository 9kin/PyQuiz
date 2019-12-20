import api
import json
import sys
import os
import webbrowser
import secrets
from constants import *

from typing import List, Tuple

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import (Qt, QTime, QTimer, QBasicTimer,
                          QSize, QThread, pyqtSlot)
from PyQt5.QtGui import QIcon
from PyQt5.Qt import QEventLoop
from PyQt5 import QtTest
from PyQt5.QtCore import QThread, pyqtSignal

from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QLabel, QLineEdit, QTableWidget, QInputDialog,
                             QTableWidgetItem, QProgressBar, QVBoxLayout, QDialog,
                             QSpinBox, QHBoxLayout, QGridLayout, QFileDialog,
                             QListWidget, QMessageBox)

import sip

COORDS = [200, 200]

URL = 'http://127.0.0.1:8000'


def showMsg(s, type=QMessageBox.Critical):
    msg = QMessageBox()
    msg.setIcon(type)
    msg.setText(s)
    msg.setWindowTitle('pyQuiz')
    msg.exec_()


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
            self.Signal.emit([self.window.true_false_window,
                              res['valid'],
                              res['place'],
                              res['score']])
            if i + 1 != question_cnt:
                self.window.API.wait()
        QtTest.QTest.qWait(2000)  # 2 s


class PlayerGameWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.move(*COORDS)
        self.setWindowTitle('pyQuiz')
        self.error = ''
        self.API = None
        self.answer = None
        self.cur_answer = 0
        self.waiting_window_box = None
        self.connect_window_box = None
        self.setWindowTitle('pyQuiz')
        self.connect_window_connect, self.connect_window_name = None, None
        self.connect_window_pin = None
        self.connect_window_exit, self.connect_window_connect = None, None
        self.connect_window_status = None
        self.buttons = []
        self.vbox = None
        self.waiting_window_title = None
        self.true_false_vbox = None
        self.true_false_label, self.true_false_statistic = None, None

        self.table = None
        self.setStyleSheet(
            QUIZ_STYLE_SHEET)
        self.setFixedSize(300, 300)

        self.connect_window()

    def delete_answer_windgets(self):
        for button in self.buttons:
            button.deleteLater()
            button = None
        self.buttons = []

    def delete_waiting_wingets(self):
        # https://stackoverflow.com/questions/5899826/pyqt-how-to-remove-a-widget
        if self.waiting_window_box is not None:
            sip.delete(self.waiting_window_box)
            self.waiting_window_box = None
        if self.waiting_window_title is not None:
            self.waiting_window_title.deleteLater()
            self.waiting_window_title = None

    def delete_true_false_wingets(self):
        if self.true_false_vbox is not None:
            sip.delete(self.true_false_vbox)
            self.true_false_vbox = None
        if self.true_false_label is not None:
            self.true_false_label.deleteLater()
            self.true_false_label = None
        if self.true_false_statistic is not None:
            self.true_false_statistic.deleteLater()
            self.true_false_statistic = None

    def delete_connect_windgets(self):
        if self.connect_window_box is not None:
            sip.delete(self.connect_window_box)
            self.connect_window_box = None
        if self.connect_window_pin is not None:
            self.connect_window_pin.deleteLater()
            self.connect_window_pin = None
        if self.connect_window_name is not None:
            self.connect_window_name.deleteLater()
            self.connect_window_name = None
        if self.connect_window_connect is not None:
            self.connect_window_connect.deleteLater()
            self.connect_window_connect = None
        if self.connect_window_exit is not None:
            self.connect_window_exit.deleteLater()
            self.connect_window_exit = None
        if self.connect_window_status is not None:
            self.connect_window_status.deleteLater()
            self.connect_window_status = None

    def delete_all_windgets(self):
        self.delete_connect_windgets()
        self.delete_answer_windgets()
        self.delete_waiting_wingets()
        self.delete_true_false_wingets()

    def answer_window(self, cnt=2):
        self.delete_all_windgets()
        cur = OPTIONS_BUTTONS_MAP[cnt]
        for i in range(len(cur)):
            cords = cur[i]
            button = QPushButton(self)
            button.move(cords[0], cords[1])
            button.resize(cords[2], cords[3])
            button.setStyleSheet('QPushButton {background-color: ' +
                                 OPTIONS_BUTTONS_COLOR[i] + '; color: #BBBBBB;}')
            button.setObjectName(str(i))
            button.clicked.connect(self.click)
            button.show()
            self.buttons.append(button)
        self.setFixedSize(300, 300)

    def waiting_window(self):
        self.delete_all_windgets()

        self.waiting_window_box = QVBoxLayout()
        self.waiting_window_title = QLabel(self)
        self.waiting_window_title.resize(300, 100)
        self.waiting_window_title.setText('Ожидание')
        self.waiting_window_title.setStyleSheet(
            'QLabel {font-size: 50px;font-weight: bold;background-color: #3C3F41;color: #BBBBBB;}')
        self.waiting_window_title.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.waiting_window_box.addWidget(self.waiting_window_title)
        self.setLayout(self.waiting_window_box)
        self.setFixedSize(300, 300)

    def true_false_window(self, flag, place, points):
        self.delete_all_windgets()
        self.true_false_vbox = QVBoxLayout()
        self.true_false_label = QLabel()
        self.true_false_label.setText('Правильно' if flag else 'Неправильно')
        self.true_false_label.setStyleSheet(
            'QLabel {font-size: 40px; font-weight: bold; background-color: #3C3F41; color: ' + (
                'green}' if flag else 'red}'))
        self.true_false_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.true_false_statistic = QLabel()
        self.true_false_statistic.setText(f'{points} очков, {place} место')
        self.true_false_statistic.setStyleSheet(
            'QLabel{font-size: 20px;font-weight:bold;background-color: #3C3F41;color:#BBBBBB;}')
        self.true_false_statistic.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.true_false_vbox.addWidget(self.true_false_label)
        self.true_false_vbox.addWidget(self.true_false_statistic)

        self.setLayout(self.true_false_vbox)
        self.setFixedSize(300, 300)

    def connect_window(self):
        self.delete_all_windgets()
        self.connect_window_box = QVBoxLayout()
        self.connect_window_box.setContentsMargins(0, 0, 0, 0)

        self.connect_window_pin = QLineEdit()
        self.connect_window_pin.setPlaceholderText('ID игры')
        self.connect_window_pin.setStyleSheet(
            'QLineEdit {font-size: 40px;background-color: #3C3F41; color: #BBBBBB;}'
        )

        self.connect_window_name = QLineEdit()
        self.connect_window_name.setPlaceholderText('Ваше имя')
        self.connect_window_name.setText(load_config()[CONFIG_OPTION_NAME])
        self.connect_window_name.setStyleSheet(
            """QLineEdit {font-size: 40px; background-color: #3C3F41; color: #BBBBBB;}""")

        self.connect_window_connect = QPushButton()
        self.connect_window_connect.setText('подключиться')
        self.connect_window_connect.setStyleSheet(
            'QPushButton{font-size:40px;text-align:center;background-color:#3C3F41;color:#BBBBBB;}')
        self.connect_window_connect.clicked.connect(self.connect)

        self.connect_window_exit = QPushButton()
        self.connect_window_exit.clicked.connect(self.exit)
        self.connect_window_exit.setText('Назад')
        self.connect_window_exit.setStyleSheet(
            'QPushButton{font-size:30px;text-align:center;background-color:#3C3F41;color:#BBBBBB;}')

        self.connect_window_status = QLabel(self.error)
        self.connect_window_status.setStyleSheet('QLabel {color: red; font-size: 14px;}')
        self.connect_window_status.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.connect_window_pin.setFixedHeight(100)
        self.connect_window_name.setFixedHeight(100)
        self.connect_window_connect.setFixedHeight(100)
        self.connect_window_exit.setFixedHeight(50)
        self.connect_window_status.setFixedHeight(35)

        self.connect_window_box.addWidget(self.connect_window_pin)
        self.connect_window_box.addWidget(self.connect_window_name)
        self.connect_window_box.addWidget(self.connect_window_connect)
        self.connect_window_box.addWidget(self.connect_window_exit)
        self.connect_window_box.addWidget(self.connect_window_status)
        self.setLayout(self.connect_window_box)
        self.setFixedSize(300, 385)

    def game_end(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.start_window = StartWindow()
        self.start_window.show()
        self.close()

    def thread_signal(self, game, name):
        self.thread = PlayerThread(game, name, self)
        self.thread.Signal.connect(self.change_window)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def change_window(self, value):
        func = value[0]
        arguments = value[1:]
        func(*arguments)

    def on_finished(self):
        self.thread.Signal.disconnect(self.change_window)
        self.thread.finished.disconnect(self.on_finished)
        self.connect_window()

    def click(self):
        i = int(self.sender().objectName())
        self.waiting_window()
        self.API.ans(i)

    def connect(self):
        game = self.connect_window_pin.text()
        name = self.connect_window_name.text()
        if not game.isnumeric():
            showMsg('Неправильный ID игры')
            return
        game = int(game)
        self.thread_signal(game, name)

    def exit(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.start_window = StartWindow()
        self.start_window.show()
        self.close()


class HostThread(QThread):
    Signal = pyqtSignal(list)

    def __init__(self, host, window):
        super().__init__()
        self.host, self.window = host, window

    def run(self):
        self.window.API = api.HostAPI(self.host, self.window.quiz)
        id_ = str(self.window.API.id)
        self.window.curent_window = self.window.person_waiting_window
        while self.window.curent_window == self.window.person_waiting_window:
            self.Signal.emit([self.window.person_waiting_window,
                              self.window.name,
                              id_,
                              self.window.API.get_peoples()])
            c = 0
            while c < 20 and self.window.curent_window == self.window.person_waiting_window:
                QtTest.QTest.qWait(50)  # 2 s
                c += 1

        res = self.window.API.get_info()
        cnt = len(res['quiz'])
        self.window.API.play()
        cur = 0
        for i in range(cnt):
            curent_question = res['quiz'][str(cur)]
            self.Signal.emit([self.window.question_window,
                              curent_question['question'],
                              curent_question['answers'],
                              curent_question['time']]
                             )
            while self.window.curent_window == self.window.question_window:
                pass
            self.Signal.emit([self.window.true_answer_window,
                              curent_question['question'],
                              curent_question['answers'][curent_question['true']],
                              curent_question['true']]
                             )
            while self.window.curent_window == self.window.true_answer_window:
                pass
            self.Signal.emit([self.window.raiting_window, self.window.API.get_raiting()])
            while self.window.curent_window == self.window.raiting_window:
                pass
            cur += 1
            self.window.API.next()


# raiting question answer person_waiting
class Host(QWidget):

    def __init__(self, quiz):
        super().__init__()
        self.move(*COORDS)
        self.setWindowTitle('pyQuiz')
        self.name = quiz['name']
        del quiz['name']
        self.quiz = quiz
        self.curent_window = None
        self.API = None
        self.question_button = None
        self.timer = None
        self.raiting_table, self.raiting_box, self.raiting_button = None, None, None
        # question
        self.answers = []
        self.question_box, self.question_label, self.question_pbar = None, None, None
        # true_answer
        self.true_answer_box, self.true_answer_button, self.true_answer_question = None, None, None
        self.true_answer_label, self.true_answer_answer = None, None
        # person_waiting
        self.person_waiting_pin = None
        self.person_waiting_box, self.person_waiting_title = None, None
        self.person_waiting_table, self.person_waiting_button = None, None
        self.person_waiting_box = None
        self.thread_signal(URL)

    def delete_raiting_widgets(self):
        if self.raiting_box is not None:
            sip.delete(self.raiting_box)
            self.raiting_box = None
        if self.raiting_table is not None:
            self.raiting_table.deleteLater()
            self.raiting_table = None
        if self.raiting_button is not None:
            self.raiting_button.deleteLater()
            self.raiting_button = None

    def delete_question_widgets(self):
        if self.timer is not None:
            self.timer.stop()
            self.timer = None
        if self.question_box is not None:
            sip.delete(self.question_box)
            self.question_box = None
        if self.question_label is not None:
            self.question_label.deleteLater()
            self.question_label = None
        if self.answers is not None:
            for i in range(len(self.answers)):
                if self.answers[i] is not None:
                    self.answers[i].deleteLater()
                    self.answers[i] = None
        self.answers = []
        if self.question_button is not None:
            self.question_button.deleteLater()
            self.question_button = None

        if self.question_pbar is not None:
            self.question_pbar.deleteLater()
            self.question_pbar = None

    def delete_true_answer_widgets(self):
        if self.true_answer_box is not None:
            sip.delete(self.true_answer_box)
            self.true_answer_box = None
        if self.true_answer_question is not None:
            self.true_answer_question.deleteLater()
            self.true_answer_question = None
        if self.true_answer_label is not None:
            self.true_answer_label.deleteLater()
            self.true_answer_label = None
        if self.true_answer_answer is not None:
            self.true_answer_answer.deleteLater()
            self.true_answer_answer = None
        if self.true_answer_button is not None:
            self.true_answer_button.deleteLater()
            self.true_answer_button = None

    def delete_person_waiting_widgets(self):
        if self.person_waiting_table is not None:
            self.person_waiting_table.deleteLater()
            self.person_waiting_table = None
        if self.person_waiting_box is not None:
            sip.delete(self.person_waiting_box)
            self.person_waiting_box = None
        if self.person_waiting_button is not None:
            self.person_waiting_button.deleteLater()
            self.person_waiting_button = None
        if self.person_waiting_title is not None:
            self.person_waiting_title.deleteLater()
            self.person_waiting_title = None
        if self.person_waiting_pin is not None:
            self.person_waiting_pin.deleteLater()
            self.person_waiting_pin = None

    def delete_all_windgets(self):
        self.delete_person_waiting_widgets()  # +++
        self.delete_true_answer_widgets()  # +++
        self.delete_raiting_widgets()  # +++
        self.delete_question_widgets()  # +++

    def raiting_window(self, raiting: List[Tuple[int, str]]):
        self.delete_all_windgets()
        self.raiting_box = QVBoxLayout()
        self.raiting_box.setContentsMargins(0, 0, 0, 0)
        raiting.sort(reverse=True)
        self.raiting_table = QTableWidget()
        self.raiting_table.setRowCount(len(raiting))
        self.raiting_table.setColumnCount(2)
        self.raiting_table.setHorizontalHeaderLabels(['имя', 'очки'])
        for i in range(len(raiting)):
            self.raiting_table.setItem(i, 1, QTableWidgetItem(str(raiting[i][0])))
            self.raiting_table.setItem(i, 0, QTableWidgetItem(str(raiting[i][1])))
        self.raiting_table.setColumnWidth(0, 177)
        self.raiting_table.setColumnWidth(1, 120)
        self.raiting_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setStyleSheet(
            QUIZ_STYLE_SHEET)
        self.raiting_box.addWidget(self.raiting_table)
        self.raiting_button = QPushButton('next')
        self.raiting_button.clicked.connect(self.to_question)
        self.raiting_box.addWidget(self.raiting_button)
        self.setLayout(self.raiting_box)
        self.setFixedSize(300, 300)

    def question_window(self, question, answer_array, time=10):
        self.delete_all_windgets()
        self.time = time
        self.question_box = QVBoxLayout()
        self.question_label = QLabel()
        self.question_label.setText(question)
        self.question_label.setStyleSheet(
            'QLabel{font-size:50px;font-weight:bold;background-color:#3C3F41;color:#BBBBBB;}')
        self.question_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.question_box.addWidget(self.question_label)

        self.answers = [0 for _ in range(len(answer_array))]
        for i in range(len(answer_array)):
            self.answers[i] = QLabel(str(answer_array[i]))
            self.answers[i].setStyleSheet(
                'QLabel {font-size: 40px; font-weight: bold; background-color: ' +
                OPTIONS_BUTTONS_COLOR[i] + '; color: ' + OPTIONS_BUTTONS_STRING_COLOR[i] + ';}')
            self.question_box.addWidget(self.answers[i])

        self.question_pbar = QProgressBar()
        self.question_pbar.setFixedHeight(50)
        self.question_pbar.setStyleSheet("""
                QProgressBar{
                    border: 2px solid grey;
                    border-radius: 5px;
                    text-align: center;
                    color: black;
                    font-size:30px;
                }

                QProgressBar::chunk {
                    background-color: pink;
                    width: 10px;
                    margin: 1px;
                }
            """)

        self.timer = QBasicTimer()
        self.step = 0
        self.timer.start(100, self)
        self.question_box.addWidget(self.question_pbar)
        self.setLayout(self.question_box)
        self.setStyleSheet(QUIZ_STYLE_SHEET)
        self.setFixedSize(1000, 480)

    def timerEvent(self, e):
        if self.question_pbar is not None and self.question_pbar.value() == 100:
            self.question_pbar.deleteLater()
            self.question_pbar = None
            self.question_button = QPushButton('next')
            self.question_button.setFixedHeight(50)
            self.question_button.clicked.connect(self.to_true_false)

            self.question_box.addWidget(self.question_button)
            self.setFixedSize(1000, 480)
            # QShortcut(QKeySequence("Ctrl+n"), self, self.next)

        elif self.question_pbar is not None:
            self.step = self.step + 100 / self.time / 10
            self.question_pbar.setValue(min(self.step, 100))

    def true_answer_window(self, question, answer, index):
        self.delete_all_windgets()
        self.true_answer_box = QVBoxLayout()
        self.true_answer_question = QLabel()
        self.true_answer_question.setText(question)
        self.true_answer_question.setStyleSheet(
            'QLabel{font-size:50px;font-weight:bold;background-color:#3C3F41;color:#BBBBBB;}')
        self.true_answer_question.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.true_answer_label = QLabel('Правильный ответ:')
        self.true_answer_label.setStyleSheet(
            'QLabel{font-size:50px;font-weight:bold;background-color:#3C3F41;color:#BBBBBB;}')
        self.true_answer_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.true_answer_label.setFixedHeight(50)

        self.true_answer_answer = QLabel(str(answer))

        self.true_answer_answer.setStyleSheet(
            'QLabel {font-size: 40px; font-weight: bold; background-color: ' +
            OPTIONS_BUTTONS_COLOR[index] + '; color: ' + OPTIONS_BUTTONS_STRING_COLOR[
                index] + ';}')
        self.true_answer_box.addWidget(self.true_answer_question)
        self.true_answer_box.addWidget(self.true_answer_label)
        self.true_answer_box.addWidget(self.true_answer_answer)
        self.true_answer_button = QPushButton('next')
        self.true_answer_button.clicked.connect(self.to_raiting)
        self.true_answer_box.addWidget(self.true_answer_button)
        self.setLayout(self.true_answer_box)
        self.setStyleSheet(
            QUIZ_STYLE_SHEET)
        self.setFixedSize(1000, 480)

    def to_raiting(self):
        self.curent_window = self.raiting_window

    def to_question(self):
        self.curent_window = self.question_window

    def to_true_false(self):
        self.curent_window = self.true_answer_window

    def person_waiting_window(self, quiz_title, pin, peoples):
        self.delete_all_windgets()
        self.person_waiting_box = QVBoxLayout()
        self.person_waiting_table = QTableWidget()
        self.person_waiting_table.setRowCount(len(peoples))
        self.person_waiting_table.setColumnCount(1)
        self.person_waiting_table.horizontalHeader().hide()
        self.person_waiting_table.verticalHeader().hide()

        for i in range(len(peoples)):
            self.person_waiting_table.setItem(i, 0, QTableWidgetItem(str(peoples[i])))
        self.person_waiting_table.setColumnWidth(0, 300)
        self.person_waiting_table.setFixedHeight(150)

        self.person_waiting_title = QLabel()
        self.person_waiting_title.resize(300, 100)
        self.person_waiting_title.setText(quiz_title)

        self.person_waiting_title.setStyleSheet(
            'QLabel{font-size:30px;font-weight:bold;background-color:#3C3F41;color:#BBBBBB;}')
        self.person_waiting_title.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.person_waiting_pin = QLabel()
        self.person_waiting_pin.setText(pin)
        self.person_waiting_pin.setStyleSheet(
            'QLabel{font-size:30px;font-weight:bold;background-color:#3C3F41;color:#BBBBBB;}')
        self.person_waiting_pin.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.person_waiting_button = QPushButton('start game')
        self.person_waiting_button.clicked.connect(self.play)

        self.person_waiting_box.addWidget(self.person_waiting_title)
        self.person_waiting_box.addWidget(self.person_waiting_pin)
        self.person_waiting_box.addWidget(self.person_waiting_table)
        self.person_waiting_box.addWidget(self.person_waiting_button)

        self.person_waiting_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setLayout(self.person_waiting_box)
        self.setStyleSheet(QUIZ_STYLE_SHEET)
        self.setFixedSize(300, 300)

    def play(self):
        if self.person_waiting_table.rowCount() < PLAYERS_NUM_MIN:
            showMsg('нет людей')
            return

        self.curent_window = self.question_window

    def thread_signal(self, url):
        self.thread = HostThread(url, self)
        self.thread.Signal.connect(self.change_window)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def change_window(self, value):
        func = value[0]
        arguments = value[1:]
        func(*arguments)

    def on_finished(self):
        self.thread.Signal.disconnect(self.change_window)
        self.thread.finished.disconnect(self.on_finished)
        self.exit()

    def exit(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.quiz_selection_window = QuizSelectionWindow()
        self.quiz_selection_window.show()
        self.close()


#######################

class CreateQuizWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.DEFAULT_BLOCK = (10, 100, [('Вопрос №1', ['Ответ №1', 'Ответ №2'], 0)])
        self.blocks = [self.DEFAULT_BLOCK]
        self.questions = self.blocks[0][2]
        self.cur_block = 0
        self.cur_question = -1
        self.initUI()

    def initUI(self):
        self.move(*COORDS)
        self.setWindowTitle('pyQuiz')

        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText('Название викторины')
        self.title_edit.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.prev_block_button = QPushButton()
        self.prev_block_button.setIcon(QIcon('assets/back.png'))
        self.prev_block_button.setFixedWidth(30)
        self.prev_block_button.setEnabled(False)
        self.prev_block_button.clicked.connect(self.prevBlock)

        self.next_block_button = QPushButton()
        self.next_block_button.setIcon(QIcon('assets/plus.png'))
        self.next_block_button.setFixedWidth(30)
        self.next_block_button.clicked.connect(self.nextBlock)

        self.delete_block_button = QPushButton()
        self.delete_block_button.setIcon(QIcon('assets/cross.png'))
        self.delete_block_button.setFixedWidth(30)
        self.delete_block_button.setEnabled(False)
        self.delete_block_button.clicked.connect(self.delBlock)

        self.block_name_label = QLabel('Блок №1')
        self.block_name_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)

        self.block_time_limit = QLineEdit()
        self.block_time_limit.setPlaceholderText('Время на вопрос')

        self.block_points = QLineEdit()
        self.block_points.setPlaceholderText('Очки за вопрос')

        self.add_question_button = QPushButton()
        self.add_question_button.setIcon(QIcon('assets/plus.png'))
        self.add_question_button.clicked.connect(self.addQuestion)

        self.delete_question_button = QPushButton()
        self.delete_question_button.setIcon(QIcon('assets/cross.png'))
        self.delete_question_button.clicked.connect(self.deleteQuestion)

        self.questions_list = QListWidget()
        self.questions_list.setFixedWidth(150)
        self.questions_list.itemSelectionChanged.connect(self.switchQuestion)

        self.question_text_edit = QLineEdit()
        self.question_text_edit.setPlaceholderText('Текст вопроса')

        self.options_list = QListWidget()

        self.exit_button = QPushButton()
        self.exit_button.clicked.connect(self.exit)

        self.exit_button.setText('Назад')
        self.exit_button.setStyleSheet(
            'QPushButton{font-size:30px;text-align:center;background-color:#3C3F41;color:#BBBBBB;}')

        self.save_button = QPushButton()
        self.save_button.setText('Сохранить')
        self.save_button.setStyleSheet(
            'QPushButton{font-size:30px;text-align:center;background-color:#3C3F41;color:#BBBBBB;}')
        self.save_button.clicked.connect(self.save)

        self.add_option_button = QPushButton()
        self.add_option_button.setIcon(QIcon('assets/plus.png'))
        self.add_option_button.clicked.connect(self.addOption)

        self.delete_option_button = QPushButton()
        self.delete_option_button.setIcon(QIcon('assets/cross.png'))
        self.delete_option_button.clicked.connect(self.delOption)

        vbox = QVBoxLayout()

        menu_layout = QHBoxLayout()
        menu_layout.addWidget(self.prev_block_button)
        menu_layout.addWidget(self.block_name_label)
        menu_layout.addWidget(self.delete_block_button)
        menu_layout.addWidget(self.next_block_button)

        block_settings = QHBoxLayout()
        block_settings.addWidget(self.block_time_limit)
        block_settings.addWidget(self.block_points)

        main_layout = QHBoxLayout()

        block_table_layout = QVBoxLayout()
        block_table_layout.addWidget(self.questions_list)
        change_block_layout = QHBoxLayout()
        change_block_layout.addWidget(self.add_question_button)
        change_block_layout.addWidget(self.delete_question_button)
        block_table_layout.addLayout(change_block_layout)

        main_layout.addLayout(block_table_layout)
        question_layout = QVBoxLayout()

        question_layout.addWidget(self.question_text_edit)
        question_layout.addWidget(self.options_list)
        change_question_layout = QHBoxLayout()
        change_question_layout.addWidget(self.add_option_button)
        change_question_layout.addWidget(self.delete_option_button)
        question_layout.addLayout(change_question_layout)

        main_layout.addLayout(question_layout)

        footer_menu = QHBoxLayout()
        footer_menu.addWidget(self.exit_button)
        footer_menu.addWidget(self.save_button)

        vbox.addWidget(self.title_edit)
        vbox.addLayout(menu_layout)
        vbox.addLayout(block_settings)
        vbox.addLayout(main_layout)
        vbox.addLayout(footer_menu)

        self.restoreBlock()

        self.setLayout(vbox)
        self.setStyleSheet(QUIZ_STYLE_SHEET)
        self.setFixedSize(500, 500)

    def blockNavUpdate(self):
        if self.cur_block == len(self.blocks) - 1:
            self.next_block_button.setIcon(QIcon('assets/plus.png'))
        else:
            self.next_block_button.setIcon(QIcon('assets/next.png'))
        self.prev_block_button.setEnabled(self.cur_block > 0)
        self.next_block_button.setEnabled(self.cur_block < QUIZ_BLOCKS_NUM_RANGE.stop - 1)
        self.delete_block_button.setEnabled(len(self.blocks) > 1)
        self.block_name_label.setText(f'Блок № {self.cur_block + 1}')

    def showMsg(self, s, type=QMessageBox.Critical):
        msg = QMessageBox()
        msg.setIcon(type)
        msg.setText(s)
        msg.setWindowTitle('pyQuiz')
        msg.exec_()

    def saveBlock(self):
        if self.cur_question != -1:
            if not self.saveQuestion():
                return False
        time = self.block_time_limit.text()
        points = self.block_points.text()
        if not time.isnumeric():
            self.showMsg('Время на вопрос должно быть целым числом!')
            return False
        time = int(time)
        if time not in QUIZ_BLOCK_TIME_RANGE:
            self.showMsg(f'Время на вопрос должно быть не меньше {QUIZ_BLOCK_TIME_RANGE.start}, '
                         f'но меньше {QUIZ_BLOCK_TIME_RANGE.stop}')
            return False
        if not points.isnumeric():
            self.showMsg('Кол-во очков за вопрос должно быть целым числом!')
            return False
        points = int(points)
        if points not in QUIZ_BLOCK_POINTS_RANGE:
            self.showMsg(
                f'Кол-во очков за вопрос должно быть не меньше {QUIZ_BLOCK_POINTS_RANGE.start}, '
                f'но меньше {QUIZ_BLOCK_POINTS_RANGE.stop}')
            return False
        if len(self.questions) not in QUIZ_QUESTIONS_NUM_RANGE:
            self.showMsg(
                f'Кол-во вопросов в блоке должно быть не меньше {QUIZ_QUESTIONS_NUM_RANGE.start}, '
                f'но меньше {QUIZ_QUESTIONS_NUM_RANGE.stop}')
            return False
        self.blocks[self.cur_block] = (time, points, self.questions)
        return True

    def restoreBlock(self):
        block = self.blocks[self.cur_block]
        self.block_time_limit.setText(str(block[0]))
        self.block_points.setText(str(block[1]))
        self.questions_list.clear()
        for question_text, options, right_option in block[2]:
            self.questions_list.addItem(question_text)
        self.questions = block[2][:]
        self.cur_question = -1
        self.questions_list.clearSelection()
        self.question_text_edit.setText('')
        self.options_list.clear()
        self.cur_question = -1

    def nextBlock(self):
        if not self.saveBlock():
            return
        self.cur_block += 1
        if self.cur_block == len(self.blocks):
            self.blocks.append(self.DEFAULT_BLOCK)
        self.blockNavUpdate()
        self.restoreBlock()

    def prevBlock(self):
        if not self.saveBlock():
            return
        self.cur_block -= 1
        self.blockNavUpdate()
        self.restoreBlock()

    def delBlock(self):
        self.blocks.pop(self.cur_block)
        if self.cur_block == len(self.blocks):
            self.cur_block -= 1
        self.blockNavUpdate()
        self.restoreBlock()

    def switchQuestion(self):
        if len(self.questions_list.selectedIndexes()) == 0:
            return
        if self.cur_question != -1:
            if not self.saveQuestion():
                self.questions_list.blockSignals(True)
                self.questions_list.clearSelection()
                self.questions_list.item(self.cur_question).setSelected(True)
                self.questions_list.blockSignals(False)
                return
        self.cur_question = self.questions_list.selectedIndexes()[0].row()
        self.restoreQuestion()

    def addQuestion(self):
        question_text, okBtnPressed = QInputDialog.getText(self,
                                                           'Создание вопроса',
                                                           'Введите текст вопроса')
        if not okBtnPressed:
            return
        if len(question_text) not in QUIZ_QUESTION_TEXT_LEN_RANGE:
            self.showMsg(
                f'Длина вопроса должна быть не меньше {QUIZ_QUESTION_TEXT_LEN_RANGE.start}, '
                f'но меньше {QUIZ_QUESTION_TEXT_LEN_RANGE.stop}', QMessageBox.Critical)
            return
        i = -1
        if len(self.questions_list.selectedIndexes()) > 0:
            i = self.questions_list.selectedIndexes()[0].row()
        i += 1
        self.questions.insert(i, (question_text, ['Ответ №1', 'Ответ №2'], 0))
        self.questions_list.insertItem(i, question_text)
        self.delete_question_button.setEnabled(True)

    def deleteQuestion(self):
        if len(self.questions_list.selectedIndexes()) == 0:
            return
        i = self.questions_list.selectedIndexes()[0].row()
        self.questions_list.takeItem(i)
        self.questions.pop()
        self.cur_question = -1

    def saveQuestion(self):
        question_text = self.question_text_edit.text()
        if len(question_text) not in QUIZ_QUESTION_TEXT_LEN_RANGE:
            self.showMsg(
                f'Длина текста вопроса должна быть не меньше {QUIZ_QUESTION_TEXT_LEN_RANGE.start}, '
                f'но меньше {QUIZ_QUESTION_TEXT_LEN_RANGE.stop}', QMessageBox.Critical)
            return False
        self.questions_list.item(self.cur_question).setText(question_text)
        options = []
        for i in range(len(self.options_list)):
            options.append(self.options_list.item(i).text())
        if len(options) not in QUIZ_OPTIONS_NUM_RANGE:
            self.showMsg(
                f'Кол-во ответов на вопрос должно быть не меньше {QUIZ_OPTIONS_NUM_RANGE.start}, '
                f'но меньше {QUIZ_OPTIONS_NUM_RANGE.stop}', QMessageBox.Critical)
            return False
        if len(self.options_list.selectedIndexes()) != 1:
            self.showMsg(f'Не выбран правильный ответ!', QMessageBox.Critical)
            return False
        right_answer = self.options_list.selectedIndexes()[0].row()
        self.questions[self.cur_question] = (question_text, options, right_answer)
        return True

    def restoreQuestion(self):
        question = self.questions[self.cur_question]
        self.question_text_edit.setText(question[0])
        self.options_list.clear()
        for option in question[1]:
            self.options_list.addItem(option)
        self.options_list.item(question[2]).setSelected(True)

    def addOption(self):
        option_text, okBtnPressed = QInputDialog.getText(self,
                                                         'Создание ответа',
                                                         'Введите текст ответа')
        if not okBtnPressed:
            return
        if len(option_text) not in QUIZ_OPTION_TEXT_LEN_RANGE:
            self.showMsg(f'Длина ответа должна быть не меньше {QUIZ_OPTION_TEXT_LEN_RANGE.start}, '
                         f'но меньше {QUIZ_OPTION_TEXT_LEN_RANGE.stop}', QMessageBox.Critical)
            return
        self.options_list.addItem(option_text)

    def delOption(self):
        for index in self.options_list.selectedIndexes():
            self.options_list.takeItem(index.row())

    def save(self):
        if not self.saveBlock():
            return
        quiz_name = self.title_edit.text()
        if len(quiz_name) not in QUIZ_NAME_LEN_RANGE:
            self.showMsg(
                f'Длина названия викторины должна быть не меньше {QUIZ_NAME_LEN_RANGE.start}, '
                f'но меньше {QUIZ_NAME_LEN_RANGE.stop}')
            return
        quiz_json = {'name': quiz_name}
        cur = 0
        for time, pts, questions in self.blocks:
            for text, options, right_answer in questions:
                quiz_json[str(cur)] = {
                    'time': time,
                    'score': pts,
                    'question': text,
                    'answers': list(options),
                    'true': right_answer
                }
                cur += 1
        # QUIZ_SAVE_DIR
        file_name_preffix = secrets.token_hex(5)
        while os.path.isfile(os.path.join(QUIZ_SAVE_DIR, file_name_preffix)):
            file_name_preffix = secrets.token_hex(5)
        # https://stackoverflow.com/questions/18337407/saving-utf-8-texts-in-json-dumps-as-utf8-not-as-u-escape-sequence
        file_path = os.path.join(QUIZ_SAVE_DIR, quiz_name + '_' + file_name_preffix + '.json')
        with open(file_path, 'w', encoding='utf8') as json_file:
            json.dump(quiz_json, json_file, ensure_ascii=False, sort_keys=True, indent=4)
        self.exit()

    def exit(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.create_game_window = QuizSelectionWindow()
        self.create_game_window.show()
        self.close()


#############
class QuizSelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.move(*COORDS)
        self.quizzes = []
        self.setWindowTitle('pyQuiz')
        self.create_game = QPushButton('Cоздать')
        self.create_game.clicked.connect(self.create_new_game)
        self.create_game.setStyleSheet(QBUTTON_STYLE)

        self.play_game = QPushButton('Играть')
        self.play_game.setStyleSheet(QBUTTON_STYLE)
        self.play_game.clicked.connect(self.play)

        self.exit_button = QPushButton()
        self.exit_button.clicked.connect(self.exit)

        self.exit_button.setText('Назад')
        self.exit_button.setStyleSheet(QBUTTON_STYLE)

        self.quizzes_list = QListWidget()
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.create_game)
        hbox.addWidget(self.play_game)
        vbox.addWidget(self.quizzes_list)
        vbox.addLayout(hbox)
        vbox.addWidget(self.exit_button)
        self.setLayout(vbox)
        self.setStyleSheet(QUIZ_STYLE_SHEET)
        self.setFixedSize(300, 300)

        self.quizzes = []
        mypath = os.path.abspath(QUIZ_SAVE_DIR)
        onlyfiles = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]

        for file in onlyfiles:
            filename, file_extension = os.path.splitext(file)
            if file_extension == '.json':
                with open(os.path.join(mypath, file), 'r', encoding='utf8') as f:
                    data = json.load(f)
                    self.quizzes_list.addItem(data['name'])
                    self.quizzes.append(data)

    def play(self):
        if len(self.quizzes_list.selectedIndexes()) == 0:
            return
        cur = self.quizzes_list.selectedIndexes()[0].row()
        global COORDS
        COORDS = [self.x(), self.y()]
        self.host_window = Host(self.quizzes[cur])
        self.host_window.show()
        self.close()

    def exit(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.create_game_window = StartWindow()
        self.create_game_window.show()
        self.close()

    def create_new_game(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.create_game_window = CreateQuizWindow()
        self.create_game_window.show()
        self.close()


class StartWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.move(*COORDS)
        self.setWindowTitle('pyQuiz')
        self.play_btn = QPushButton(self)
        self.host_btn = QPushButton(self)
        self.play_btn.setText('Играть')
        self.host_btn.setText('Создать')
        self.play_btn.resize(300, 100)
        self.play_btn.move(0, 100)
        self.host_btn.resize(300, 100)
        self.host_btn.move(0, 200)

        self.help_btn = QPushButton(self)
        self.help_btn.resize(50, 50)
        self.help_btn.setIcon(QIcon('assets/question.png'))
        self.help_btn.setIconSize(QSize(40, 40))
        self.help_btn.move(250, 50)

        self.settngs_btn = QPushButton(self)
        self.settngs_btn.resize(50, 50)
        self.settngs_btn.setIcon(QIcon('assets/api.png'))
        self.settngs_btn.setIconSize(QSize(40, 40))
        self.settngs_btn.move(250, 0)

        self.settngs_btn.clicked.connect(self.open_settings)
        self.help_btn.clicked.connect(self.open_help)
        self.setStyleSheet(QUIZ_STYLE_SHEET)
        self.setFixedSize(300, 300)

        self.play_btn.setStyleSheet(
            'QPushButton{font-size:40px;background-color:#3C3F41;color:#BBBBBB;}')
        self.host_btn.setStyleSheet(
            'QPushButton{font-size:40px;background-color:#3C3F41;color:#BBBBBB;}')

        self.title_label = QLabel(self)
        self.title_label.resize(300, 100)
        self.title_label.setText('PyQuiz')
        self.title_label.setStyleSheet('QLabel {font-size: 40px;font-weight: bold;}')
        self.title_label.lower()
        self.title_label.setAlignment(Qt.AlignCenter | Qt.AlignHCenter)
        self.setStyleSheet(QUIZ_STYLE_SHEET)

        self.play_btn.clicked.connect(self.start_game)
        self.host_btn.clicked.connect(self.create_game)

    def open_settings(self):
        global URL
        new_url, okBtnPressed = QInputDialog.getText(self,
                                                     'Настройки',
                                                     'Введите url хоста')
        if okBtnPressed:
            URL = new_url

    def open_help(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.help_window = HelpWindow()
        self.help_window.show()
        self.close()

    def start_game(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.game_window = PlayerGameWindow()
        self.game_window.show()
        self.close()

    def create_game(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.create_game_window = QuizSelectionWindow()
        self.create_game_window.show()
        self.close()


class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.move(*COORDS)
        self.setWindowTitle('pyQuiz')
        self.setStyleSheet(QUIZ_STYLE_SHEET)
        self.setFixedSize(300, 300)
        hbox = QHBoxLayout()
        pixmap = QPixmap('assets/quiz.png')
        pixmap = pixmap.scaled(150, 150)
        label = QLabel()
        label.setPixmap(pixmap)
        about = QLabel()
        about.setText(QUIZ_HELP_TEXT)

        about.setWordWrap(True)
        about.setStyleSheet('QLabel{font-size:12px;background-color:#3C3F41;color:#BBBBBB;}')
        self.repo_btn = QPushButton('PyQuiz repo')
        self.doc_btn = QPushButton('PyQuiz doc')
        self.back_btn = QPushButton('back')
        hbox.addWidget(label)
        hbox.addWidget(about)
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.repo_btn)
        vbox.addWidget(self.doc_btn)
        vbox.addWidget(self.back_btn)
        self.repo_btn.clicked.connect(self.repo)
        self.doc_btn.clicked.connect(self.doc)
        self.back_btn.clicked.connect(self.back)
        self.setLayout(vbox)
        self.setStyleSheet(QUIZ_STYLE_SHEET)

    def repo(self):
        webbrowser.open('https://github.com/9kin/PyQuiz')

    def doc(self):
        webbrowser.open('https://pyquiz2.readthedocs.io/en/latest/')

    def back(self):
        global COORDS
        COORDS = [self.x(), self.y()]
        self.start_window_window = StartWindow()
        self.start_window_window.show()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = StartWindow()
    ex.show()
    sys.exit(app.exec())
