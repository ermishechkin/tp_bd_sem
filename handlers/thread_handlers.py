from bottle import get, post, request
from database import Thread, Forum, User, Post, SubscribeThread
from common_handlers import normal_json, check_related
from details import _user_details, _forum_details, _thread_details
from peewee import fn
from database import my_json
from lists import _post_list
from detail2 import *

@post('/db/api/thread/create/')
def thread_create():
    data = request.json
    thread, created = Thread.create_or_get(**data)
    result = thread.json(recurse=False)
    return normal_json(result)

@get('/db/api/thread/details/')
def thread_details():
    data = request.GET
    related = data.getall('related')
    if not check_related(related, ['user', 'forum']):
        return { "code": 3, "response": "Semantic error" }
    try:
        result = thread_json_by_id(data['thread'], 'user' in related, 'forum' in related)
    except:
        return { "code": 1, "response": "" }
    else:
        return normal_json(result)

@get('/db/api/thread/list/')
def thread_list():
    data = request.GET
    query = Thread.select()
    if 'forum' in data:
        query = query.where(Thread.forum==data['forum'])
    elif 'user' in data:
        query = query.where(Thread.user==data['user'])
    else:
        return { "code": 3, "response": "Semantic error" }
    query = query.dicts()
    if 'since' in data:
        query = query.where(Thread.date>=data['since'])
    if 'limit' in data:
        query = query.limit(data['limit'])
    if 'order' in data:
        if data['order'] == 'asc':
            query = query.order_by(+Thread.date)
        elif data['order'] == 'desc':
            query = query.order_by(-Thread.date)
        else:
            return { "code": 3, "response": "Semantic error" }
    res = [my_json(x) for x in query.execute()]
    return normal_json(res)



@get('/db/api/thread/listPosts/')
def thread_listPosts():
    data = request.GET
    query = Post.select()
    query = query.where(Post.thread==data['thread'])
    query = query.dicts()

    if 'sort' not in data or data['sort'] == 'flat':
        if 'since' in data:
            query = query.where(Post.date>=data['since'])
        if 'limit' in data:
            query = query.limit(data['limit'])
        if 'order' in data:
            if data['order'] == 'asc':
                query = query.order_by(+Post.date)
            elif data['order'] == 'desc':
                query = query.order_by(-Post.date)
            else:
                return { "code": 3, "response": "Semantic error" }
        res = [my_json(x) for x in query.execute()]

    elif data['sort'] == 'parent_tree':
        query = query.where(Post.parent==None)
        if 'since' in data:
            query = query.where(Post.date>=data['since'])
        if 'limit' in data:
            query = query.limit(data['limit'])
        if 'order' in data:
            if data['order'] == 'asc':
                query = query.order_by(+Post.date)
            elif data['order'] == 'desc':
                query = query.order_by(-Post.date)
            else:
                return { "code": 3, "response": "Semantic error" }
        res = []
        for x in query.execute():
            res.append(my_json(x))
            res += _post_list(x['id'])

    elif data['sort'] == 'tree':
        query = query.where(Post.parent==None)
        if 'since' in data:
            query = query.where(Post.date>=data['since'])
        if 'limit' in data:
            query = query.limit(data['limit'])
        if 'order' in data:
            if data['order'] == 'asc':
                query = query.order_by(+Post.date)
            elif data['order'] == 'desc':
                query = query.order_by(-Post.date)
            else:
                return { "code": 3, "response": "Semantic error" }
        res = []
        left = data.get('limit')
        left = int(left) if left is not None else None
        for x in query.execute():
            if left == 0:
                break
            res.append(my_json(x))
            left = left-1 if left is not None else None
            if left == 0:
                break
            t = _post_list(x['id'], left)
            res += t
            left = left-len(t) if left is not None else None

    return normal_json(res)



@post('/db/api/thread/remove/')
def thread_remove():
    data = request.json
    Thread.update(isDeleted = True, posts = 0).where(Thread.id==data['thread']).execute()
    Post.update(isDeleted=True).where(Post.thread==data['thread']).execute()
    return normal_json( {'thread': data['thread']} )

@post('/db/api/thread/restore/')
def thread_restore():
    data = request.json
    subquery = Post.select(fn.count(Post.id)).where(Post.thread==data['thread']).scalar()
    Thread.update(isDeleted = False, posts = subquery).where(Thread.id==data['thread']).execute()
    Post.update(isDeleted=False).where(Post.thread==data['thread']).execute()
    return normal_json( {'thread': data['thread']} )

@post('/db/api/thread/close/')
def thread_close():
    data = request.json
    Thread.update(isClosed = True).where(Thread.id==data['thread']).execute()
    return normal_json( {'thread': data['thread']} )

@post('/db/api/thread/open/')
def thread_open():
    data = request.json
    Thread.update(isClosed = False).where(Thread.id==data['thread']).execute()
    return normal_json( {'thread': data['thread']} )

@post('/db/api/thread/update/')
def thread_update():
    data = request.json
    Thread.update(message = data['message'], slug = data['slug']).where(Thread.id==data['thread']).execute()
    result = thread_json_by_id(data['thread'], False, False)
    return normal_json(result)

@post('/db/api/thread/vote/')
def thread_vote():
    data = request.json
    if data['vote'] not in [-1, 1]:
        return { "code": 3, "response": "Semantic error" }
    if data['vote'] == 1:
        Thread.update(likes=Thread.likes+1, points=Thread.points+1).where(Thread.id==data['thread']).execute()
    else:
        Thread.update(dislikes=Thread.likes+1, points=Thread.points-1).where(Thread.id==data['thread']).execute()
    result = thread_json_by_id(data['thread'], False, False)
    return normal_json(result)

@post('/db/api/thread/subscribe/')
def thread_subscribe():
    data = request.json
    subscribe, created = SubscribeThread.create_or_get(subscriber=data['user'],
                                                       thread=data['thread'])
    return normal_json( { 'user': data['user'], 'thread': data['thread']} )

@post('/db/api/thread/unsubscribe/')
def thread_unsubscribe():
    data = request.json
    SubscribeThread.delete().where(SubscribeThread.subscriber==data['user'],
                                   SubscribeThread.thread==data['thread']).execute()
    return normal_json( { 'user': data['user'], 'thread': data['thread']} )
