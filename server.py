#!/usr/bin/env python3

import argparse
import grpc
import queue
import time
import subprocess as sp
import threading

from concurrent import futures
from select import select
from random import randint

import validator_pb2 as message
import validator_pb2_grpc as rpc

from util.enc_dec import enc, dec
from util.string_constants import vcf_path, end_of_report_neg, end_of_report
from util.defaults import default_port, default_ip
from util.files import get_files_in_dir, clean_folder, del_folder, verify_file, verify_folder
from util.code import EXIT, NORMAL, JOIN

class ValidatorServicer(rpc.ValidatorServicer):
    def __init__(self):
        self.user_list = {}
        self.output_dir = "./bin/out/"
        verify_folder(self.output_dir)
        self.output_file = self.output_dir + "log.txt"
        verify_file(self.output_file)
        self.fout = open(self.output_file,'w')

    def log(self, msg, msg_type, user_id, user_name):
        write_it = str(user_id) + ":" + msg_type +  ":" + user_name + ":" + msg
        self.fout.write(write_it+'\n')
        self.fout.flush()
        print(write_it)

    def Validate(self, request, context):
        metadata = dict(context.invocation_metadata())
        for req in request:
            if(req.value == EXIT):
                self.log(req.value, EXIT, metadata['user_id'],metadata['user_name'])
                break
            self.log(req.value, NORMAL, metadata['user_id'],metadata['user_name'])

        return message.Empty()

    def Get_result(self, request, context):
        output_vcf = sp.Popen(["tail -n0 -f "+self.output_file], shell=True, stdout=sp.PIPE)
        q = queue.Queue()
        t = threading.Thread(target=self.enqueue_output, args=(output_vcf.stdout, q))
        t.start()

        while (True): # validator alive or dead we will continue
            try:
                reply = q.get(timeout = 0.1)
            except queue.Empty: # no line yet
                pass
            else: # got line
                reply = self.make_reply(reply)
                response = message.String()
                response.value = reply
                self.get_msg_type(reply)
                yield response

        response = message.String()
        response.value = EXIT
        yield response

    def Get_user_id(self, request, context):
        metadata = dict(context.invocation_metadata())
        self.log('join', JOIN, 0, metadata['user_name'])

        user_id = randint(1,1000)
        while (user_id in self.user_list):
            user_id = randint(1,1000)
        self.user_list[user_id] = str(user_id)
        response = message.Number()
        response.value = user_id
        return response

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def get_msg_type(self, msg):
        arr = msg.split(':')
        return arr[1]

    def make_reply(self, reply):
        reply = dec(reply)
        if(len(reply) == 0):
            return reply

        if(reply[-1]=='\n'):
            return reply[:-1]


if (__name__=="__main__"):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port",default=default_port, help="PORT number eg:- 12321")
    parser.add_argument("-i", "--ip",default=default_ip, help="IP adress eg:- 127.0.0.1")
    args = parser.parse_args()

    ip = args.ip
    port = int(args.port)

    # Create Server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_ValidatorServicer_to_server(ValidatorServicer(), server)
    server.add_insecure_port(ip+':'+ str(port))
    print('Starting server on ' + ip + ' Listening on port ' + str(port) + '.')
    server.start()

    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)
