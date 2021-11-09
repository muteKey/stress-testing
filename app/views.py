import functools

from flask import (
    Blueprint, flash, g, redirect, request, session, url_for
)

from app.db import get_db

bp = Blueprint('views', __name__, url_prefix='/')


def save_request(request):
    db = get_db()
    try:
        db.execute("INSERT INTO request (url, body, method) VALUES (?, ?, ?)",
            (request.url,request.data, request.method)
        )
        db.commit()
    except db.IntegrityError:
        error = f"Cannot save request"

@bp.route('/', methods=('GET', 'POST'))
def index():
    save_request(request)
    return "<h1>This is index page</h1>"

@bp.route('/hello', methods=('GET', 'POST'))
def hello():
    save_request(request)
    return "<h1>This is greeting page</h1>"
