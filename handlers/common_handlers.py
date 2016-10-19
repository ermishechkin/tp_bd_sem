from database import init_db as init, recreate_db, clear_db
from bottle import route, get, post
from database import User, Forum, Thread, Post

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

@get('/db/api/status/')
def status():
    u = User().select().count()
    f = Forum().select().count()
    t = Thread().select().count()
    p = Post().select().count()
    return {'user': u, 'thread': t, 'forum': f, 'post': p}
