FROM python:3.9-buster

WORKDIR /opt/app

EXPOSE 8000

RUN pip3 install pipenv
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
