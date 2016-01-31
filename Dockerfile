FROM ubuntu:14.04

RUN apt-get update && apt-get install python3 python3-pip cron nginx git wget -y
RUN pip3 install gunicorn bottle

WORKDIR /var/www
RUN git clone https://github.com/FrontSide/txfmtrackservice-client.git

RUN wget https://raw.githubusercontent.com/Eonasdan/bootstrap-datetimepicker/master/build/css/bootstrap-datetimepicker.min.css -O /var/www/txfmtrackservice-client/bootstrap-datetimepicker.min.css
RUN wget https://raw.githubusercontent.com/Eonasdan/bootstrap-datetimepicker/master/build/js/bootstrap-datetimepicker.min.js -O /var/www/txfmtrackservice-client/bootstrap-datetimepicker.min.js

WORKDIR /opt
RUN git clone https://github.com/FrontSide/txfmtrackservice.git

WORKDIR /opt/txfmtrackservice
RUN pip3 install -r requirements.txt

RUN cp -f ./config/nginx/default.conf /etc/nginx/sites-enabled/default

RUN touch txfmtrack.log \
&& echo "* * * * * /opt/txfmtrackservice/txfmtracker.py && TXFM_MSG="OK $(date)" || TXFM_MSG="ERROR $(date)"; echo "$TXFM_MSG" >> /opt/txfmtrackservice/txfmtrack.log" > cron.tmp \
&& crontab cron.tmp \
&& rm cron.tmp

VOLUME /var/www/txfmtrackservice-client/_config

ENTRYPOINT cp /var/www/txfmtrackservice-client/config/host.js /var/www/txfmtrackservice-client/_config/host.js && chmod 777 /var/www/txfmtrackservice-client/_config/host.js \
;service nginx start; cron start; gunicorn -w 4 -b 127.0.0.1:8384 web:app
