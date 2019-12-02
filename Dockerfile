FROM python:3

ADD . .

RUN pip3 install -r requirements.txt

RUN adduser -D myuser
USER myuser 

CMD ["python3","-u","app.py"]