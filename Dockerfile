
FROM python:3.8

WORKDIR /usr/src/app
RUN mkdir results
RUN mkdir results/won
RUN mkdir results/draw
RUN mkdir results/lost

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY main/ ./

CMD [ "python3", "__init__.py" ]
