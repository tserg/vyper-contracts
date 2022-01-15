# Collection of Vyper contracts

This is a collection of smart contracts implemented in the Vyper smart contract language on Ethereum.

CAUTION: Not meant for production use.

# Dependencies

- [Vyper](https://github.com/vyperlang/vyper)
- [Brownie](https://github.com/eth-brownie/brownie)

# Directory

- `ERC721.vy`: ERC-721 implementation with ERC721Metadata, ERC721Enumerable and ERC721Receiver interfaces
- `PlainEIP712.vy`: Simple implementation of EIP712, with reference to [Yearn Vaults](https://github.com/yearn/yearn-vaults/blob/main/contracts/Vault.vy)
- `EIP4494.vy`: `ERC721.vy` with implementation of EIP-4494 (approval for transfer by signature).
- `VickreyAuction.vy`: A simple Vickrey auction (winning bidder pays second highest bid).
- `VickreyAuctionERC721.vy`: Extension of `VickreyAuction.vy` with ERC-721 non-fungible token held in escrow by auction contract.

# Testing

Run `brownie test` in your console.
