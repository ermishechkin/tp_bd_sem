from bottle import get, post, request
from database import Post, Forum, User, Thread
from common_handlers import normal_json, check_related
from details import _forum_details, _thread_details, _user_details, _post_details
from peewee import fn
from database import my_json

@post('/db/api/post/create/')
def post_create():
    data = request.json
    data['user'] = User.get(User.email==data['user'])
    data['forum'] = Forum.get(Forum.short_name==data['forum'])
    post, created = Post.create_or_get(**data)
    result = post.json(recurse=False)
    result['user'] = data['user'].email
    result['forum'] = data['forum'].short_name
    return normal_json(result)

@get('/db/api/post/details/')
def post_details():
    data = request.GET
    related = data.getall('related')
    if not check_related(related, ['user', 'thread', 'forum']):
        return { "code": 3, "response": "Semantic error" }
    try:
        post = Post.get(Post.id==data['post'])
    except Post.DoesNotExist as e:
        return { "code": 1, "response": "Post doesn't exists" }
    return normal_json(_post_details(post, related))

@get('/db/api/post/list/')
def post_list():
    data = request.GET
    query = Post.select(Post, (Post.likes-Post.dislikes).alias('points'))
    if 'forum' in data:
        query = query.where(Post.forum==Forum.get(Forum.short_name==data['forum']))
    elif 'thread' in data:
        query = query.where(Post.thread_id==data['thread'])
    else:
        return { "code": 3, "response": "Semantic error" }
    query = query.annotate(User, User.email.alias('user'))
    query = query.annotate(Forum, Forum.short_name.alias('forum'))
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
    try:
        post = Post.get(Post.id==data['post'])
    except Post.DoesNotExist as e:
        return { "code": 1, "response": "Post doesn't exists" }
    if data['vote'] not in [-1, 1]:
        return { "code": 3, "response": "Semantic error" }
    if data['vote'] == 1:
        post.likes += 1
    else:
        post.dislikes += 1
    post.save()
    return normal_json(_post_details(post, []))

@post('/db/api/post/remove/')
def post_remove():
    data = request.json
    try:
        post = Post.get(Post.id==data['post'])
    except Post.DoesNotExist as e:
        return { "code": 1, "response": "Post doesn't exists" }
    post.isDeleted = True
    post.save()
    return normal_json( {'post': post.id} )

@post('/db/api/post/restore/')
def post_restore():
    data = request.json
    try:
        post = Post.get(Post.id==data['post'])
    except Post.DoesNotExist as e:
        return { "code": 1, "response": "Post doesn't exists" }
    post.isDeleted = False
    post.save()
    return normal_json( {'post': post.id} )

@post('/db/api/post/update/')
def post_update():
    data = request.json
    try:
        post = Post.get(Post.id==data['post'])
    except Post.DoesNotExist as e:
        return { "code": 1, "response": "Post doesn't exists" }
    post.message = data['message']
    post.save()
    return normal_json(_post_details(post, []))
