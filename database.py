from peewee import CharField, BooleanField, ForeignKeyField, DateTimeField, TextField, CompositeKey, IntegerField
from peewee import Model, DeleteQuery
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import model_to_dict
from datetime import datetime
from peewee import decimal
database = PooledMySQLDatabase('bd_sem', user='root', password='nfs2378')

class BaseModel(Model):
    class Meta:
        database = database

    def json(self, **kwargs):
        res = model_to_dict(self, max_depth=2, **kwargs)
        return my_json(res)

class User(BaseModel):
    username = CharField(null=True)
    about = TextField(null=True)
    name = CharField(null=True)
    email = CharField(unique=True)
    isAnonymous = BooleanField(default=False)
    class Meta:
        indexes = (
            (('email', 'id'), False),
            (('name', 'email'), False),
        )

class Forum(BaseModel):
    name = CharField()
    short_name = CharField(unique=True, index=True)
    user = CharField()

class Thread(BaseModel):
    forum = CharField()
    title = CharField()
    isClosed = BooleanField()
    user = CharField()
    date = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    message = TextField()
    slug = CharField()
    isDeleted = BooleanField(default=False)
    likes = IntegerField(null=False, default=0)
    dislikes = IntegerField(null=False, default=0)
    points = IntegerField(null=False, default=0)
    posts = IntegerField(null=False, default=0)
    class Meta:
        indexes = (
            (('forum', 'date'), False),
            (('user', 'date'), False),
        )

class Post(BaseModel):
    date = DateTimeField()
    thread = IntegerField()
    message = TextField()
    user = CharField()
    forum = CharField()

    parent = IntegerField(null=True)
    isApproved = BooleanField()
    isHighlighted = BooleanField()
    isEdited = BooleanField()
    isSpam = BooleanField()
    isDeleted = BooleanField()

    likes = IntegerField(null=False, default=0)
    dislikes = IntegerField(null=False, default=0)
    points = IntegerField(null=False, default=0)

    class Meta:
        indexes = (
            (('user', 'date'), False),
            (('forum', 'date'), False),
            (('thread', 'date'), False),
            (('user', 'forum'), False),
            (('thread', 'parent', 'date'), False),
        )


class FollowUser(BaseModel):
    follower = CharField()
    followee = CharField()
    class Meta:
        primary_key = CompositeKey('follower', 'followee')
        indexes = (
            (('followee', ), False),
        )

class SubscribeThread(BaseModel):
    subscriber = CharField()
    thread = IntegerField()
    class Meta:
        primary_key = CompositeKey('subscriber', 'thread')


def init_db():
    database.create_tables([User,Thread,Forum,Post,FollowUser,SubscribeThread], safe=True)

def clear_db():
    database.truncate_tables([User,Thread,Forum,Post,FollowUser,SubscribeThread])

def recreate_db():
    database.drop_tables([User,Thread,Forum,Post,FollowUser,SubscribeThread])
    init_db()



def my_json(query, **kwargs):
    def change(t):
        for i in t:
            if type(t[i])==datetime:
                t[i]=t[i].strftime('%Y-%m-%d %H:%M:%S')
            elif type(t[i])==decimal.Decimal:
                t[i]=int(t[i])
            elif type(t[i])==list or type(t[i])==dict:
                change(t[i])
            elif i in ['following', 'followers']:
                if t[i]:
                    t[i] = t[i].split(',')
                else:
                    t[i] = []
            elif i == 'subscriptions':
                r = []
                if t[i] is not None:
                    for u in t[i].split(','):
                        if u != '':
                            r.append(int(u))
                t[i] = r

    res = { x:query[x] for x in query }
    change(res)
    return res

class NotExist(Exception):
    def __init__(self, description=""):
        self.description = description
