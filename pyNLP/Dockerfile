FROM python:3.6

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt
RUN python -m spacy download en
COPY server /app/server
COPY textProcessing /app/textProcessing

ENTRYPOINT [ "python" ]

CMD [ "server/app.py" ]