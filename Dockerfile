FROM python:3.10-alpine3.18

RUN pip install --upgrade pip

WORKDIR /youtubeFeed

COPY . /youtubeFeed

RUN pip install -r requirements.txt

EXPOSE 5000

CMD [ "python", "app.py" ]
