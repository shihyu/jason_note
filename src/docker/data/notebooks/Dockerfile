FROM jupyter/base-notebook:python-3.10

ENV APP_HOME /home/jovyan/work
WORKDIR $APP_HOME

COPY ./requirements.txt requirements.txt
RUN pip install -r requirements.txt
