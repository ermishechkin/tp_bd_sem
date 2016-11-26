from database import User, Forum, Post, Thread, SubscribeThread, FollowUser
from peewee import fn, JOIN, SQL
from database import my_json

def user_detail_impl():
    FollowUserAlias = FollowUser.alias()

    query = User.select()

    query = query.join(SubscribeThread, JOIN.LEFT_OUTER, on=SubscribeThread.subscriber==User.email)
    query = query.annotate(SubscribeThread, fn.group_concat(SubscribeThread.thread).alias('subscriptions').coerce(False))

    query = query.join(FollowUser, JOIN.LEFT_OUTER, on=FollowUser.follower==User.email)
    query = query.annotate(FollowUser, fn.group_concat(FollowUser.followee).alias('following'))

    query = query.switch(User)

    query = query.join(FollowUserAlias, JOIN.LEFT_OUTER, on=FollowUserAlias.followee==User.email)
    query = query.annotate(FollowUserAlias, fn.group_concat(FollowUserAlias.follower).alias('followers'))

    query = query.group_by()

    return query.dicts()

def user_json_by_email(email):
    query = user_detail_impl().where(User.email==email)
    # raise Exception(query.sql())
    return my_json(query.execute().next())

def forum_json_by_short_name(short_name, related_user):
    selected_fields = [Forum]
    query = Forum.select().where(Forum.short_name==short_name)
    if related_user:
        FollowUserAlias = FollowUser.alias()
        selected_fields += [
            User.id.alias('user__id'),
            User.username.alias('user__username'),
            User.about.alias('user__about'),
            User.name.alias('user__name'),
            User.email.alias('user__email'),
            User.isAnonymous.alias('user__isAnonymous'),
            fn.group_concat(SubscribeThread.thread).alias('user__subscriptions').coerce(False),
            fn.group_concat(FollowUser.followee).alias('user__following'),
            fn.group_concat(FollowUserAlias.follower).alias('user__followers')
        ]
        query = query.join(User, on=User.email==Forum.user)
        query = query.join(SubscribeThread, JOIN.LEFT_OUTER, on=SubscribeThread.subscriber==User.email)
        query = query.join(FollowUser, JOIN.LEFT_OUTER, on=FollowUser.follower==User.email)
        query = query.join(FollowUserAlias, JOIN.LEFT_OUTER, on=FollowUserAlias.followee==User.email)
    query = query.select(*selected_fields)
    return my_json(query.dicts().execute().next())


def thread_json_by_query(query, related_user, related_forum):
    selected_fields = [Thread]
    if related_user:
        FollowUserAlias = FollowUser.alias()
        selected_fields += [
            User.id.alias('user__id'),
            User.username.alias('user__username'),
            User.about.alias('user__about'),
            User.name.alias('user__name'),
            User.email.alias('user__email'),
            User.isAnonymous.alias('user__isAnonymous'),
            fn.group_concat(SubscribeThread.thread).alias('user__subscriptions').coerce(False),
            fn.group_concat(FollowUser.followee).alias('user__following'),
            fn.group_concat(FollowUserAlias.follower).alias('user__followers')
        ]
        query = query.join(User, on=User.email==Thread.user)
        query = query.join(SubscribeThread, JOIN.LEFT_OUTER, on=SubscribeThread.subscriber==User.email)
        query = query.join(FollowUser, JOIN.LEFT_OUTER, on=FollowUser.follower==User.email)
        query = query.join(FollowUserAlias, JOIN.LEFT_OUTER, on=FollowUserAlias.followee==User.email)

    if related_forum:
        selected_fields += [
            Forum.id.alias('forum__id'),
            Forum.name.alias('forum__name'),
            Forum.short_name.alias('forum__short_name'),
            Forum.user.alias('forum__user'),
        ]
        query = query.join(Forum, on=Forum.short_name==Thread.forum)

    query = query.select(*selected_fields)
    # raise Exception(query.sql())
    return [my_json(i) for i in query.dicts().execute()]


def thread_json_by_id(id, related_user, related_forum):
    query = Thread.select().where(Thread.id==id)
    return thread_json_by_query(query, related_user, related_forum)[0]


def post_json_by_query(query, related_user, related_thread, related_forum):
    selected_fields = [Post]
    if related_user:
        FollowUserAlias = FollowUser.alias()
        selected_fields += [
            User.id.alias('user__id'),
            User.username.alias('user__username'),
            User.about.alias('user__about'),
            User.name.alias('user__name'),
            User.email.alias('user__email'),
            User.isAnonymous.alias('user__isAnonymous'),
            fn.group_concat(SubscribeThread.thread).alias('user__subscriptions').coerce(False),
            fn.group_concat(FollowUser.followee).alias('user__following'),
            fn.group_concat(FollowUserAlias.follower).alias('user__followers')
        ]
        query = query.join(User, on=User.email==Post.user)
        query = query.join(SubscribeThread, JOIN.LEFT_OUTER, on=SubscribeThread.subscriber==User.email)
        query = query.join(FollowUser, JOIN.LEFT_OUTER, on=FollowUser.follower==User.email)
        query = query.join(FollowUserAlias, JOIN.LEFT_OUTER, on=FollowUserAlias.followee==User.email)

    if related_thread:
        selected_fields += [
            Thread.id.alias('thread__id'),
            Thread.forum.alias('thread__forum'),
            Thread.title.alias('thread__title'),
            Thread.isClosed.alias('thread__isClosed'),
            Thread.user.alias('thread__user'),
            Thread.date.alias('thread__date'),
            Thread.message.alias('thread__message'),
            Thread.slug.alias('thread__slug'),
            Thread.isDeleted.alias('thread__isDeleted'),
            Thread.likes.alias('thread__likes'),
            Thread.dislikes.alias('thread__dislikes'),
            Thread.points.alias('thread__points'),
            Thread.posts.alias('thread__posts'),
        ]
        query = query.join(Thread, on=Thread.id==Post.thread)
    if related_forum:
        selected_fields += [
            Forum.id.alias('forum__id'),
            Forum.name.alias('forum__name'),
            Forum.short_name.alias('forum__short_name'),
            Forum.user.alias('forum__user'),
        ]
        query = query.join(Forum, on=Forum.short_name==Post.forum)
    query = query.select(*selected_fields)
    return [my_json(i) for i in query.dicts().execute()]

def post_json_by_id(id, related_user, related_thread, related_forum):
    query = Post.select().where(Post.id==id)
    result = post_json_by_query(query, related_user, related_thread, related_forum)
    return result[0]
