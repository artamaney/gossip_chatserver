# Gossip chat-server

Decentralized course task. Web chat-server which uses websockets, realized gossip protocol
Like in IRC developed

Authorization form and token generator for users developed

## How to get token?
You should use generate_token method of class Authenticator.

###Steps
+ In gossip/authenticator.py an example of generating token
+ Create tokens.json file in gossip directory
+ Insert your values there. Key - username, value - generated token. It looks like `{"test": "$2b$10$BB6vXakBMrMAlDVoOvHkiu/bT0mfsnbYKcGtjBoAQ.8zvMeBTviti"}`

## How to run?

+ чтобы запустить сеть, нужно запустить файл main.py, в нем можно конфигурировать сервера сети, они задаются в виде списка узлов, для каждого узла указывается его хост и порт, а так же список смежности других серверов в сети. этот список смежности представлен в качестве словаря, где ключ это хост и порт узла сети, а значение -- список смежных узлов. Так сделано, чтобы распространение по госсип было как в IRC, где каждая узел сети это нода в дереве. 
