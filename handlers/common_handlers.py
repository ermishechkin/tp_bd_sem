from database import init_db as init, recreate_db, clear_db
from bottle import route, get, post

def normal_json(data):
    return { "code": 0, "response": data }

def check_related(actual, possible):
    temp = list(actual)
    for i in possible:
        if i in temp:
            temp.remove(i)
    return len(temp) == 0

@route('/init')
def init_db():
    init()

@route('/reinit')
def reinit():
    recreate_db()

@post('/db/api/clear/')
def clear():
    clear_db()
    return normal_json("OK")
