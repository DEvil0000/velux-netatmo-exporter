FROM python

RUN mkdir -p /var/lib/velux-netatmo-exporter/ \
 && chown nobody /var/lib/velux-netatmo-exporter/

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY velux-netatmo-exporter.py  /bin/velux-netatmo-exporter.py

RUN chmod +x /bin/velux-netatmo-exporter.py

USER nobody
EXPOSE 9211

VOLUME /var/lib/velux-netatmo-exporter/

ENTRYPOINT ["/bin/velux-netatmo-exporter.py"]