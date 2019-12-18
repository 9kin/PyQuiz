QUIZ_NAME_LEN_LEN = 2
QUIZ_NAME_LEN_RANGE = range(1, 10 ** QUIZ_NAME_LEN_LEN)

QUIZ_BLOCKS_NUM_LEN = 1
QUIZ_BLOCKS_NUM_RANGE = range(1, 10 ** QUIZ_BLOCKS_NUM_LEN)

QUIZ_BLOCK_TIME_LEN = 2
QUIZ_BLOCK_TIME_RANGE = range(1, 10 ** QUIZ_BLOCK_TIME_LEN)

QUIZ_BLOCK_POINTS_LEN = 3
QUIZ_BLOCK_POINTS_RANGE = range(1, 10 ** QUIZ_BLOCK_POINTS_LEN)

QUIZ_QUESTIONS_NUM_LEN = 1
QUIZ_QUESTIONS_NUM_RANGE = range(1, 10 ** QUIZ_QUESTIONS_NUM_LEN)

QUIZ_QUESTION_TEXT_LEN_LEN = 2
QUIZ_QUESTION_TEXT_LEN_RANGE = range(1, 10 ** QUIZ_QUESTION_TEXT_LEN_LEN)

QUIZ_OPTIONS_NUM_LEN = 1
QUIZ_OPTIONS_MAX_NUM = 7
QUIZ_OPTIONS_NUM_RANGE = range(2, QUIZ_OPTIONS_MAX_NUM + 1)

QUIZ_OPTION_TEXT_LEN_LEN = 2
QUIZ_OPTION_TEXT_LEN_RANGE = range(1, 10 ** QUIZ_OPTION_TEXT_LEN_LEN)

PLAYER_NAME_LEN_LEN = 2
PLAYER_NAME_LEN_RANGE = range(1, 20)

PLAYERS_NUM_MIN = 1
PLAYERS_NUM_LEN = 2
PLAYERS_NUM_RANGE = range(PLAYERS_NUM_MIN, 10 ** PLAYERS_NUM_LEN)

GAME_ID_LEN = 6
GAME_ID_RANGE = range(10 ** (GAME_ID_LEN - 1), 10 ** GAME_ID_LEN)

QUIZ_SAVE_DIR = ".quizzes/"

###

OPTIONS_BUTTONS_MAP = {
    2: [(0, 0, 150, 300), (150, 0, 150, 300)],
    3: [(0, 0, 150, 150), (150, 0, 150, 150), (0, 150, 300, 150)],
    4: [(0, 0, 150, 150), (150, 0, 150, 150), (0, 150, 150, 150), (150, 150, 150, 150)],
    5: [
        (0, 0, 150, 100),
        (150, 0, 150, 100),
        (0, 100, 150, 100),
        (150, 100, 150, 100),
        (0, 200, 300, 100)
    ],
    6: [
        (0, 0, 150, 100),
        (150, 0, 150, 100),
        (0, 100, 150, 100),
        (150, 100, 150, 100),
        (0, 200, 150, 100),
        (150, 200, 150, 100)
    ],
    7: [
        (0, 0, 150, 75),
        (150, 0, 150, 75),
        (0, 75, 150, 75),
        (150, 75, 150, 75),
        (0, 150, 150, 75),
        (150, 150, 150, 75),
        (0, 225, 300, 75)
    ],
    8: [
        (0, 0, 150, 75),
        (150, 0, 150, 75),
        (0, 75, 150, 75),
        (150, 75, 150, 75),
        (0, 150, 150, 75),
        (150, 150, 150, 75),
        (0, 225, 150, 75),
        (150, 225, 150, 75)
    ]
}

OPTIONS_BUTTONS_COLOR = ['red', 'green', 'yellow', 'blue', 'pink', 'orange', 'skyblue', 'palegreen']
OPTIONS_BUTTONS_STRING_COLOR = ['black', 'white', 'blue', 'yellow', 'green', 'avevad', 'purple', 'darkblue']
