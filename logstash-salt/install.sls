/tmp/logstash-2.0.0.tar.gz:
  file.managed:
    - source: salt://logstash/files/logstash-2.0.0.tar.gz
    - unless: /tmp/logstash-2.0.0.tar.gz

unpack_ball:
  cmd.run:
    - name: cd /tmp && tar -xzf logstash-2.0.0.tar.gz && mv logstash-2.0.0  /webdata/opt/local/logstash-2.0
    - required: 
      - file: /tmp/logstash-2.0.0.tar.gz
      - unless: test -d /webdata/opt/local/logstash-2.0       

/tmp/supervisor-3.3.1.tar.gz:
  file.managed:
    - source: salt://logstash/files/supervisor-3.3.1.tar.gz
    - unless: test -f /tmp/supervisor-3.3.1.tar.gz

install_supervisord:
  cmd.run:
    - name: cd /tmp && tar -xzf supervisor-3.3.1.tar.gz && cd supervisor-3.3.1 && /usr/bin/python setup.py install &>/dev/null
    - unless: test -f /usr/bin/supervisord
    - required:
      - file: /tmp/supervisor-3.3.1.tar.gz
 

/etc/init.d/supervisord:
  file.managed:
    - source: salt://logstash/files/supervisord
    - mode: 755
    - unless: test -f /etc/init.d/supervisord
  cmd.run: 
    - name: mkdir -p /etc/supervisord.d 

/etc/supervisord.d/logstash.ini:
  file.managed:
    - source: salt://logstash/files/logstash.ini
    - required:
      - file: /etc/init.d/supervisord
    - unless: test -f /etc/supervisord.d/logstash.ini
