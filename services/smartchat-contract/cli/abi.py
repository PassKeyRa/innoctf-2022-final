import json

abi_s = ''
abi_r = ''
with open('abi_smartchat.json', 'r') as f:
    abi_s = f.read()
with open('abi_roomchat.json', 'r') as f:
    abi_r = f.read()
abi_smartchat = json.loads(abi_s)
abi_roomchat = json.loads(abi_r)
