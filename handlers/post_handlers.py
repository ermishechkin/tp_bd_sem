from bottle import get, post, request
from database import Post, Forum, User, Thread
from common_handlers import normal_json, check_related
from details import _forum_details, _thread_details, _user_details, _post_details
from peewee import fn
from database import my_json
from detail2 import *

@post('/db/api/post/create/')
def post_create():
    data = request.json
    post, created = Post.create_or_get(**data)
    Thread.update(posts=Thread.posts+1).where(Thread.id==post.thread).execute()
    result = post.json()
    return normal_json(result)

@get('/db/api/post/details/')
def post_details():
    data = request.GET
    related = data.getall('related')
    if not check_related(related, ['user', 'thread', 'forum']):
        return { "code": 3, "response": "Semantic error" }
    try:
        result = post_json_by_id(data['post'], 'user' in related, 'thread' in related, 'forum' in related)
    except:
        return { "code": 1, "response": "" }
    else:
        return normal_json(result)

@get('/db/api/post/list/')
def post_list():
    data = request.GET
    query = Post.select()
    if 'forum' in data:
        query = query.where(Post.forum==data['forum'])
    elif 'thread' in data:
        query = query.where(Post.thread==data['thread'])
    else:
        return { "code": 3, "response": "Semantic error" }
    query = query.dicts()
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
    return normal_json(res)

@post('/db/api/post/vote/')
def post_vote():
    data = request.json
    if data['vote'] not in [-1, 1]:
        return { "code": 3, "response": "Semantic error" }
    if data['vote'] == 1:
        Post.update(likes=Post.likes+1, points=Post.points+1).where(Post.id==data['post']).execute()
    else:
        Post.update(dislikes=Post.likes+1, points=Post.points-1).where(Post.id==data['post']).execute()
    result = post_json_by_id(data['post'], False, False, False)
    return normal_json(result)

@post('/db/api/post/remove/')
def post_remove():
    data = request.json
    Post.update(isDeleted = True).where(Post.id==data['post']).execute()
    thread_id = Post.select(Post.thread).where(Post.id==data['post']).scalar()
    Thread.update(posts=Thread.posts-1).where(Thread.id==thread_id).execute()
    return normal_json( {'post': data['post']} )

@post('/db/api/post/restore/')
def post_restore():
    data = request.json
    Post.update(isDeleted = False).where(Post.id==data['post']).execute()
    thread_id = Post.select(Post.thread).where(Post.id==data['post']).scalar()
    Thread.update(posts=Thread.posts+1).where(Thread.id==thread_id).execute()
    return normal_json( {'post': data['post']} )

@post('/db/api/post/update/')
def post_update():
    data = request.json
    Post.update(message = data['message']).where(Post.id==data['post']).execute()
    result = post_json_by_id(data['post'], False, False, False)
    return normal_json(result)
