from bottle import run, default_app, hook
from handlers import common_handlers, user_handlers, forum_handlers, post_handlers, thread_handlers
from database import database

@hook('before_request')
def _connect_db():
    database.connect()

@hook('after_request')
def _close_db():
    if not database.is_closed():
        database.close()

if __name__ == "__main__":
    run(host='localhost', port=8083, debug=True)

app = default_app()
