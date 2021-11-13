from flask import (
    Blueprint, request
)

from .repo import Repository

bp = Blueprint('views', __name__, url_prefix='/')

repository = Repository()

@bp.route('/', methods=('GET', 'POST'))
def index():
    repository.save_request(request)
    print(request.path)
    result = repository.get_metrics(request)
    if result:
        return f"<h1>Metric for index page is {result}</h1>"
    return "<h1>This is index page</h1>"

@bp.route('/hello', methods=('GET', 'POST'))
def hello():
    repository.save_request(request)
    result = repository.get_metrics(request)
    if result:
        return f"<h1>Metric for hello page is {result}</h1>"
    return "<h1>This is greeting page</h1>"
