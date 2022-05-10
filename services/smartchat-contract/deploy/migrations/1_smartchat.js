const Helper = artifacts.require("Helper")
const SmartChat = artifacts.require("SmartChat");

module.exports = function (deployer) {
  deployer.deploy(Helper);
  deployer.link(Helper, SmartChat);
  deployer.deploy(SmartChat, "INTERNAL");
};
