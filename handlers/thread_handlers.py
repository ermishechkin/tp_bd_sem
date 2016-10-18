from bottle import get, post, request
from database import Thread, Forum, User, Post, SubscribeThread
from common_handlers import normal_json, check_related
from details import _user_details, _forum_details, _thread_details
from peewee import fn
from database import my_json
from lists import _post_list

@post('/db/api/thread/create/')
def thread_create():
    data = request.json
    data['user'] = User.get(User.email==data['user'])
    data['forum'] = Forum.get(Forum.short_name==data['forum'])
    thread, created = Thread.create_or_get(**data)
    result = thread.json(recurse=False)
    result['user'] = data['user'].email
    result['forum'] = data['forum'].short_name
    return normal_json(result)

@get('/db/api/thread/details/')
def thread_details():
    data = request.GET
    related = data.getall('related')
    if not check_related(related, ['user', 'forum']):
        return { "code": 3, "response": "Semantic error" }
    try:
        thread = Thread.get(Thread.id==data['thread'])
    except Thread.DoesNotExist as e:
        return { "code": 1, "response": "Thread doesn't exists" }
    return normal_json(_thread_details(thread, related))

@get('/db/api/thread/list/')
def thread_list():
    data = request.GET
    query = Thread.select(Thread,(Thread.likes-Thread.dislikes).alias('points'))
    if 'forum' in data:
        query = query.where(Thread.forum==Forum.get(Forum.short_name==data['forum']))
    elif 'user' in data:
        query = query.where(Thread.user==User.get(User.email==data['user']))
    else:
        return { "code": 3, "response": "Semantic error" }
    query = query.annotate(User, User.email.alias('user'))
    query = query.annotate(Forum, Forum.short_name.alias('forum'))
    query = query.annotate(Post, fn.Count(Post.id).alias('posts'))
    # query = query.annotate(Post, fn.Sum(Post.likes).alias('likes'))
    # query = query.annotate(Post, fn.Sum(Post.dislikes).alias('dislikes'))
    # query = query.annotate(Post, (fn.Sum(Post.likes)-fn.Sum(Post.dislikes)).alias('points'))
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
    query = Post.select(Post,(Post.likes-Post.dislikes).alias('points'))
    query = query.where(Post.thread_id==data['thread'])
    query = query.annotate(User, User.email.alias('user'))
    query = query.annotate(Forum, Forum.short_name.alias('forum'))
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
        for x in query.execute():
            res.append(my_json(x))
            res += _post_list(x['id'])
        if 'limit' in data:
            res = res[:int(data['limit'])]

    return normal_json(res)



@post('/db/api/thread/remove/')
def thread_remove():
    data = request.json
    try:
        thread = Thread.get(Thread.id==data['thread'])
    except Thread.DoesNotExist as e:
        return { "code": 1, "response": "Thread doesn't exists" }
    thread.isDeleted = True
    thread.save()
    Post.update(isDeleted=True).where(Post.thread==thread).execute()
    return normal_json( {'thread': thread.id} )

@post('/db/api/thread/restore/')
def thread_restore():
    data = request.json
    try:
        thread = Thread.get(Thread.id==data['thread'])
    except Thread.DoesNotExist as e:
        return { "code": 1, "response": "Thread doesn't exists" }
    thread.isDeleted = False
    thread.save()
    Post.update(isDeleted=False).where(Post.thread==thread).execute()
    return normal_json( {'thread': thread.id} )

@post('/db/api/thread/close/')
def thread_close():
    data = request.json
    try:
        thread = Thread.get(Thread.id==data['thread'])
    except Thread.DoesNotExist as e:
        return { "code": 1, "response": "Thread doesn't exists" }
    thread.isClosed = True
    thread.save()
    return normal_json( {'thread': thread.id} )

@post('/db/api/thread/open/')
def thread_open():
    data = request.json
    try:
        thread = Thread.get(Thread.id==data['thread'])
    except Thread.DoesNotExist as e:
        return { "code": 1, "response": "Thread doesn't exists" }
    thread.isClosed = False
    thread.save()
    return normal_json( {'thread': thread.id} )

@post('/db/api/thread/update/')
def thread_update():
    data = request.json
    try:
        thread = Thread.get(Thread.id==data['thread'])
    except Thread.DoesNotExist as e:
        return { "code": 1, "response": "Thread doesn't exists" }
    thread.message = data['message']
    thread.slug = data['slug']
    thread.save()
    return normal_json(_thread_details(thread, []))

@post('/db/api/thread/vote/')
def thread_vote():
    data = request.json
    try:
        thread = Thread.get(Thread.id==data['thread'])
    except Thread.DoesNotExist as e:
        return { "code": 1, "response": "Thread doesn't exists" }
    if data['vote'] not in [-1, 1]:
        return { "code": 3, "response": "Semantic error" }
    if data['vote'] == 1:
        thread.likes += 1
    else:
        thread.dislikes += 1
    thread.save()
    return normal_json(_thread_details(thread, []))

@post('/db/api/thread/subscribe/')
def thread_subscribe():
    data = request.json
    try:
        thread = Thread.get(Thread.id==data['thread'])
        user = User.get(User.email==data['user'])
    except Thread.DoesNotExist as e:
        return { "code": 1, "response": "Thread or User doesn't exists" }
    SubscribeThread.create_or_get(subscriber=user, thread=thread)
    return normal_json( { 'user': data['user'], 'thread': data['thread']} )

@post('/db/api/thread/unsubscribe/')
def thread_unsubscribe():
    data = request.json
    try:
        thread = Thread.get(Thread.id==data['thread'])
        user = User.get(User.email==data['user'])
    except Thread.DoesNotExist as e:
        return { "code": 1, "response": "Thread or User doesn't exists" }
    SubscribeThread.delete().where(SubscribeThread.subscriber==user, \
                                   SubscribeThread.thread==thread).execute()
    return normal_json( { 'user': data['user'], 'thread': data['thread']} )
