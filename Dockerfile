FROM python:3.7-alpine

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt

# COPY . /app
CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
# CMD ["sh","-c","python3.7 create_tables.py &&  flask run -h 0.0.0.0 -p 5000"]