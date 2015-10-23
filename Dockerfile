FROM nginx

RUN apt-get update && apt-get install git cron python-pip -y
RUN pip install gunicorn bottle pytz beautifulsoup4 redis pymongo

WORKDIR /var/www
RUN git clone -b v1 https://github.com/FrontSide/txfmtrackservice-client.git

WORKDIR /opt
RUN git clone -b v1 https://github.com/FrontSide/txfmtrackservice.git

WORKDIR /opt/txfmtrackservice

RUN cp -f ./config/nginx/default.conf /etc/nginx/conf.d/default.conf

RUN touch txfmtrack.log \
&& echo "* * * * * /opt/txfmtrackservice/txfmtracker.py && TXFM_MSG="OK $(date)" || TXFM_MSG="ERROR $(date)"; echo "$TXFM_MSG" >> /opt/txfmtrackservice/txfmtrack.log" > cron.tmp \
&& crontab cron.tmp \
&& rm cron.tmp

VOLUME /var/www/txfmtrackservice-client/_config

ENTRYPOINT cp /var/www/txfmtrackservice-client/config/host.js /var/www/txfmtrackservice-client/_config/host.js && chmod 777 /var/www/txfmtrackservice-client/_config/host.js \
;service nginx start; cron start; gunicorn -w 4 -b 127.0.0.1:8384 web:app
