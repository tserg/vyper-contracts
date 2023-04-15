# Collection of Vyper contracts

![tests](https://github.com/tserg/vyper-contracts/actions/workflows/test.yml/badge.svg)

This is a collection of smart contracts implemented in the Vyper smart contract language on Ethereum.

CAUTION: Not meant for production use.

# Dependencies

For Vyper contracts:
- [Vyper](https://github.com/vyperlang/vyper)
  - Some contracts may require the latest unreleased version of Vyper.
- [Ape](https://github.com/ApeWorX/ape)

For Cairo contracts:
- [Cairo](https://www.cairo-lang.org/docs/quickstart.html)
- [Starknet](https://www.cairo-lang.org/docs/hello_starknet/account_setup.html#installation)

# Directory

- ConditionalSoulbound
	- `TimeConditionalSoulbound`: A modified version of EIP-4671 Non-Tradable Tokens (a.k.a. Soulbound) where the right to claim is dependent on holding a specified ERC-721 token for a minimum period of time.
	- `TimedERC721`: A modified version of ERC-721 token with an additional mapping from address to the earliest timestamp of that address' ownership of a token.
- `ERC721.vy`: ERC-721 implementation with ERC721Metadata, ERC721Enumerable and ERC721Receiver interfaces
- `PlainEIP712.vy`: Simple implementation of EIP712, with reference to [Yearn Vaults](https://github.com/yearn/yearn-vaults/blob/main/contracts/Vault.vy)
- `EIP4494.vy`: `ERC721.vy` with implementation of EIP-4494 (approval for transfer by signature).
- `VickreyAuction.vy`: A simple Vickrey auction (winning bidder pays second highest bid).
- `VickreyAuctionERC721.vy`: Extension of `VickreyAuction.vy` with ERC-721 non-fungible token held in escrow by auction contract.
- EIP-4671 (a.k.a Soulbound) [outdated implementation]
	- `NTT.vy`: Implementation of EIP-4671 Non-Tradable Token Standard with Metadata and Enumerable extensions.
	- `NTTDelegate.vy`: Implementation of EIP-4671 Non-Tradable Token Standard with Metadata, Enumerable and Delegation extensions.
- StarknetDeposit: Vyper implementation of a modified Starknet's L1-L2 [bridge](https://www.cairo-lang.org/docs/hello_starknet/l1l2.html) for ERC-20. See `README.md` in folder for more details.
- Time-mining ERC721: Mine ERC20 tokens based on duration of possession of any NFT in wallet address.
	- `ERC20_mintable.vy`: Modified ERC20 that takes in a minter address in constructor.
	- `timer.vy`: Modified ERC721 that sets an ERC20 address it has mint permissions to, and allows holders to claim rewards based on duration of possession of any NFT.

# Testing

Run `ape test` in your console.
