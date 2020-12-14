
FROM python:3.8

WORKDIR /usr/src/app
RUN mkdir results

COPY requirements.txt ./

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY main/ ./

CMD [ "python3", "__init__.py" ]
