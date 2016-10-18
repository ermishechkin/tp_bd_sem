from database import Post, User, Forum
from database import my_json
from peewee import fn

def _post_list(root, limit=None):
    query = Post.select(Post,(Post.likes-Post.dislikes).alias('points'))
    query = query.where(Post.parent_id==root)
    query = query.annotate(User, User.email.alias('user'))
    query = query.annotate(Forum, Forum.short_name.alias('forum'))
    query = query.order_by(+Post.date)
    if limit:
        query = query.limit(limit)
    query = query.dicts()

    result = []
    for x in query.execute():
        result.append(my_json(x))
        result += _post_list(x['id'])
    return result
