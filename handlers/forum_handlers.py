from bottle import get, post, request
from database import Forum, User, Post, Thread, FollowUser, SubscribeThread
from common_handlers import normal_json, check_related
from details import _user_details, _post_details, _forum_details, _thread_details
from detail2 import *
from database import my_json
from peewee import fn, JOIN

@post('/db/api/forum/create/')
def forum_create():
    data = request.json
    forum, created = Forum.create_or_get(**data)
    result = forum.json()
    return normal_json(result)

@get('/db/api/forum/details/')
def forum_details():
    data = request.GET
    related = data.getall('related')
    if not check_related(related, ['user']):
        return { "code": 3, "response": "Semantic error" }
    try:
        result = forum_json_by_short_name(data['forum'], 'user' in related)
    except Exception as e:
        return { "code": 1, "response": "" }
    else:
        return normal_json(result)

@get('/db/api/forum/listPosts/')
def forum_listPosts():
    data = request.GET
    related = data.getall('related')
    if not check_related(related, ['user', 'thread', 'forum']):
        return { "code": 3, "response": "Semantic error" }

    query = Post.select()
    query = query.where(Post.forum==data['forum'])
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
    res = post_json_by_query(query, 'user' in related, 'thread' in related, 'forum' in related)
    return normal_json(res)

@get('/db/api/forum/listThreads/')
def forum_listThreads():
    data = request.GET
    related = data.getall('related')
    if not check_related(related, ['user', 'forum']):
        return { "code": 3, "response": "Semantic error" }

    query = Thread.select()
    query = query.where(Thread.forum==data['forum'])
    query = query.group_by(Thread.id)
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
    result = thread_json_by_query(query, 'user' in related, 'forum' in related)
    return normal_json(result)

@get('/db/api/forum/listUsers/')
def forum_listUsers():
    data = request.GET
    query = Post.select(User).distinct().dicts()
    query = query.where(Post.forum==data['forum'])
    query = query.join(User, on=User.email==Post.user)

    if 'since_id' in data:
        query = query.where(User.id >= data['since_id'])

    if 'order' not in data or data['order'] == 'desc':
        sort_order = -User.name
    elif data['order'] == 'asc':
        sort_order = +User.name
    else:
        return { "code": 3, "response": "Semantic error" }
    query = query.order_by(sort_order)

    if 'limit' in data:
        query = query.limit(data['limit'])

    result = []
    for post in query.execute():
        FollowUserAlias = FollowUser.alias()

        q = User.select(fn.group_concat(fn.distinct(SubscribeThread.thread)).alias('subscriptions').coerce(False),
                        fn.group_concat(fn.distinct(FollowUser.followee)).alias('following'),
                        fn.group_concat(fn.distinct(FollowUserAlias.follower)).alias('followers'))
        q = q.join(SubscribeThread, JOIN.LEFT_OUTER, on=SubscribeThread.subscriber==User.email)
        q = q.join(FollowUser, JOIN.LEFT_OUTER, on=FollowUser.follower==User.email)
        q = q.switch(User)
        q = q.join(FollowUserAlias, JOIN.LEFT_OUTER, on=FollowUserAlias.followee==User.email)
        q = q.group_by()
        result.append(my_json(q.dicts.execute().next()))
    return normal_json(result)
