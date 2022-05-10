// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

import "./Helper.sol";

interface BaseContract {
  function isBossAddress(address addr) external pure returns (bool);
}

contract RoomChat {
  struct Message {
    address sender;
    bytes text;
  }

  BaseContract base;
  string public algorithm;
  address owner;
  address[] public members;
  Message[] messages;

  event MessageSent();
  event MessageDeleted();

  constructor(string memory algorithm_, address base_addr) {
    base = BaseContract(base_addr);
    algorithm = algorithm_;
    owner = tx.origin;
    members.push(owner);
  }
  
  function addMember(address member) external {
    require(msg.sender == owner, "Only admin can add users");
    require(!Helper.contains(members, member), "The user is already in the chat");
    members.push(member);
  }

  function listMembers() external view returns(address[] memory) {
    return members;
  }

  function newMessage(bytes calldata text) external returns (uint id){
    require(Helper.contains(members, msg.sender), "The sender is not in the chat");
    messages.push(Message(msg.sender, text));
    emit MessageSent();
    return messages.length - 1;
  }

  function countMessages() external view returns(uint count) {
    require(Helper.contains(members, msg.sender), "The sender is not in the chat");
    return messages.length;
  }

  function getMessages() external view returns(Message[] memory) {
    require(Helper.contains(members, msg.sender), "The sender is not in the chat");
    return messages;
  }

  function encrypt(bytes calldata input, bytes calldata key) external pure returns(bytes memory) {
    bytes memory encrypted = new bytes(input.length);
    uint k_len = key.length;
    for (uint i = 0; i < input.length; i++) {
      encrypted[i] = input[i] ^ key[i % k_len];
    }
    return encrypted;
  }

  function decrypt(bytes calldata input, bytes calldata key) external pure returns(bytes memory) {
    bytes memory decrypted = new bytes(input.length);
    uint k_len = key.length;
    for (uint i = 0; i < input.length; i++) {
      decrypted[i] = input[i] ^ key[i % k_len];
    }
    return decrypted;
  }

  function deleteMessage(uint id) external {
    require(base.isBossAddress(msg.sender), "Only boss can delete messages");
    delete messages[id];
  }

  function changeAlgorithm(string memory algo) external {
    require(msg.sender == address(base) || msg.sender == owner, "Only the base contract or chat admin can send such requests");
    algorithm = algo;
  }
}
