FROM python:3.11.5-slim


WORKDIR /Accounts/

COPY ./requirements.txt .
RUN python -m pip install -r requirements.txt

# COPY ./src/ .

EXPOSE 8003

CMD uvicorn main:app --host 0.0.0.0 --port 8003 --reload
