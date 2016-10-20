from peewee import CharField, BooleanField, ForeignKeyField, DateTimeField, TextField, CompositeKey, IntegerField
from peewee import Model, DeleteQuery
from peewee import MySQLDatabase
from playhouse.shortcuts import model_to_dict
from datetime import datetime
from peewee import decimal
database = MySQLDatabase('bd_sem', user='root', password='nefosp')

class BaseModel(Model):
    class Meta:
        database = database

    def json(self, **kwargs):
        res = model_to_dict(self, max_depth=2, **kwargs)
        def change(t):
            for i in t:
                if type(t[i])==datetime:
                    t[i]=t[i].strftime('%Y-%m-%d %H:%M:%S')
                elif type(t[i])==decimal.Decimal:
                    t[i]=int(t[i])
                elif type(t[i])==list or type(t[i])==dict:
                    change(t[i])
        change(res)
        return res

class User(BaseModel):
    username = CharField(null=True)
    about = TextField(null=True)
    name = CharField(null=True)
    email = CharField(unique=True, index=True)
    isAnonymous = BooleanField(default=False)

class Forum(BaseModel):
    name = CharField(unique=True)
    short_name = CharField(unique=True, index=True)
    user = ForeignKeyField(User, on_delete='CASCADE')

class Thread(BaseModel):
    forum = ForeignKeyField(Forum, on_delete='CASCADE')
    title = CharField()
    isClosed = BooleanField()
    user = ForeignKeyField(User, on_delete='CASCADE')
    date = DateTimeField(formats='%Y-%m-%d %H:%M:%S')
    message = TextField()
    slug = CharField()
    isDeleted = BooleanField(default=False)
    likes = IntegerField(null=False, default=0)
    dislikes = IntegerField(null=False, default=0)

class Post(BaseModel):
    date = DateTimeField()
    thread = ForeignKeyField(Thread, on_delete='CASCADE')
    message = TextField()
    user = ForeignKeyField(User, on_delete='CASCADE')
    forum = ForeignKeyField(Forum, on_delete='CASCADE')

    parent = ForeignKeyField('self', null=True, on_delete='CASCADE')
    isApproved = BooleanField()
    isHighlighted = BooleanField()
    isEdited = BooleanField()
    isSpam = BooleanField()
    isDeleted = BooleanField()

    likes = IntegerField(null=False, default=0)
    dislikes = IntegerField(null=False, default=0)

class FollowUser(BaseModel):
    follower = ForeignKeyField(User, related_name='followers', on_delete='CASCADE')
    followee = ForeignKeyField(User, related_name='followees', on_delete='CASCADE')
    class Meta:
        primary_key = CompositeKey('follower', 'followee')

class SubscribeThread(BaseModel):
    subscriber = ForeignKeyField(User, related_name='subscriptions', on_delete='CASCADE')
    thread = ForeignKeyField(Thread, on_delete='CASCADE')
    class Meta:
        primary_key = CompositeKey('subscriber', 'thread')

# class VotePost(BaseModel):
#     voter = ForeignKeyField(User, related_name='votes', on_delete='CASCADE')
#     post = ForeignKeyField(Post, on_delete='CASCADE')
#     vote = SmallIntegerField()
#     class Meta:
#         primary_key = CompositeKey('voter', 'post')


def init_db():
    database.create_tables([User,Thread,Forum,Post,FollowUser,SubscribeThread], safe=True)

def clear_db():
    DeleteQuery(User).execute()
    DeleteQuery(Thread).execute()
    DeleteQuery(Forum).execute()
    DeleteQuery(Post).execute()
    DeleteQuery(FollowUser).execute()
    DeleteQuery(SubscribeThread).execute()

def recreate_db():
    database.drop_tables([User,Thread,Forum,Post,FollowUser,SubscribeThread])
    init_db()



def my_json(query, **kwargs):
    res = { x:query[x] for x in query }
    def change(t):
        for i in t:
            if type(t[i])==datetime:
                t[i]=t[i].strftime('%Y-%m-%d %H:%M:%S')
            elif type(t[i])==decimal.Decimal:
                t[i]=int(t[i])
            elif type(t[i])==list or type(t[i])==dict:
                change(t[i])
    change(res)
    return res
