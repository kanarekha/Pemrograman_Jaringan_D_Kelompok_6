import base64
import json
import logging
import os
import socket
import threading
import time
import tkinter

from tkinter import Tk, Scrollbar, Label, END, Entry, Text, Button, filedialog, messagebox, \
    Toplevel, DISABLED, NORMAL


from chat import Chat

TARGET_IP = "127.0.0.1"
TARGET_PORT = 8889

chat = Chat()
users = chat.getUsers()

class ChatClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = (TARGET_IP, TARGET_PORT)
        self.sock.connect(self.server_address)
        self.initlocation = os.getcwd()
        self.isfile = False
        self.isgroup = False
        self.receiverid = ""
        # self.chatopen = False
        self.rcv = threading.Thread(target=self.getmessage)
        self.tokenid = ""
        self.initialize_login()

    def initialize_login(self):  # GUI initializer
        ## chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()

        # login window
        self.loginpage = Toplevel()
        # set the title
        self.loginpage.title("Login")
        self.loginpage.resizable(width=False,
                                 height=False)
        self.loginpage.configure(width=400,
                                 height=300,
                                 bg = "#493323")
        # create a Label
        self.pls = Label(self.loginpage,
                         text="Silahkan login ",
                         font="Montserrat 14 bold",
                         bg ='#493323',
                         fg='#ffdf91')

        self.pls.place(relheight=0.15,
                       relx=0.29,
                       rely=0.07)
        # create a Label
        self.labelName = Label(self.loginpage,
                               text="Username: ",
                               font="Helvetica 12",
                               bg = '#493323',
                               fg='#ffdf91')

        self.labelName.place(relheight=0.2,
                             relx=0.1,
                             rely=0.27)

        # create a entry box for
        self.entryName = Entry(self.loginpage,
                               font="Helvetica 14",
                               bg ='#91684a',
                                fg='#ffdf91')

        self.entryName.place(relwidth=0.5,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.3)

        # create a Label pass
        self.labelPass = Label(self.loginpage,
                               text="Password: ",
                               font="Helvetica 12",
                                fg='#ffdf91',
                                bg = '#493323')

        self.labelPass.place(relheight=0.2,
                             relx=0.1,
                             rely=0.47)

        # create a entry box for pass
        self.entryPass = Entry(self.loginpage,
                               font="Helvetica 14",
                                bg ='#91684a',
                                fg='#ffdf91')

        self.entryPass.place(relwidth=0.5,
                             relheight=0.12,
                             relx=0.35,
                             rely=0.5)

        # set the focus of the curser
        self.entryName.focus()

        # create a Continue Button
        # along with action
        self.go = Button(self.loginpage,
                         text="Login",
                         font="Helvetica 14 bold",
                         bg="#eaac7f",
                         fg='#493323',
                         command=lambda: self.loginto(self.entryName.get(), self.entryPass.get()))

        self.go.place(relx=0.35,
                      rely=0.70)
        self.Window.mainloop()

    def loginto(self, username, password):
        self.loginpage.destroy()
        x = self.login(username, password).strip()
        # print(x)
        if (x == "Error, User Tidak Ada"):
            tkinter.messagebox.showinfo('Error', 'Nama tidak ada')
            self.loginpage.destroy()
            self.initialize_login()
        elif (x == "Error, Password Salah"):
            tkinter.messagebox.showinfo('Error', 'Password salah')
            self.loginpage.destroy()
            self.initialize_login()
        else:
            # start receiving msg
            # self.chatopen = True
            self.rcv.start()
            self.chatlist(username)
            # self.sendto(username);

    def login(self,username,password):
        string="auth {} {} \r\n" . format(username,password)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.tokenid=result['tokenid']
            return "username {} logged in, token {} " .format(username,self.tokenid)
        else:
            return "Error, {}" . format(result['message'])
    
    def chatlist(self, name):
        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("Menu Chat")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=470,
                              height=650,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="login sebagai " + self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=120.1)

        # label
        self.labellist = Label(self.line,
                               text="List Chat",
                               bg="#ABB2B9",
                               font="Helvetica 20")

        self.labellist.place(relheight=0.0005,
                             rely=0.0001,
                             relx=0.38)

        # loop name target list
        x = 0
        for k, v in users.items():
            # print(k, v)
            if (name == k):
                self.fullname = v["nama"]
                continue
            self.buttonperson = Button(self.line,
                                       text=v["nama"],
                                       font="Helvetica 10 bold",
                                       width=20,
                                       bg="#FFFFFF",
                                       command=lambda receiver=k, receivername=v["nama"]: self.sendto(name,
                                                                                                      receivername,
                                                                                                      receiver))

            self.buttonperson.place(relx=0.1,
                                    rely=0.0008 + x,
                                    relheight=0.0006,
                                    relwidth=0.8)
            x = x + 0.0008

        # Bikin Grup Baru
        self.buttongrups = Button(self.line,
                                  text="Buat Grup",
                                  font="Helvetica 10 bold",
                                  width=20,
                                  bg="#FFFFFF",
                                  command=lambda: self.createegroup())

        self.buttongrups.place(relx=0.1,
                               rely=0.0008 + x,
                               relheight=0.0006,
                               relwidth=0.8)

        # # create a scroll bar
        # scrollbar = Scrollbar(self.line)
        #
        # # place the scroll bar
        # # into the gui window
        # scrollbar.place(relheight=1,
        #                 relx=0.974)
        #
        # scrollbar.config(command=self.line.yview)

        # self.textCons.config(state=DISABLED)
    
    def sendto(self, username, receivername, receiver):
        self.isgroup = False
        self.receiverwho = receivername
        self.receiverid = receiver
        self.filename = ""
        # to show chat window
        self.Window.deiconify()
        self.Window.title("Ruangan Chat")
        self.Window.resizable(width=False,
                              height=False)
        self.Window.configure(width=470,
                              height=550,
                              bg="#17202A")
        self.labelHead = Label(self.Window,
                               bg="#17202A",
                               fg="#EAECEE",
                               text="Kirim pesan ke " + receivername,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)

        # tombol kembali
        self.buttonBack = Button(self.Window,
                                 text="Kembali",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=lambda: self.backtochatlist(username))

        self.buttonBack.place(relwidth=0.2, relx=0.8)

        # garis
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.textCons = Text(self.Window,
                             width=20,
                             height=2,
                             bg="#17202A",
                             fg="#EAECEE",
                             font="Helvetica 14",
                             padx=5,
                             pady=5)

        self.textCons.place(relheight=0.585,
                            relwidth=1,
                            rely=0.08)

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.66)

        # kolom pesan
        self.TextMsg = Text(self.labelBottom,
                            bg="#2C3E50",
                            fg="#EAECEE",
                            font="Helvetica 13")

        self.labelPassMsg = Label(self.labelBottom,
                                  text="Pesan: ",
                                  bg="#ABB2B9",
                                  font="Helvetica 10")

        self.labelPassMsg.place(relheight=0.02,
                                rely=0,
                                relx=0.011)

        self.TextMsg.place(relwidth=0.74,
                           relheight=0.088,
                           rely=0.02,
                           relx=0.011)

        # kolom receiver

        # self.entryRcv = Entry(self.labelBottom,
        #                       bg="#2C3E50",
        #                       fg="#EAECEE",
        #                       font="Helvetica 13",
        #                       text=receiver)
        # self.labelPassRcv = Label(self.labelBottom,
        #                        text="Penerima: ",
        #                        bg="#ABB2B9",
        #                        font="Helvetica 10")
        #
        # self.labelPassRcv.place(relheight=0.02,
        #                     rely=0,
        #                     relx=0.011)
        #
        # self.entryRcv.place(relwidth=0.74,
        #                     relheight=0.02,
        #                     rely=0.02,
        #                     relx=0.011)

        # nama file
        self.labelPassFile = Label(self.labelBottom,
                                   text="File: ",
                                   bg="#ABB2B9",
                                   font="Helvetica 10")

        self.labelPassFile.place(relheight=0.02,
                                 rely=0.107,
                                 relx=0.011)

        self.entryFile = Entry(self.labelBottom,
                               bg="#2C3E50",
                               fg="#EAECEE",
                               font="Helvetica 13")

        self.entryFile.place(relwidth=0.74,
                             relheight=0.02,
                             rely=0.1265,
                             relx=0.011)

        self.TextMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Kirim",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendhandler(receiver, self.TextMsg.get("1.0", 'end-1c')))

        self.buttonMsg.place(relx=0.77,
                             rely=0.004,
                             relheight=0.05,
                             relwidth=0.22)

        # create a MyFile Button
        self.buttonMF = Button(self.labelBottom,
                               text="File Anda",
                               font="Helvetica 10 bold",
                               width=20,
                               bg="#ABB2B9",
                               command=lambda: self.myfilepage(receiver))

        self.buttonMF.place(relx=0.77,
                            rely=0.06,
                            relheight=0.035,
                            relwidth=0.22)

        # create a Send File Button
        self.buttonMsg2 = Button(self.labelBottom,
                                 text="Unggah File",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=self.browse_file)

        self.buttonMsg2.place(relx=0.77,
                              rely=0.1,
                              relheight=0.021,
                              relwidth=0.22)

        # create a Send File Button
        self.buttonMsg3 = Button(self.labelBottom,
                                 text="Kirim File",
                                 font="Helvetica 10 bold",
                                 width=20,
                                 bg="#ABB2B9",
                                 command=lambda: self.filehandler(receiver, self.filename))

        self.buttonMsg3.place(relx=0.77,
                              rely=0.126,
                              relheight=0.021,
                              relwidth=0.22)

        self.textCons.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.textCons)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.textCons.yview)

        self.textCons.config(state=DISABLED)

    def sendhandler(self, receiver, text):
        if not (self.TextMsg.get("1.0", 'end-1c') and self.TextMsg.get("1.0", 'end-1c').strip()):
            return tkinter.messagebox.showinfo('Error', 'Pesan tidak boleh kosong')
        self.sendmessage(receiver, text)
    
    def sendmessage(self,usernameto="xxx",message="xxx"):
        if (self.tokenid==""):
            return "Error, not authorized"
        string="send {} {} {} \r\n" . format(self.tokenid,usernameto,message)
        print(string)
        result = self.sendstring(string)
        if result['status']=='OK':
            self.textCons.config(state=NORMAL)
            if self.isfile == True:
                self.textCons.insert(END,
                                     self.fullname + " : " + message + "\n")
            else:
                self.textCons.insert(END,
                                     self.fullname + " : " + self.TextMsg.get("1.0", 'end-1c') + "\n")
                self.isfile = False
            self.textCons.config(state=DISABLED)
            self.textCons.see(END)
            # clear msgtext
            self.TextMsg.delete('1.0', END)
            return "message sent to {}" . format(usernameto)
        else:
            return "Error, {}" . format(result['message'])
    
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
    
    def getmessage(self):
            while True:
                print(self.inbox().strip())
                time.sleep(1)
                # if self.chatopen == False :
                #     break
                # try:
                #
                #     print(self.inbox().strip())
                # except:
                #     # an error will be printed on the command line or console if there's an error
                #     break







if __name__ == "__main__":
    cc = ChatClient()
    while True:
        cmdline = input("Command {}:".format(cc.tokenid))
        print(cc.proses(cmdline))
