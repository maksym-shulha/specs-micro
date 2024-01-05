FROM python:latest

WORKDIR /specs_micro

COPY ./requirements.txt /specs_micro/requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY ./specs_micro/. /specs_micro

RUN mkdir log_files

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]