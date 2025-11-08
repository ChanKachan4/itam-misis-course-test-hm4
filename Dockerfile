FROM python:3.13-trixie

RUN apt-get update && apt-get install -y gcc python3-dev

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

COPY . /app

CMD ["python", "main.py"]