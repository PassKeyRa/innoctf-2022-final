// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

import "./Helper.sol";
import "./RoomChat.sol";

contract SmartChat {
  address private owner;
  string public algorithm;

  mapping (string => address[2]) rooms;
  
  constructor(string memory algorithm_) {
    owner = msg.sender;
    algorithm = algorithm_;
  }

  function getRoomByName(string memory name) public view returns (address) {
    return rooms[name][0];
  }

  function createRoom(string memory roomName) external returns (address) {
    RoomChat room = new RoomChat(algorithm, address(this));
    rooms[roomName][0] = address(room);
    rooms[roomName][1] = msg.sender;
    return address(room);
  }

  function changeAlgorithmForRoom(string memory algo, string memory roomName) external {
    require(this.isBossAddress(msg.sender) || rooms[roomName][1] == msg.sender, "Only boss or room admin can do that");
    if (rooms[roomName][0] != address(0)) {
      RoomChat room = RoomChat(rooms[roomName][0]);
      room.changeAlgorithm(algo);
      return;
    }
    algorithm = algo;
  }

  function isBossAddress(address addr) external pure returns (bool) {
    uint160 mask = 0x003133700000000000000000000000000000000000;
    if (uint160(addr) & mask == mask) {
      return true;
    }
    return false;
  }

  function gen_key() public view returns (bytes32 key) {
        uint64[4] memory rs;
        uint64 s = 0;
        for (uint i = 0; i < 4; i++) {
            rs[i] = Helper.random_number(s);
        }

        assembly {
            let i := 0
            for 
                { let end := 4 }
                lt(i, end)
                { i := add(i, 1) }
            {
                let r := mload(add(rs, mul(32, i)))
                let k := key
                let p := shl(64, k)
                key := or(p, r)
            }
        }
    }
}
