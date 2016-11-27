from bottle import get, post, request
from database import User, Thread, FollowUser, SubscribeThread, Post, Forum
from database import my_json
from peewee import IntegrityError
from common_handlers import normal_json
from peewee import fn, JOIN
from detail2 import *

@post('/db/api/user/create/')
def user_create():
    data = request.json
    try:
        user = User.create(**data)
    except IntegrityError as e:
        return { "code": 5, "response": "User already exists" }
    else:
        return normal_json(user.json())

@post('/db/api/user/updateProfile/')
def user_updateProfile():
    data = request.json
    User.update(name = data['name'],
                about = data['about']).where(User.email==data['user']).execute()
    return normal_json(user_json_by_email(data['user']))

@get('/db/api/user/details/')
def user_details():
    data = request.GET
    return normal_json(user_json_by_email(data['user']))

@post('/db/api/user/follow/')
def user_follow():
    data = request.json
    follow, created = FollowUser.create_or_get(follower=data['follower'],
                                               followee=data['followee'])
    return normal_json(user_json_by_email(data['follower']))

@post('/db/api/user/unfollow/')
def user_unfollow():
    data = request.json
    FollowUser.delete().where(FollowUser.follower==data['follower'],
                              FollowUser.followee==data['followee']).execute()
    return normal_json(user_json_by_email(data['follower']))

@get('/db/api/user/listFollowers/')
def user_listFollowers():
    data = request.GET

    FollowUserAlias = FollowUser.alias()
    query = user_detail_impl()
    query = query.join(FollowUserAlias, on=FollowUserAlias.follower==User.email)
    query = query.where(FollowUserAlias.followee==data['user'])
    query = query.group_by(User.email, User.id)

    if 'since_id' in data:
        query = query.where(User.id >= data['since_id'])

    order = data['order'] if 'order' in data else 'desc'
    if order == 'desc':
        query = query.order_by(-User.email)
    else:
        query = query.order_by(+User.email)

    if 'limit' in data:
        query = query.limit(data['limit'])

    return normal_json([my_json(i) for i in query.execute()])

@get('/db/api/user/listFollowing/')
def user_listFollowing():
    data = request.GET

    FollowUserAlias = FollowUser.alias()
    query = user_detail_impl()
    query = query.join(FollowUserAlias, on=FollowUserAlias.follower==User.email)
    query = query.where(FollowUserAlias.followee==data['user'])
    query = query.group_by(User.email, User.id)

    if 'since_id' in data:
        query = query.where(User.id >= data['since_id'])

    order = data['order'] if 'order' in data else 'desc'
    if order == 'desc':
        query = query.order_by(-User.email)
    else:
        query = query.order_by(+User.email)

    if 'limit' in data:
        query = query.limit(data['limit'])

    return normal_json([my_json(i) for i in query.execute()])

@get('/db/api/user/listPosts/')
def user_listPosts():
    data = request.GET
    query = Post.select()
    query = query.where(Post.user==data['user'])
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
