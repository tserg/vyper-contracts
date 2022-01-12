# vyper-contracts

Collection of Vyper contracts implementation.

- `ERC721.vy`: ERC-721 implementation with ERC721Metadata, ERC721Enumerable and ERC721Receiver interfaces
- `PlainEIP712.vy`: Simple implementation of EIP712, with reference to [Yearn Vaults](https://github.com/yearn/yearn-vaults/blob/main/contracts/Vault.vy)
- `EIP4494.vy`: `ERC721.vy` with implementation of EIP-4494 (approval for transfer by signature).
- `VickreyAuction.vy`: A simple Vickrey auction (winning bidder pays second highest bid).

CAUTION: Not meant for production use.
