FROM python:3.10-slim

ENV APP_HOME /spotman
WORKDIR $APP_HOME

RUN apt update && \
    apt upgrade -y && \
    apt-get -y install netcat curl dnsutils

# 複製當前目錄的所有檔案到容器內的，資料放在/usr/src/app
COPY . $APP_HOME
RUN pip install --no-cache-dir -r requirements.txt

ARG TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    addgroup --gid 1001 --system spotman && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --gid 1001 spotman && \
    chown -R spotman:spotman $APP_HOME

ENV PYTHONUNBUFFERED 1
USER spotman
# Define container entry point (could also work with CMD python main.py)
ENTRYPOINT ["python", "main.py"]
