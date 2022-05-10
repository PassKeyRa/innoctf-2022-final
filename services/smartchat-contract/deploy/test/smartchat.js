const SmartChat = artifacts.require("SmartChat")
const RoomChat = artifacts.require("RoomChat")

contract('SmartChat', async accounts => {
  it('gen_key works without exceptions', async () => {
    let smartchat = await SmartChat.deployed("INTERNAL");
    await smartchat.gen_key();
  });
  it('isBossAddress works correctly', async () => {
    let smartchat = await SmartChat.deployed("INTERNAL");
    assert(accounts[0].startsWith('0x31337'), "The call should be performed using boss account");
    let isboss = await smartchat.isBossAddress(accounts[0]);
    assert.equal(isboss, true, 'Something is wrong with boss checking');
    isboss = await smartchat.isBossAddress('0x78ceF33A0c4c0Ae01Ee45029Ee9f5A67Da3B7FC7');
    assert.equal(isboss, false, 'Something is wrong with boss checking');
  });
  it('Check the room is deployed and works correctly', async () => {
    let smartchat = await SmartChat.deployed("INTERNAL");
    await smartchat.createRoom("test");
    let roomaddr_ = await smartchat.getRoomByName("test");
    assert.notEqual(roomaddr_, '0x0000000000000000000000000000000000000000', "createRoom or getRoomByName returned wrong room address");
    let room = await RoomChat.at(roomaddr_);
    let roomalgo = await room.algorithm();
    assert.equal(roomalgo, "INTERNAL", "Initial room algorithm should be INTERNAL")
    let key = web3.utils.toHex('keykey');
    let data = web3.utils.toHex('testtest');
    let encrypted_ = '0x1f000a1f111c1811';
    let encrypted = await room.encrypt(data, key);
    assert.equal(encrypted, encrypted_, 'Wrong encryption');
    let decrypted = await room.decrypt(encrypted, key);
    assert.equal(decrypted, '0x7465737474657374', 'Wrong decryption');
    await room.newMessage(encrypted);
    let encrypted1 = await room.encrypt(web3.utils.toHex('newmessage'), key);
    await room.newMessage(encrypted1);
    let messages = await room.getMessages();

    assert(messages.length == 2, "puts messages incorrectly");
    assert(messages[0].sender == accounts[0], 'msg0 sender isn\'t right');
    assert(messages[1].sender == accounts[0], 'msg1 sender isn\'t right');
    assert(messages[0].text = encrypted, 'msg0 data is not correct');
    assert(messages[1].text = encrypted1, 'msg1 data is not correct');

    await room.deleteMessage(0);
    messages = await room.getMessages();

    assert(messages[0].sender == '0x0000000000000000000000000000000000000000', "boss deletes messages incorrectly");
    await room.changeAlgorithm('TEST');
    let algo = await room.algorithm();
    assert.equal(algo, 'INTERNAL', 'not a base contract changed room algorithm');

    await smartchat.changeAlgorithmForRoom('TEST', 'test');
    algo = await room.algorithm();
    assert.equal(algo, 'TEST', 'algorithm hasn\'t changed');

    await room.addMember('0x78ceF33A0c4c0Ae01Ee45029Ee9f5A67Da3B7FC7');
    let members = await room.listMembers();
    assert(members[1] = '0x78ceF33A0c4c0Ae01Ee45029Ee9f5A67Da3B7FC7', 'addMember works incorrectly');
  });
});
