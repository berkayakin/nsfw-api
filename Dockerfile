FROM python:3.9

WORKDIR /app

ADD requirements.txt app/

RUN pip3 install --upgrade pip
RUN pip3 install -U -r app/requirements.txt
RUN pip3 install protobuf==3.20.*

RUN apt-get update -y
RUN apt install libgl1-mesa-glx -y

COPY . /app/

EXPOSE 8000

ENV PYTHONPATH "${PYTHONPATH}:/app/api"

CMD [ "python3", "api" ]