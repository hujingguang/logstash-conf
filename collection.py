#!/usr/bin/python
# -*- coding: utf-8 -*-
import SocketServer
import os
import json
import socket
import MySQLdb
import logging
import time
import datetime


logging.basicConfig(level=logging.DEBUG,
	format='%(asctime)s %(levelname)s %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S',
	filename='/tmp/collection.log',
	filemode='a')


class MainHandler(SocketServer.BaseRequestHandler):
    db_name='your_db'
    db_user='your_user'
    db_password='your_password'
    db_host='your_ip'
    db_port=3306
    def get_connection(self):
	try:
	    self.conn=MySQLdb.connect(host=self.db_host,
		    user=self.db_user,
		    passwd=self.db_password,
		    db=self.db_name,
		    charset='utf8',
		    port=self.db_port)
	except Exception as e:
	     logging.error(e)
	     self.conn=None
	return self.conn
    def insert_to_mysql(self,data={}):
	if data:
	    message=data.get('message','').replace('"','')
	    host=data.get('host','')
	    logdate=datetime.datetime.strptime(data.get('logdate',''),'%d/%b/%Y:%H:%M:%S +0800').strftime('%Y-%m-%d %H:%M:%S')
	    method=data.get('method','')
	    uri=data.get('uri','')
	    protocol=data.get('protocol','')
	    status=data.get('status','0')
	    bytes=data.get('byte','0')
	    referer=data.get('referer','')
	    upstream_time=data.get('upstream_time','0.0')
	    response_time=data.get('response_time','0.0')
	    sql=''' insert into log_info(host,logdate,method,uri,protocol,status,bytes,referer,upstream_time,response_time,message) 
	    values("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}","{9}","{10}")'''.format(host,logdate,method,uri,protocol,status,bytes,referer,upstream_time,response_time,message)
	    conn=self.get_connection()
	    if conn:
		try:
		    cursor=conn.cursor()
		    cursor.execute(sql)
		    conn.commit()
		except Exception as e:
		    logging.error(e)
		    conn.rollback()
		finally:
		    conn.close()
		    self.conn=None
            else:
		logging.error('获取数据库连接异常')

	
	
    def handle(self):
	data=''
	while True:
	    recv_data=self.request.recv(1024)
	    if not recv_data:break
	    L=len(recv_data.split('}\n'))
	    if L==1:
		data=data+recv_data
	    elif L==2:
		slice_data=recv_data.split('}\n')
		data=data+slice_data[0]+'}'
		if len(data.split('}\n'))==2:
		    tmp_data=data.split('}\n')
		    try:
		        Dict=json.loads(tmp_data[0]+'}')
			self.insert_to_mysql(Dict)
		        Dict=json.loads(tmp_data[1])
			self.insert_to_mysql(Dict)
		    except Exception as e:
			logging.error(e)
		else:
		    try:
		        Dict=json.loads(data)
			self.insert_to_mysql(Dict)
		    except Exception as e:
			logging.error(e)
		data=slice_data[1]
	    else:
		slice_data=recv_data.split('}\n')
		data=data+slice_data[0]+'}'
		if len(data.split('}\n'))==2:
		    tmp_data=data.split('}\n')
		    try:
		        Dict=json.loads(tmp_data[0]+'}')
			self.insert_to_mysql(Dict)
		        Dict=json.loads(tmp_data[1])
			self.insert_to_mysql(Dict)
		    except Exception as e:
			logging.error(e)
		else:
		    try:
			Dict=json.loads(data)
			self.insert_to_mysql(Dict)
		    except Exception as e:
			logging.error(e)
		data=slice_data[-1:][0]
		for r in slice_data[1:-1]:
		    try:
			Dict=json.loads(r+'}')
			self.insert_to_mysql(Dict)
		    except Exception as e:
			logging.error(e)



def main():
    host,port='10.117.74.247',9999
    server=SocketServer.ForkingTCPServer((host,port),MainHandler)
    server.serve_forever()


if __name__=='__main__':
    main()
