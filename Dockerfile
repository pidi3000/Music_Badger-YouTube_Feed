FROM python:3-alpine3.18

RUN pip install --upgrade pip

WORKDIR /youtubeFeed

COPY . /youtubeFeed

RUN pip install -r requirements.txt

CMD [ "python", "main.py" ]
