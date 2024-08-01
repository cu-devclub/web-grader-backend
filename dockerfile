FROM python:3.10

WORKDIR /

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY src/. .

EXPOSE 5000

CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]