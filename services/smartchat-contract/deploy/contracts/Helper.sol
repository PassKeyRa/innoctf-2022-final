// SPDX-License-Identifier: MIT
pragma solidity >=0.4.22 <0.9.0;

library Helper {
  function toBytes(address a) external pure returns (bytes32 b){
    assembly {
      let m := mload(0x40)
      a := and(a, 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF)
      mstore(add(m, 20), xor(0x140000000000000000000000000000000000000000, a))
      mstore(0x40, add(m, 52))
      b := m
    }
  }
  function contains(address[] memory address_list, address addr) external pure returns (bool) {
    bool flag = false;
    for (uint i = 0; i < address_list.length; i++) {
      if (address_list[i] == addr) {
        flag = true;
        break;
      }
    }
    return flag;
  }
  function compare(string memory a, string memory b) external pure returns (bool) {
    return keccak256(abi.encodePacked(a)) == keccak256(abi.encodePacked(b));
  }

  function get_seed() internal view returns (uint256) {
      return uint256(keccak256(abi.encodePacked(blockhash(block.number - 1))));
  }

  function random_number(uint64 s_) external view returns (uint64) {
    uint64 seed = s_;
    if (seed == 0)
      seed = uint64(get_seed());
    unchecked {
        return uint64((6364136223846793005 * seed + 1442695040888963407) % (2 ** 64));
    }
  }

}