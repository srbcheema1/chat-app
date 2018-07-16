#!/usr/bin/env python3

import argparse
import grpc
import sys
import threading
import time

import validator_pb2 as message
import validator_pb2_grpc as rpc

from util.defaults import default_ip, default_port, connection_timeout
from util.vcfColor import Color
from util.code import EXIT, NORMAL, JOIN

class User:
    def __init__(self, ip=default_ip, port=default_port, username="noname"):
        self.input_iterator = self.create_iterator()
        self.username = username
        self.user_id = None
        self.metadata = None
        self.stub = None
        self.is_connected = False
        self.ip = ip
        self.port = port

    def create_connection(self):
        channel = grpc.insecure_channel(self.ip+':'+str(self.port))
        try:
            grpc.channel_ready_future(channel).result(timeout=connection_timeout)
        except grpc.FutureTimeoutError:
            sys.exit('Error connecting to server')
        else:
            self.stub = rpc.ValidatorStub(channel)

    def get_user_id(self):
        self.metadata = [('user_id', '0'), ('user_name',self.username)]
        user_id = self.stub.Get_user_id(message.Empty(),metadata=self.metadata)
        self.user_id = user_id.value
        self.metadata = [('user_id', str(self.user_id)), ('user_name',self.username)]

    def create_iterator(self):
        while(True):
            try:
                inp = input()
            except:
                yield message.String(value=EXIT)
                break
            inp = message.String(value=inp)
            yield inp

    def receive_output(self):
        for note in self.stub.Get_result(message.Empty(),metadata=self.metadata):
            if(note.value == EXIT):
                break
            self.display(note.value)

    def send_input(self):
        self.stub.Validate(self.input_iterator,metadata=self.metadata)

    def validate(self):
        if (self.stub == None):
            user.create_connection()
        if (self.user_id == None):
            self.get_user_id()

        threading.Thread(target=self.send_input, daemon=True).start()
        self.receive_output()

    def display(self, msg):
        user_id, code, user_name, msg = msg.split(':')
        if (code == EXIT):
            if(user_id == str(self.user_id)):
                print(Color.RED+'exiting ...'+Color.END)
                sys.exit(0)
            else:
                print(Color.BLUE + user_name + " : " + Color.CYAN + "left the chat" + Color.END)
        elif (code == JOIN):
            if(user_id != str(self.user_id)):
                print(Color.BLUE + user_name + " : " + Color.CYAN + "join the chat" + Color.END)
        elif(user_id != str(self.user_id)):
            print(Color.BLUE + user_name + " : " + Color.END + msg)

if (__name__ == "__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port",default=default_port, help="PORT number eg:- 12321")
    parser.add_argument("-u", "--user", help="USER username without space")
    parser.add_argument("-i", "--ip",default=default_ip, help="IP adress eg:- 127.0.0.1")
    args = parser.parse_args()

    ip = args.ip
    port = int(args.port)
    if(not args.user):
        user = input('enter username : ')
    else:
        user = args.user

    user = User(ip, port, user)
    user.validate()
