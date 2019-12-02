FROM python:3

ADD . .

RUN pip3 install -r requirements.txt

RUN adduser --disabled-password myuser
USER myuser 

CMD ["python3","-u","app.py"]