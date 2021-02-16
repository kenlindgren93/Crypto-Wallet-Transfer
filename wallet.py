import subprocess
import json
import bit
import web3
import os
import constants

from eth_account import Account
from web3 import Web3
from dotenv import load_dotenv
from web3.middleware import geth_poa_middleware
from bit.network import NetworkAPI

load_dotenv()

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

mnemonic = os.getenv("MNEMONIC", "axis cradle lesson panda jazz tenant swarm excess small toss client hobby")

def derive_wallets(mnemonic):
    output_json = dict()
    command = ["/Users/Ken/FinTech/Homework/Homework19/hd-wallet-derive/hd-wallet-derive.php", "-g", "--mnemonic='"+mnemonic+"'", "--cols=path,address,privkey,pubkey", "--format=json", "--coin=eth", "--numderive=3"]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    p_status = p.wait()
    command_out = json.loads(stdout)

    output_json['eth'] = command_out

    command = ["/Users/Ken/FinTech/Homework/Homework19/hd-wallet-derive/hd-wallet-derive.php", "-g", "--mnemonic='"+mnemonic+"'", "--cols=path,address,privkey,pubkey", "--format=json", "--coin=btc", "--numderive=3"]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    p_status = p.wait()
    command_out = json.loads(stdout)

    output_json['btc'] = command_out

    command = ["/Users/Ken/FinTech/Homework/Homework19/hd-wallet-derive/hd-wallet-derive.php", "-g", "--mnemonic='"+mnemonic+"'", "--cols=path,address,privkey,pubkey", "--format=json", "--coin=btc-test", "--numderive=3"]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    p_status = p.wait()
    command_out = json.loads(stdout)

    output_json['btc-test'] = command_out

    return output_json

def priv_key_to_account(coin, privkey):
    if coin == constants.BTCTEST:
        return bit.PrivateKeyTestnet(privkey)
    elif coin == constants.ETH:
        return Account.from_key(privkey)

def create_tx(coin, account, recipient, amount):
    if coin==constants.BTCTEST:
        return account.create_transaction([(str(recipient),amount,'btc')])

    gasEstimate = w3.eth.estimateGas(
        {"from": account.address, "to": recipient, "value": amount}
    )
    return {
        "from": account.address,
        "to": recipient,
        "value": amount,
        "gasPrice": w3.eth.gasPrice,
        "gas": gasEstimate,
        "nonce": w3.eth.getTransactionCount(account.address),
    }

def send_tx(coin, account, recipient, amount):
    if coin == constants.BTC:
        print("BTC token")
    elif coin == constants.ETH:
        tx = create_tx('eth', account, recipient, amount)
        signed_tx = account.sign_transaction(tx)
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
    elif coin == constants.BTCTEST:
        tx_hash=create_tx('btc-test',account,recipient,amount)
        result=NetworkAPI.broadcast_tx_testnet(tx_hash)
        return result
  

if __name__ == "__main__":
    coins = derive_wallets(mnemonic)
    print(coins)

account = priv_key_to_account('eth', 'cVZFy3PA9WRdvED5uev9GveaRqh6M7ZzVozaNU6jvDKMNMifgo8n')
create_tx('eth', account, coins['eth'][0]['address'], 0.00001)

output = send_tx('eth', account, coins['eth'][0]['address'], 0.00001)
print(output)



