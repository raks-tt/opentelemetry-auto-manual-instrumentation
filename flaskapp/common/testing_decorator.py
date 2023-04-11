"""
Configures the Global Tracer Provider and exports the traces to the
OpenTelemetry Collector. The OpenTelemetry Collector is configured to
receive traces via OTLP over HTTP
"""
import functools
import inspect
import logging
from flask import request, current_app
from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import Tracer
from opentelemetry.sdk.trace.export import ConsoleSpanExporter
from opentelemetry.trace.propagation.tracecontext import (
    TraceContextTextMapPropagator,
)
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
)

log = logging.getLogger(__name__)


class TracingWrapper:
    """
    Wrapper class to initialize the trace provider and tracer.
    """

    def __init__(self, tracer: Tracer = None):
        if tracer is not None:
            self.tracer = tracer
        else:
            self.initialize_instrumentation()

    def initialize_instrumentation(self):
        """
        Initialize the instrumentation.
        """
        exporter = ConsoleSpanExporter()
        provider = TracerProvider(
            resource=Resource.create({SERVICE_NAME: "TESTING_DECORATOR"})
        )
        trace.set_tracer_provider(provider)
        self.tracer = trace.get_tracer(__name__)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)


def instrument_tracing(
    func=None,
    *,
    service_name: str = "",
    span_name: str = "",
    ignoreTracing=False,
    is_class=False,
):
    """
    Decorator to instrument a function or class with tracing.
    :param service_name: The name of the service to be used.
    :param span_name: The name of the span to be created.
    :param ignoreTracing: If True, the function will not be traced.
    :return: The decorated function or class.
    """

    def instrument_class(cls):
        """
        Filters out all the methods that are to be instrumented
        for a class with tracing.

        :param cls: The class to be decorated.
        :return: The decorated class.
        """
        for name, method in cls.__dict__.items():
            if (
                callable(method)
                and not method.__name__.startswith("_")
                and not inspect.isclass(method)
            ):
                setattr(cls, name, instrument_tracing(method))
        return cls

    def instrument_span(func):
        """
        Decorator to instrument a function with tracing.
        """
        print("Instrumenting span", span_name)
        propagator = TraceContextTextMapPropagator()
        context = None
        tracer = trace.get_tracer(__name__)
        if tracer is None:
            wrapper = TracingWrapper()
            tracer = wrapper.tracer

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with current_app.app_context():
                traceparent = request.headers.get("traceparent")
                carier = {"traceparent": traceparent}
                context = propagator.extract(carier)
            log.info("Instrumenting function  %s", type(func))
            with tracer.start_as_current_span(
                span_name or func.__name__,
                kind=SpanKind.SERVER,
                context=context or kwargs.get("context", None),
            ) as span:
                if func.__name__:
                    span.set_attribute("function_name", func.__name__)
                try:
                    result = func(*args, **kwargs)
                except Exception as exc:
                    span.set_status(Status(StatusCode.ERROR))
                    span.record_exception(exc)
                    raise
                else:
                    if result:
                        log.info("Result is: ", result)
                        span.set_attribute("result_attributes", result)
                    if args:
                        span.set_attribute("arguments", args)
                    if kwargs:
                        # Need to handle all the types of kwargs
                        for keys, values in kwargs.items():
                            if keys == "context":
                                continue
                            if type(values) is dict:
                                for key, value in values.items():
                                    span.set_attribute(key, value)
                            elif type(values) is list:
                                for value in values:
                                    if type(value) is dict:
                                        for k, v in value.items():
                                            span.set_attribute(k, v)
                                    else:
                                        span.set_attribute(keys, value)
                            else:
                                span.set_attribute(keys, values)
                    if func.__doc__:
                        span.set_attribute("description", func.__doc__)
                    span.add_event(
                        f"{func.__name__} executed",
                        {"result": result or "success"}
                    )
                    span.set_status(Status(StatusCode.OK))
                finally:
                    # Add the span context from the current span to the link
                    span_id = span.get_span_context().span_id
                    trace_id = span.get_span_context().trace_id
                    traceparent = f"00-{trace_id}-{span_id}-01"
                    headers = {"traceparent": traceparent}
                    propagator.inject(span.get_span_context(), headers)
                    log.info("Headers are: %s", headers)

                return result

        wrapper = wrapper
        return wrapper

    if ignoreTracing:
        return func

    if is_class:
        # The decorator is being used to decorate a function
        return instrument_class
    else:
        # The decorator is being used to decorate a class
        return instrument_span
