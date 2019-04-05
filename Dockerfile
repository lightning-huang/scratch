FROM frolvlad/alpine-python3

RUN set -x && pip install --upgrade pip && pip install tornado && mkdir /app &&mkdir /data
COPY dumpfolder.py /app
EXPOSE 8888
#we will mount the data into /data directory
ENTRYPOINT ["/bin/sh", "-c", "cd /app && python dumpfolder.py /data"]