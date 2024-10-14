FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
COPY . .
# CMD ["flask", "run", "--host", "0.0.0.0"]
CMD [ "gunicorn", "-bind", "0.0.0.0:80", "app:create_app()" ]
#docker run -dp 5005:5000 -w /app -v "$(pwd):/app" flask-smorest-api

# docker build -t flask-smorest-api .