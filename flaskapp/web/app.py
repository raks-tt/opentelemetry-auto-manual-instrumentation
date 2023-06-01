from flask import Flask
from .api_v1 import api_v1
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from flaskapp.common.testing_decorator import TracingWrapper


def create_app():
    app = Flask(__name__)
    tracerWrapper = TracingWrapper()
    FlaskInstrumentor().instrument_app(
        app,
        enable_commenter=True,
        commenter_options={},
        tracer_provider=tracerWrapper.provider,
    )
    app.register_blueprint(api_v1, url_prefix="/api/v1")
    return app
