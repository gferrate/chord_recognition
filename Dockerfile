FROM debian:10
MAINTAINER gabrielferrate1996@gmail.com

RUN mkdir /app
WORKDIR /app

# Install required software
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cron \
    git \
    libffi-dev \
    libssl-dev \
    python3 \
    python3-dev \
    python3-pip \
    ssh \
    libsndfile1

# Install python packages needed for the custom package
RUN pip3 install setuptools
RUN pip3 install wheel
RUN pip3 install uwsgi

# Install requirements
COPY requirements.txt /root/tmp/requirements.txt
RUN pip3 install -r /root/tmp/requirements.txt

# Prepare enviroment
#RUN mkdir /src
COPY ./src/ .
#COPY cronfiles/$source.cron /etc/cron.d/$source.cron
#RUN chmod 0644 /etc/cron.d/$source.cron

RUN mkdir /var/log/chord-recognition/
RUN touch /var/log/chord-recognition/uwsgi.log

#RUN python3 manage.py collectstatic --noinput

RUN mkdir /conf
COPY ./conf/uwsgi.ini /conf/uwsgi.ini
COPY ./docker-entrypoint.sh /
RUN chmod 0755 /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uwsgi"]
