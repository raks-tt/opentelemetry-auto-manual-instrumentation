# opentelemetry-auto-manual-instrumentation
This repo is a POC to achieve Auto and Manual Instrumentation of a flask application

# To run the application
flask run --port=3000 --host=0.0.0.0

## Port assignment
Check if the port is used before running the application.

## Environment setup for testing

Create a virtualenv and install the required packages.
```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```


# Request

## Send a simple curl request with traceparent
curl -H "traceparent: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"  http://localhost:3000/api/v1/hello
Hello, World!%

# Send a simple curl request without a traceparent
curl http://localhost:3000/api/v1/hello
Hello, World!%