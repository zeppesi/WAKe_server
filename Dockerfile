FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

EXPOSE 8000

RUN    apt-get -y update
RUN    apt-get -y install vim
RUN    apt-get -y install python3.11-dev python3.11-venv python3-pip
RUN    update-alternatives --install /usr/bin/python3 python /usr/bin/python3.11 1

RUN apt-get update \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*


RUN useradd -b /home -m -s /bin/bash django
RUN usermod -a -G www-data django
RUN mkdir -p /var/www/django
RUN mkdir -p /var/www/django/run
RUN mkdir -p /var/www/django/logs
RUN mkdir -p /var/www/django/ini

RUN python3 -m venv /var/www/django/venv
RUN chown -R django:www-data /var/www/django
RUN chmod -R g+w /var/www/django

RUN /var/www/django/venv/bin/pip3 install wheel
RUN /var/www/django/venv/bin/pip3 install -U uwsgi

ADD ./requirements.txt /var/www/django/requirements.txt
RUN /var/www/django/venv/bin/pip3 install -r /var/www/django/requirements.txt

ADD ./uwsgi/uwsgi.ini /var/www/django/ini/uwsgi.ini
ADD ./ /var/www/django/code

CMD ["/bin/bash", "-c", "source /var/www/django/venv/bin/activate && uwsgi --ini /var/www/django/ini/uwsgi.ini"]
