FROM nginx
RUN apt-get update && apt-get install git -y
WORKDIR /var/www
RUN git clone -b v1 https://github.com/FrontSide/txfmtrackservice-client.git
WORKDIR /opt
RUN git clone -b v1 https://github.com/FrontSide/txfmtrackservice.git
WORKDIR /opt/txfmtrackservice
RUN touch txfmtrack.log \
&& crontab -l > cron.tmp \
&& echo "* * * * * /opt/txfmtrackservice/txfmtracker.py && TXFM_MSG="OK $(date)" || TXFM_MSG="ERROR $(date)"; echo "$TXFM_MSG" >> /opt/txfmtrackservice/txfmtrack.log" >> cron.tmp \
&& crontab cron.tmp \
&& rm cron.tmp
ENTRYPOINT service nginx start; gunicorn -w 4 -b 127.0.0.1:8384 web:app
