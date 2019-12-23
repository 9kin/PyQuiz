import datetime
import secrets
import time
import json
from fastapi import FastAPI, HTTPException

app = FastAPI()

host_map = {}
empty_hosts = list([i for i in range(100001, 1000000)])


@app.get('/status')
def status(game_id: int, key: str):
    if game_id not in host_map or host_map[game_id]['key'] != key:
        raise HTTPException(status_code=404, detail='error')
    return host_map[game_id]


@app.get('/host')
def host(quiz: str):
    global host_map, empty_hosts
    key = secrets.token_hex(20)
    game_id = empty_hosts[0]
    try:
        quiz = json.loads(quiz)
        host_map[game_id] = {
            'key': key,
            'last_active': datetime.datetime.now(),
            'question_cnt': -1,  # wait
            'peoples': {},
            'quiz': quiz,
        }
        empty_hosts = empty_hosts[1:]
        return {'id': game_id, 'key': key}
    except:
        if game_id in host_map:
            del host_map[game_id]
        raise HTTPException(status_code=404, detail='error')


@app.get('/{game_id}/connect')
def connect(game_id: int, name: str):
    global host_map
    if game_id not in host_map or host_map[game_id]['question_cnt'] != -1:
        raise HTTPException(status_code=404, detail='game')
    else:
        for i in host_map[game_id]['peoples']:
            if host_map[game_id]['peoples'][i]['name'] == name:
                raise HTTPException(status_code=404, detail='name')
        key = secrets.token_hex(20)
        host_map[game_id]['peoples'][key] = {'score': 0,
                                             'last_active': datetime.datetime.now(),
                                             'name': name,
                                             'last': {'ans': -1, 'res': False, 'add': 0}}
    return {'key': key}


@app.get('/{game_id}/play')
def play(game_id: int, key: str):
    global host_map
    if game_id not in host_map or host_map[game_id]['key'] != key or \
            host_map[game_id]['question_cnt'] != -1 or len(host_map[game_id]['peoples']) == 0:
        raise HTTPException(status_code=404, detail='error')
    else:
        host_map[game_id]['question_cnt'] = 0
        host_map[game_id]['last_active'] = datetime.datetime.now()
        return {1}


@app.get('/{game_id}/next')
def next_game(game_id: int, key: str):
    global host_map
    if game_id not in host_map or host_map[game_id]['key'] != key or \
            host_map[game_id]['question_cnt'] < 0:
        raise HTTPException(status_code=404, detail='error')
    else:
        if len(host_map[game_id]['quiz']) == host_map[game_id]['question_cnt'] + 1:
            return {'finish'}
        host_map[game_id]['question_cnt'] += 1
        host_map[game_id]['last_active'] = datetime.datetime.now()
        for key in host_map[game_id]['peoples']:
            host_map[game_id]['peoples'][key]['score'] += \
                host_map[game_id]['peoples'][key]['last']['add']
            host_map[game_id]['peoples'][key]['last'] = {'ans': -1, 'res': False, 'add': 0}
        return {'next'}


@app.get('/{game_id}/validate')
def validate(game_id: int, key: str):
    global host_map
    if game_id not in host_map or host_map[game_id]['question_cnt'] < 0 or \
            key not in host_map[game_id]['peoples']:
        raise HTTPException(status_code=404, detail='error')
    cur = str(host_map[game_id]['question_cnt'])
    curent_time = datetime.datetime.now()
    host_map[game_id]['peoples'][key]['last_active'] = curent_time
    question_time = host_map[game_id]['quiz'][cur]['time']
    start_time = host_map[game_id]['last_active']
    time.sleep(max(0, question_time - (curent_time - start_time).total_seconds()))  ## !!!!!!!
    score = host_map[game_id]['peoples'][key]['last']['add'] + \
            host_map[game_id]['peoples'][key]['score']
    place = 1
    arr = []
    for k in host_map[game_id]['peoples']:
        val = host_map[game_id]['peoples'][k]
        arr.append([val['score'] + val['last']['add'], k])
    arr.sort(reverse=True)
    if arr[0][1] == key:
        place = 1
    else:
        for i in range(1, len(arr)):
            if arr[i][0] != arr[i - 1][0]:
                place += 1
            if arr[i][1] == key:
                break
    return {'valid': host_map[game_id]['peoples'][key]['last']['res'],
            'score': score,
            'place': place}


# send ans
@app.get('/{game_id}/reply')
def reply(game_id: int, key: str, ans: int):
    global host_map
    if game_id not in host_map or host_map[game_id]['question_cnt'] < 0:
        raise HTTPException(status_code=404, detail='error')
    if key not in host_map[game_id]['peoples']:
        raise HTTPException(status_code=404, detail='error')
    curent_time = datetime.datetime.now()
    cur = str(host_map[game_id]['question_cnt'])
    host_map[game_id]['peoples'][key]['last_active'] = curent_time
    if host_map[game_id]['peoples'][key]['last']['ans'] == int(cur):
        raise HTTPException(status_code=404, detail='error')
    host_map[game_id]['peoples'][key]['last']['ans'] = int(cur)
    right_answer = host_map[game_id]['quiz'][cur]['true']
    points = host_map[game_id]['quiz'][cur]['score']
    question_time = host_map[game_id]['quiz'][cur]['time']
    start_time = host_map[game_id]['last_active']
    if (curent_time - start_time).total_seconds() > question_time:
        raise HTTPException(status_code=404, detail='error')
    if ans == right_answer:
        time_left = (curent_time - start_time).total_seconds() / question_time
        plr_points = max(0, int(points * (1. - time_left)))
        host_map[game_id]['peoples'][key]['last']['add'] = plr_points
    host_map[game_id]['peoples'][key]['last']['res'] = (ans == right_answer)

    return {}


# wait for next question/start game
@app.get('/{game_id}/wait')
def wait(game_id: int, key: str):
    global host_map
    if game_id not in host_map:
        raise HTTPException(status_code=404, detail='error')
    if key not in host_map[game_id]['peoples']:
        raise HTTPException(status_code=404, detail='error')
    last = host_map[game_id]['last_active']
    while host_map[game_id]['last_active'] == last:
        pass
    return {1}


# return ans(cnt), time(for sleep)
@app.get('/{game_id}/question_info')
def question_info(game_id: int, key: str):
    global host_map
    if game_id not in host_map or host_map[game_id]['question_cnt'] == -1:
        raise HTTPException(status_code=404, detail='error')
    if key not in host_map[game_id]['peoples']:
        raise HTTPException(status_code=404, detail='error')
    cur = str(host_map[game_id]['question_cnt'])
    time_fished = host_map[game_id]['last_active'] + datetime.timedelta(
        seconds=int(host_map[game_id]['quiz'][cur]['time']))
    return {'ans': len(host_map[game_id]['quiz'][cur]['answers']),
            'time': time_fished - datetime.datetime.now()}


# return cnt_questions
@app.get('/{game_id}/game_info')
def game_info(game_id: int, key: str):
    global host_map
    if game_id not in host_map or host_map[game_id]['question_cnt'] == -1:
        raise HTTPException(status_code=404, detail='error')
    if key not in host_map[game_id]['peoples']:
        raise HTTPException(status_code=404, detail='error')
    return {len(host_map[game_id]['quiz'])}
