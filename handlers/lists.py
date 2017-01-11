from database import Post, User, Forum
from database import my_json
from peewee import fn

def _post_list(root, limit=None):
    query = Post.select()
    query = query.where(Post.parent==root)
    query = query.order_by(+Post.date)
    if limit:
        query = query.limit(limit)
    query = query.dicts()
    res = []
    left = limit
    for x in query.execute():
        if left == 0:
            break
        res.append(my_json(x))
        left = left-1 if left is not None else None
        if left == 0:
            break
        t = _post_list(x['id'], left)
        res += t
        left = left-len(t) if left is not None else None
    return res

