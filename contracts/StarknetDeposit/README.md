# Steps

- Ensure your Brownie's deployment account has been set and is funded with Goerli ETH.
- Export your `WEB3_INFURA_PROJECT_ID` in a console with Brownie activated in the environment.
- Run `brownie console --network goerli`.
- In your Brownie console, run `run('deploy_StarknetDepositBridge')`. This will deploy the `ERC20` contract minting 1000 tokens to your Brownie's deployment account, the `Bridge` contract with the `ERC20` contract as the underlying token, and an approval transaction for the `Bridge` contract to spend a certain number of `ERC20` tokens from your Brownie's deployment account.
- Update the `L1_CONTRACT_ADDRESS` constant in `l1l2.cairo` to the address of your deployed `Bridge` contract.
- In a console with Starknet activated in the environment, compile the contract and deploy it.
	```
	starknet-compile l1l2.cairo --output l1l2_compiled.json --abi l1l2_abi.json
	starknet deploy --contract l1l2_compiled.json
	```
- In your Brownie console, load your deployment account, initialise `bridge` to the latest `Bridge` contract that was deployed, and call the `deposit()` function of the `Bridge` contract.
	```
	a1 = accounts.load("deployment_account")
	bridge = Bridge[0]
	bridge.deploy(L2_CONTRACT_ADDRESS, L2_USER_ADDRESS, AMOUNT, {'from': accounts[0]})
	```
- In your Starknet console, check your account balance on the L2 contract. This may take a while after the confirmation of the deposit transaction on L1.
	```
	starknet call --address L2_CONTRACT_ADDRESS --abi l1l2_abi.json --function get_balance --inputs ADDRESS
	```
- To withdraw, call the `withdraw()` function of the L2 contract in your Starknet console.
	```
	starknet invoke --address L2_CONTRACT_ADDRESS --abi l1l2_abi.json --function withdraw --inputs L2_ADDRESS L1_ADDRESS AMOUNT
	```
- Wait for the transaction to be in `ACCEPTED_ON_L1` state. To check in your Starknet console, run:
	```
	starknet tx_status --hash TX_HASH
	```
- To execute the withdrawal on L1, call the `withdraw()` function of the `Bridge` contract in your Brownie console.
	```
	bridge.withdraw(L2_CONTRACT_ADDRESS, USER_L2_ADDRESS, AMOUNT, {'from': a1})
	```
