from bottle import get, post, request
from database import User, Thread, FollowUser, SubscribeThread, Post, Forum
from database import my_json
from peewee import IntegrityError
from common_handlers import normal_json
from details import _user_details

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
    user = User.select().where(User.email==data['user']).first()
    user.name = data['name']
    user.about = data['about']
    user.save()
    return normal_json(_user_details(user))

@get('/db/api/user/details/')
def user_details():
    data = request.GET
    user = User.select().where(User.email==data['user']).first()
    return normal_json(_user_details(user))

@post('/db/api/user/follow/')
def user_follow():
    data = request.json
    follower = User.select().where(User.email==data['follower']).first()
    followee = User.select().where(User.email==data['followee']).first()

    follow, created = FollowUser.get_or_create(follower=follower,
                                               followee=followee)
    return normal_json(_user_details(follower))

@post('/db/api/user/unfollow/')
def user_unfollow():
    data = request.json
    follower = User.get(User.email==data['follower'])
    followee = User.get(User.email==data['followee'])

    follow = FollowUser.delete().where(FollowUser.follower==follower,
                                       FollowUser.followee==followee).execute()
    return normal_json(_user_details(follower))

@get('/db/api/user/listFollowers/')
def user_listFollowers():
    data = request.GET
    user = User.get(User.email==data['user'])
    query = User.select().join(FollowUser, on=User.id==FollowUser.follower_id).\
                 where(FollowUser.followee_id==user.id)

    if 'since_id' in data:
        query = query.where(FollowUser.follower>=data['since_id'])

    order = data['order'] if 'order' in data else 'desc'
    if order == 'desc':
        query = query.order_by(-User.email)
    else:
        query = query.order_by(+User.email)

    if 'limit' in data:
        query = query.limit(data['limit'])

    followers = [_user_details(x) for x in query]
    return normal_json(followers)

@get('/db/api/user/listFollowing/')
def user_listFollowing():
    data = request.GET
    user = User.get(User.email==data['user'])

    query = User.select().join(FollowUser, on=User.id==FollowUser.followee_id).\
                 where(FollowUser.follower_id==user.id)

    if 'since_id' in data:
        query = query.where(FollowUser.followee>=data['since_id'])

    order = data['order'] if 'order' in data else 'desc'
    if order == 'desc':
        query = query.order_by(-User.email)
    else:
        query = query.order_by(+User.email)

    if 'limit' in data:
        query = query.limit(data['limit'])

    followees = [_user_details(x) for x in query]
    return normal_json(followees)

@get('/db/api/user/listPosts/')
def user_listPosts():
    data = request.GET
    query = Post.select(Post, (Post.likes-Post.dislikes).alias('points'))
    query = query.where(Post.user==User.get(User.email==data['user']))
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
