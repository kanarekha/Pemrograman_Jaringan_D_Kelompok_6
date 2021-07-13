import os.path
from datetime import datetime
from urllib.parse import unquote
import re

class ReverseProxy:
	def __init__(self):
		self.url_dict = {}
		self.url_dict['/images/']=("localhost", 8889)
		self.url_dict['/pdf/']=("localhost", 9000)
		self.default_server = ("localhost", 8888)

	def proses(self,data):

		forward_response = {}
		requests = data.split("\r\n")
		baris = requests[0]

		all_headers = [n for n in requests[1:] if n!='']
		j = baris.split(" ")
		method=j[0].upper().strip()
		url_address = j[1].strip()
		if(url_address[-1] != '/'):
			data = data.replace(url_address, url_address+'/')
			url_address += '/'

		for url, server in self.url_dict.items() :
			re_match = re.match(url, url_address)
			if re_match :
				forward_response['server'] = server
				forward_response['request'] = data.replace(url, '/')
		
		if "server" not in forward_response :
			forward_response['server'] = self.default_server
			forward_response['request'] = data
		
		return forward_response

if __name__=="__main__": 
	reverse_proxy = ReverseProxy()
	d = reverse_proxy.proses('GET /server1/aaa HTTP/1.0')
	print(d)
	d = reverse_proxy.proses('GET a/server1/ HTTP/1.0')
	print(d)















