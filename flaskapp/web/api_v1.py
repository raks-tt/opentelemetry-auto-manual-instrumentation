import flask
from flaskapp.common.testing_decorator import instrument_tracing

api_v1 = flask.Blueprint("api_v1", __name__)


@api_v1.route("/hello")
def hello_world():
    res = do_sum(1, 2)
    test_changes()
    alist = [{"a": 1, "b": 2}, 2020202]
    redo_changes(request_id=123, user_name="test_user", args=alist)
    print("res: ", res)
    return "Hello, World!"


@api_v1.route("/vitals")
def hello_vitals():
    return "Hello, Vitals!"


@instrument_tracing(span_name="do_sum")
def do_sum(a, b):
    return a + b


def test_changes():
    print("test_changes")


@instrument_tracing(span_name="redo_changes")
def redo_changes(request_id=0, user_name=None, args=[]):
    print("redo_changes")
