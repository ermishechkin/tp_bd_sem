from bottle import get, post, request
from database import Forum, User, Post, Thread
from common_handlers import normal_json, check_related
from details import _user_details, _post_details, _forum_details, _thread_details

@post('/db/api/forum/create/')
def forum_create():
    data = request.json
    user = User.get(User.email==data['user'])
    data['user'] = user
    forum, created = Forum.create_or_get(**data)
    result = forum.json(recurse=False)
    result['user'] = data['user'].email
    return normal_json(result)

@get('/db/api/forum/details/')
def forum_details():
    data = request.GET
    related = data.getall('related')
    if not check_related(related, ['user']):
        return { "code": 3, "response": "Semantic error" }
    forum = Forum.get(Forum.short_name==data['forum'])
    return normal_json(_forum_details(forum, related))

@get('/db/api/forum/listPosts/')
def forum_listPosts():
    data = request.GET
    forum = Forum.get(Forum.short_name==data['forum'])
    related = data.getall('related')
    if not check_related(related, ['user', 'thread', 'forum']):
        return { "code": 3, "response": "Semantic error" }
    query = Post.select()
    query = query.where(Post.forum==forum)
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
    res = [_post_details(x, related) for x in query.execute()]
    return normal_json(res)

@get('/db/api/forum/listThreads/')
def forum_listThreads():
    data = request.GET
    forum = Forum.get(Forum.short_name==data['forum'])
    related = data.getall('related')
    if not check_related(related, ['user', 'forum']):
        return { "code": 3, "response": "Semantic error" }
    query = Thread.select()
    query = query.where(Thread.forum==forum)
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
    res = [_thread_details(x, related) for x in query.execute()]
    return normal_json(res)

@get('/db/api/forum/listUsers/')
def forum_listUsers():
    data = request.GET
    forum = Forum.get(Forum.short_name==data['forum'])
    query = User.select(User).distinct() \
                .join(Post) \
                .where(Post.forum==forum)
    if 'since_id' in data:
        query = query.where(User.id>=data['since_id'])
    if 'limit' in data:
        query = query.limit(data['limit'])
    if 'order' not in data or data['order'] == 'desc':
        query = query.order_by(-User.name)
    elif data['order'] == 'asc':
        query = query.order_by(+User.name)
    else:
        return { "code": 3, "response": "Semantic error" }
    res = [_user_details(x) for x in query.execute()]
    return normal_json(res)
