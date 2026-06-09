// Root hardhat config for the UNILIS extensions monorepo.
// Each workspace (pulseproof/, ghostgrade/, privacypool/) also has its own
// hardhat.config.js that sets paths relative to that subdirectory.
// This root config is used for top-level `npx hardhat` invocations if needed.

require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config({ path: ".env" });

module.exports = {
  // OZ v5 requires Solidity >=0.8.20 — 0.8.24 is the latest stable patch
  solidity: {
    version: "0.8.24",
    settings: { optimizer: { enabled: true, runs: 200 } },
  },
  networks: {
    localhost: { url: "http://127.0.0.1:8545" },
    amoy: {
      url:      process.env.POLYGON_AMOY_RPC || "https://rpc-amoy.polygon.technology",
      accounts: process.env.DEPLOYER_PRIVATE_KEY ? [process.env.DEPLOYER_PRIVATE_KEY] : [],
      chainId:  80002,
    },
  },
  etherscan: {
    apiKey: { polygonAmoy: process.env.POLYGONSCAN_API_KEY || "" },
    customChains: [{ network: "polygonAmoy", chainId: 80002,
      urls: { apiURL: "https://api-amoy.polygonscan.com/api", browserURL: "https://amoy.polygonscan.com" } }],
  },
  paths: { sources: "./contracts", tests: "./test", cache: "./cache", artifacts: "./artifacts" },
};
