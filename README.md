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

+ Run main.py script. After that you can 