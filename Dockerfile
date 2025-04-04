FROM     python:3.11
WORKDIR  /app
COPY    .	/app
RUN     pip install --upgrade pip --no-cache-dir
RUN		pip install -r /app/requirements.txt --no-cache-dir
CMD     gunicorn -b 0.0.0.0:8050 app:server