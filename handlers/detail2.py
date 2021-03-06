from database import User, Forum, Post, Thread, SubscribeThread, FollowUser
from peewee import fn, JOIN, SQL
from database import my_json

def user_detail_impl():
    FollowUserAlias = FollowUser.alias()

    query = User.select()

    query = query.join(SubscribeThread, JOIN.LEFT_OUTER, on=SubscribeThread.subscriber==User.email)
    query = query.annotate(SubscribeThread, fn.group_concat(fn.distinct(SubscribeThread.thread)).alias('subscriptions').coerce(False))

    query = query.join(FollowUser, JOIN.LEFT_OUTER, on=FollowUser.follower==User.email)
    query = query.annotate(FollowUser, fn.group_concat(fn.distinct(FollowUser.followee)).alias('following'))

    query = query.switch(User)

    query = query.join(FollowUserAlias, JOIN.LEFT_OUTER, on=FollowUserAlias.followee==User.email)
    query = query.annotate(FollowUserAlias, fn.group_concat(fn.distinct(FollowUserAlias.follower)).alias('followers'))

    query = query.group_by(User.email, User.id)

    return query.dicts()

def user_json_by_email(email):
    FollowUserAlias = FollowUser.alias()
    query = User.select().dicts()
    query = query.where(User.email==email)
    user = my_json(query.execute().next())

    subscriptions = SubscribeThread.select(SubscribeThread.thread).dicts()
    subscriptions = subscriptions.where(SubscribeThread.subscriber==user['email'])
    user['subscriptions'] = [i['thread'] for i in subscriptions]

    following = FollowUser.select(FollowUser.followee).dicts()
    following = following.where(FollowUser.follower==user['email'])
    user['following'] = [i['followee'] for i in following]

    followers = FollowUser.select(FollowUser.follower).dicts()
    followers = followers.where(FollowUser.followee==user['email'])
    user['followers'] = [i['follower'] for i in followers]

    return user

def forum_json_by_short_name(short_name, related_user):
    query = Forum.select().where(Forum.short_name==short_name)
    forum = my_json(query.dicts().execute().next())
    if related_user:
        forum['user'] = user_json_by_email(forum['user'])
    return forum


def thread_json_by_query(query, related_user, related_forum):
    result = []
    for t in query.dicts().execute():
        thread = my_json(t)
        if related_user:
            thread['user'] = user_json_by_email(thread['user'])
        if related_forum:
            thread['forum'] = forum_json_by_short_name(thread['forum'], False)
        result.append(thread)
    return result


def thread_json_by_id(id, related_user, related_forum):
    query = Thread.select().where(Thread.id==id)
    return thread_json_by_query(query, related_user, related_forum)[0]


def post_json_by_query(query, related_user, related_thread, related_forum):
    result = []
    for p in query.dicts().execute():
        post = my_json(p)
        if related_user:
            post['user'] = user_json_by_email(post['user'])
        if related_thread:
            post['thread'] = thread_json_by_id(post['thread'], False, False)
        if related_forum:
            post['forum'] = forum_json_by_short_name(post['forum'], False)
        result.append(post)
    return result

def post_json_by_id(id, related_user, related_thread, related_forum):
    query = Post.select().where(Post.id==id)
    result = post_json_by_query(query, related_user, related_thread, related_forum)
    return result[0]
