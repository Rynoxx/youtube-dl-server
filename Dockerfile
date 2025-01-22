FROM python:3-alpine
ENV COOKIEFILE=
RUN adduser -D -h /usr/src/app python

RUN mkdir -p /usr/src/app/.venv && chown python:python -R /usr/src/app
WORKDIR /usr/src/app

COPY --chown=python:python Pipfile Pipfile.lock youtube_dl_server.py /usr/src/app/

USER python
RUN pip install --user pipenv && python3 -m pipenv install --deploy

EXPOSE 8080

CMD ["python3", "-m", "pipenv", "run", "execute"]
