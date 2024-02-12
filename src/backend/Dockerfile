FROM python:3.11-slim as build

LABEL maintainer="Marty Berryman <mqarty@gmail.com>"

ARG ENV
ARG FUNCTION_DIR="/var/task/"

ENV FUNCTION_DIR=${FUNCTION_DIR}

WORKDIR ${FUNCTION_DIR}

# Install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY manage.py manage.py
COPY backend backend

FROM build as lambda

ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
CMD [ "backend.wsgi.handler" ]
