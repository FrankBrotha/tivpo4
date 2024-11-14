FROM python:3.12-slim
WORKDIR /app
COPY init.sql /docker-entrypoint-initdb.d/
COPY . /app
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
