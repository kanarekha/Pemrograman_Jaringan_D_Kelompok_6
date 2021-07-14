from socket import AddressFamily
import sys
import threading
from chat_cli import ChatClient
import sys
import time
import logging
import json
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import os

cc = None
isRunning = False

class ChatMutex :
    def __init__(self):
        self.cc = ChatClient()
        self.isUsed = False
    def proses(self, message):
        while(self.isUsed and isRunning):
            time.sleep(0.1)
        self.isUsed = True
        response = self.cc.proses(message)
        self.isUsed = False
        return response
    def username(self):
        return self.cc.username

class LoginView(QWidget):

    def __init__(self, parent=None):
        super(LoginView, self).__init__(parent)
        self.view = parent
        self.initUI()
        
    def initUI(self):
        self.titleLabel = QLabel("Login", self)
        self.titleLabel.setFont(QFont("Arial", 28))
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.setStyleSheet("QLabel {background-color:red;}")
        self.titleLabel.move(300-int(self.titleLabel.width()/2), 100)

        userlabel = QLabel("Username", self)
        userlabel.setFont(QFont("Arial", 14))
        userlabel.move(300-int(userlabel.width()/2)-60, 200)

        passlabel = QLabel("Password", self)
        passlabel.setFont(QFont("Arial", 14))
        passlabel.move(300-int(passlabel.width()/2)-60, 250)

        # Create textbox
        self.userbox = QLineEdit(self)
        self.userbox.setFont(QFont("Arial", 14))
        self.userbox.resize(150,30)
        self.userbox.move(300-int(self.userbox.width()/2)+60, 200)

        # Create textbox
        self.passbox = QLineEdit(self)
        self.passbox.setFont(QFont("Arial", 14))
        self.passbox.resize(150,30)
        self.passbox.move(300-int(self.passbox.width()/2)+60, 250)

        # Create a button in the window
        self.button = QPushButton('Login', self)
        self.button.setFont(QFont("Arial", 20))
        self.button.resize(100,50)
        self.button.move(300-int(self.button.width()/2), 330)
        
        # # connect button to function on_click
        self.button.clicked.connect(self.login)

    def login(self):
        username = self.userbox.text()
        password = self.passbox.text()
        self.userbox.setText("")
        self.passbox.setText("")
        global cc
        response = cc.proses(f'auth {username} {password}')
        if(response['status'] == 'ERROR'):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Login failed")
            msg.setInformativeText(response['message'])
            msg.setWindowTitle("Login Failed")
            msg.exec_()
        else :
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Login Successful")
            msg.setWindowTitle("Login Successful")
            msg.exec_()
            self.view.showChatView()


class ChatView(QWidget):
    def __init__(self, parent=None):
        super(ChatView, self).__init__(parent)
        self.view = parent
        self.initUI()
        
    def initUI(self):
        self.tabs = QTabWidget(self)
        self.tabs.resize(600, 500)
        users = ["messi", "lineker", "henderson"]
        groups = ["group1"]
        self.inboxThread = InboxChatThread()
        self.fileThread = InboxFileThread()
        for user in users :
            if cc.username() != user :
                chatPanel = ChatPanel(user)
                self.tabs.addTab(chatPanel, user)
                self.inboxThread.addNewChat(user, chatPanel)
                self.fileThread.addNewChat(user, chatPanel)
        for group in groups :
            chatPanel = ChatPanel(group, True)
            self.tabs.addTab(chatPanel, group)
            self.inboxThread.addNewChat(group, chatPanel)
            self.fileThread.addNewChat(group, chatPanel)

        self.inboxThread.start()
        self.fileThread.start()


class InboxChatThread(threading.Thread):
    def __init__(self):
        self.userDict = {}
        threading.Thread.__init__(self)
    def addNewChat(self, username, chatpanel):
        self.userDict[username] = chatpanel
    def run(self):
        global isRunning
        while isRunning:
            newMessages = json.loads(cc.proses(f"inbox"))
            for user in newMessages :
                if(len(newMessages[user]) != 0):
                    for message in newMessages[user]:
                        self.userDict[user].addChat(message['msg_from'], message['msg'][2:-3])
            time.sleep(1)

class InboxFileThread(threading.Thread):
    def __init__(self):
        self.userDict = {}
        threading.Thread.__init__(self)
    def addNewChat(self, username, chatpanel):
        self.userDict[username] = chatpanel
    def run(self):
        global isRunning
        while isRunning:
            files = json.loads(cc.proses(f"my_file"))
            for user in files :
                for file in files[user]:
                    self.userDict[user].addFile(file)
            time.sleep(1)


