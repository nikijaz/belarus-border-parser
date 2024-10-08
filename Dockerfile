FROM python:3.12.3

WORKDIR /belarus-border-parser

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]