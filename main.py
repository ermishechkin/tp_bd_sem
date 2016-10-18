from bottle import run, default_app
from handlers import common_handlers, user_handlers, forum_handlers, post_handlers, thread_handlers

if __name__ == "__main__":
    run(host='localhost', port=8083, debug=True)

app = default_app()