class ChatPanel(QWidget):
    def __init__(self, username, isGroup=False, parent=None):
        super(ChatPanel, self).__init__(parent)
        self.view = parent
        self.username = username
        self.isAddingChat = False
        self.isAddingFile = False
        self.isGroup = isGroup
        self.files = []
        self.initUI()

    def initUI(self):
        self.ribbon = QTextEdit()
        self.ribbon.setReadOnly(True)
        self.chat = QTextEdit()
        self.fileBox = QListWidget()
        self.fileBox.itemDoubleClicked.connect(self.downloadFile)
        self.sendChatBtn = QPushButton('Send')
        self.sendChatBtn.clicked.connect(self.sendmessage)
        self.sendFileBtn = QPushButton('Send File')
        self.sendFileBtn.clicked.connect(self.sendFile)
        self.chat.setFixedHeight(
            (self.chat.fontMetrics().lineSpacing()*3) +
            (self.chat.document().documentMargin()*2) +
            (self.chat.frameWidth()*2) - 1
        )
        self.chat.setFixedWidth(400)
        policy = self.sendChatBtn.sizePolicy()
        policy.setVerticalPolicy(QSizePolicy.MinimumExpanding)
        self.sendChatBtn.setSizePolicy(policy)
        grid = QGridLayout()
        grid.setSpacing(3)
        grid.addWidget(self.ribbon, 0,0,2,1)
        grid.addWidget(self.fileBox, 0,2,1,1)
        grid.addWidget(self.chat, 2,0,1,1)
        grid.addWidget(self.sendChatBtn, 2,2,1,1)
        grid.addWidget(self.sendFileBtn, 1,2,1,1)
        grid.setRowStretch(0,1)
        grid.setColumnStretch(0,1)

        self.setLayout(grid)
    # pake isGroup untuk ngecek apakah ini group atau tidak
    # command send untuk group menggunakan command send_group
    # command send_file untuk group menggunakan command send_group_file
    
    def sendmessage(self):
        global cc
        self.newchat = self.chat.toPlainText()

        if(self.isGroup):
            cc.proses(f"send_group {self.username} {self.newchat}")
        else:
            cc.proses(f"send {self.username} {self.newchat}")

        # cc.proses(f"send {self.username} {self.newchat}")
        self.namechat = QTextEdit()
        self.namechat.setText("You: " + self.newchat)
        self.addchat = self.namechat.toPlainText()
        self.chat.setText("")
        # self.ribbon.setText(self.addchat) 
        self.ribbon.append(self.addchat)

    def sendFile(self):
        dialogFile = FileDialog(self.username, self.isGroup)
        dialogFile.exec_()

    def downloadFile(self, item):
        global cc
        cc.proses(f"download_file {self.username} {item.text()}")

    def addChat(self, name, message):
        global cc
        while self.isAddingChat:
            time.sleep(0.1)
        self.isAddingChat = True
        if name != cc.username:
            self.ribbon.append(f"{name}: {message}")
        self.isAddingChat = False

    def addFile(self, filename):
        while self.isAddingChat:
            time.sleep(0.1)
        self.isAddingFile = True
        if(filename not in self.files):
            self.files.append(filename)
            self.fileBox.addItem(filename)
        self.isAddingFile = False
        
class FileDialog(QDialog):
    def __init__(self, username, isGroup=False):
        super(FileDialog, self).__init__()
        self.username = username
        self.isGroup = isGroup
        self.initUI()
    def initUI(self):
        self.fileBox = QListWidget(self)
        self.fileBox.resize(400, 250)
        self.setFixedSize(400, 300)
        self.setWindowTitle("Send File")
        self.sendFileBtn = QPushButton('Send File')
        self.sendFileBtn.clicked.connect(self.send_file)
        grid = QGridLayout()
        grid.addWidget(self.fileBox, 0, 0, 3, 3)
        grid.addWidget(self.sendFileBtn, 4, 1, 1, 1)
        grid.setRowStretch(0,1)
        grid.setColumnStretch(0,1)
        self.setLayout(grid)
    def send_file(self):
        filename = self.fileBox.currentItem().text()
        global cc
        if(self.isGroup):
            cc.proses(f"send_group_file {self.username} {filename}")
        else:
            cc.proses(f"send_file {self.username} {filename}")
    def exec_(self):
        self.fileBox.clear()
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        for f in files:
            self.fileBox.addItem(f)
        self.fileBox.setCurrentRow(0)
        super(FileDialog, self).exec_()
        

    

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Chat Client")
        self.setGeometry(0, 0, 600, 500)
        self.setFixedSize(600, 500)
        self.setContentsMargins(-10,-10,-10,-10)
        
        self.LoginView = None
        self.ChatView = None
        
        self.showLoginView()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("No server found")
        msg.setInformativeText("Closing program")
        msg.setWindowTitle("Error")
        global cc
        try:
            cc = ChatMutex()
        except ConnectionError:
            msg.exec_()
            exit()

    def showLoginView(self):
        if(self.LoginView == None):
            self.LoginView = LoginView(self)

        self.setCentralWidget(self.LoginView)
        self.show()

    def showChatView(self):
        if(self.ChatView == None):
            self.ChatView = ChatView(self)
        self.setCentralWidget(self.ChatView)
        self.show()
    
    def closeEvent(self, a0: QCloseEvent) -> None:
        global isRunning
        isRunning = False
        return super().closeEvent(a0)

if __name__=="__main__":
    app = QApplication(sys.argv)
    isRunning = True
    ex = MainWindow()
    sys.exit(app.exec_())
    

