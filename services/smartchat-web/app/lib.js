const Web3 = require('web3');
const abi = require('./abi');
const Provider = require('@truffle/hdwallet-provider');
const { encrypt, decrypt } = require('./crypto');

let wallet = undefined;
let web3 = undefined;
let contract = undefined;
let account = undefined;


async function getRoomContract(room_addr) {
    var room_contract = new web3.eth.Contract(abi.abi_roomchat, room_addr);
    return room_contract;
}

const init = async (rpc_url, private_key, contract_address) => {
    wallet = new Provider(private_key, rpc_url);
    web3 = new Web3(wallet.engine);
    contract = new web3.eth.Contract(abi.abi_smartchat, contract_address);
    account = wallet.addresses[0];
}

const createRoom = async(room) => {
    await contract.methods.createRoom(room).send({from: account});
}

const getRoomByName = async(room) => {
    var room_addr = await contract.methods.getRoomByName(room).call({from: account});
    return room_addr;
}

const getMessages = async (room_address, key) => {
    var room_contract = await getRoomContract(room_address);
    var messages = await room_contract.methods.getMessages().call({from: account});

    // TODO DECRYPTION
    var dec_mes = []
    for (var i = 0; i < messages.length; i++) {
	dec_mes.push({'author':'anon', 'content':decrypt({'iv': Buffer.from(messages[i].text.toString().slice(2), 'hex').toString('utf8').split('|')[0], 
		'content': Buffer.from(messages[i].text.toString().slice(2), 'hex').toString('utf8').split('|')[1]}, key)})
    }
    return dec_mes;
}

const newMessage = async(room_address, text, key) => {
    // TODO ENCRYPTION
    var encrypted = encrypt(text, key)
    var data = new Buffer.from(encrypted.iv + '|' + encrypted.content)

    var room_contract = await getRoomContract(room_address);
    await room_contract.methods.newMessage(data).send({from: account});
}

module.exports = {
    init,
    createRoom,
    getMessages,
    getRoomByName,
     newMessage
}
