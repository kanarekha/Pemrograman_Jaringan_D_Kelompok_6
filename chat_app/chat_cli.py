import base64
import logging
import socket
import os
import json

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889


class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP,TARGET_PORT)
        self.sock.connect(self.server_address)
        self.username=""
        self.tokenid=""
    def proses(self,cmdline):
        j=cmdline.split(" ")
        try:
            command=j[0].strip()
            if (command=='auth'):
                username=j[1].strip()
                password=j[2].strip()
                response = self.login(username,password)
                return response
            elif (command=='send'):
                usernameto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendmessage(usernameto,message)
            elif (command=='send_group'):
                groupto = j[1].strip()
                message=""
                for w in j[2:]:
                   message="{} {}" . format(message,w)
                return self.sendgroupmessage(groupto,message)
            elif (command=='send_file'):
                usernameto = j[1].strip()
                filename = j[2].strip()
                return self.sendfile(usernameto,filename)
            elif (command=='send_group_file'):
                groupto = j[1].strip()
                filename = j[2].strip()
                return self.sendgroupfile(groupto,filename)
            elif (command=='my_file'):
                return self.myfile()
            elif (command=='download_file'):
                username = j[1].strip()
                filename = j[2].strip()
                return self.downloadfile(username, filename)
            elif (command=='inbox'):
                return self.inbox()
            else:
                return "*Maaf, command tidak benar"
        except IndexError:
                return "-Maaf, command tidak benar"
    def sendstring(self,string):
        try:
            self.sock.sendall(string.encode())
            receivemsg = ""
            while True:
                data = self.sock.recv(64)
                print("diterima dari server",data)
                if (data):
                    receivemsg = "{}{}" . format(receivemsg,data.decode())  #data harus didecode agar dapat di operasikan dalam bentuk string
                    if receivemsg[-4:]=='\r\n\r\n':
                        print("end of string")
                        return json.loads(receivemsg)
        except:
            self.sock.close()
            return { 'status' : 'ERROR', 'message' : 'Gagal'}
    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            self.username = username
            return { 'status' : 'OK', 'message' : 'Logged In', 'username':username, 'token':self.tokenid}
        else:
            return { 'status' : 'ERROR', 'message' : 'Wrong Password or Username'}
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return {'status' : 'OK', 'message':'message sent to {}' . format(usernameto)}
        else:
            return {'status':'ERROR', 'message':'Error, {}' . format(result['message'])}
    def sendgroupmessage(self,groupto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send_group {} {} {} \r\n" . format(self.tokenid,groupto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            return {'status' : 'OK', 'message':'message sent to {}' . format(groupto)}
        else:
            return {'status':'ERROR', 'message':'Error, {}' . format(result['message'])}
    def sendfile(self, usernameto, filename):
        if(self.tokenid==""):
            return "Error, not authorized"
        try :
            file = open(filename, "rb")
        except FileNotFoundError :
            return "Error, {} file not found".format(filename)
        buffer = file.read()
        buffer_string = base64.b64encode(buffer).decode('utf-8')
        message="send_file {} {} {} {} \r\n" .format(self.tokenid, usernameto, filename, buffer_string)
        result = self.sendstring(message)
        if result['status']=='OK':
            return {'status' : 'OK', 'message':'file sent to {}' . format(usernameto)}
        else:
            return {'status':'ERROR', 'message':'Error, {}' . format(result['message'])}
    def sendgroupfile(self, groupto, filename):
        if(self.tokenid==""):
            return "Error, not authorized"
        try :
            file = open(filename, "rb")
        except FileNotFoundError :
            return "Error, {} file not found".format(filename)
        buffer = file.read()
        buffer_string = base64.b64encode(buffer).decode('utf-8')
        message="send_group_file {} {} {} {} \r\n" .format(self.tokenid, groupto, filename, buffer_string)
        result = self.sendstring(message)
        if result['status']=='OK':
            return {'status' : 'OK', 'message':'file sent to group {}' . format(groupto)}
        else:
            return {'status':'ERROR', 'message':'Error, {}' . format(result['message'])}
    def myfile(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="my_file {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return {'status':'ERROR', 'message':'Error, {}' . format(result['message'])}
    def downloadfile(self, username, filename):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="download_file {} {} {} \r\n" . format(self.tokenid, username, filename)
        result = self.sendstring(string)
        if result['status']=='OK':
            output_file = open(result['filename'], 'wb')
            output_file.write(base64.b64decode(result['data']))
            output_file.close()
            return {'status' : 'OK', 'message':'file {} downloaded' . format(filename)}
        else:
            return {'status':'ERROR', 'message':'Error, {}' . format(result['message'])}
    def inbox(self):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="inbox {} \r\n" . format(self.tokenid)
        result = self.sendstring(string)
        if result['status']=='OK':
            return "{}" . format(json.dumps(result['messages']))
        else:
            return {'status':'ERROR', 'message':'Error, {}' . format(result['message'])}

if __name__=="__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:" . format(cc.tokenid))
        print(cc.proses(cmdline))

