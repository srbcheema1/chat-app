# chat-app

Chat app that works on gRPC, and python3.

fist of all make an virtual environment using:
```
    python3 -m venv env
    source ./env/bin/activate
```
install the dependencies:
```
    pip install -r requirements.txt
```


You will require to compile protofiles in order to run the client and server
in order to do so run:
```
    make compile
```

for help:
```
    ./client.py --help
```



to start chatting:

    1. start the server
    2. run client from other terminal or other system by providing proper flags

