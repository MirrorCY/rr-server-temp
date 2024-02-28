FROM python:3.11

WORKDIR /app

COPY ./server.py /app

RUN pip install --no-cache-dir flask gunicorn

EXPOSE 4244

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:4244", "server:app"]