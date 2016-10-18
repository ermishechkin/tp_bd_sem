from database import User, Forum, Post, Thread, SubscribeThread, FollowUser



def _forum_details(forum, related):
    result = forum.json(recurse=False)
    result['user'] = _user_details(User.get(User.id==result['user']))
    if 'user' not in related:
        result['user'] = result['user']['email']
    return result

def _post_details(post, related):
    result = post.json(recurse=False)
    result['points'] = result['likes'] - result['dislikes']
    result['user'] = _user_details(User.get(User.id==result['user']))
    if 'user' not in related:
        result['user'] = result['user']['email']
    result['thread'] = _thread_details(Thread.get(Thread.id==result['thread']), [])
    if 'thread' not in related:
        result['thread'] = result['thread']['id']
    result['forum'] = _forum_details(Forum.get(Forum.id==result['forum']), [])
    if 'forum' not in related:
        result['forum'] = result['forum']['short_name']
    return result

def _thread_details(thread, related):
    result = thread.json(recurse=False)
    result['user'] = _user_details(User.get(User.id==result['user']))
    if 'user' not in related:
        result['user'] = result['user']['email']
    result['forum'] = _forum_details(Forum.get(Forum.id==result['forum']), [])
    if 'forum' not in related:
        result['forum'] = result['forum']['short_name']
    posts = thread.post_set.where(Post.isDeleted==False)
    result['points'] = result['likes'] - result['dislikes']
    result['posts'] = posts.count()
    return result

def _user_details(user):
    followers = [x.follower.email for x in user.followees]
    followees = [x.followee.email for x in user.followers]
    subscriptions = [int(x['id']) for x in SubscribeThread.select(Thread.id). \
                     join(Thread).where(SubscribeThread.subscriber==user). \
                     dicts().execute()]
    result = user.json()
    result['followers'] = followers
    result['following'] = followees
    result['subscriptions'] = subscriptions
    return result
