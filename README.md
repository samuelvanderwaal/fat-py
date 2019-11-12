# fat-py

Python library for the [Factom Asset Token](https://github.com/DBGrow/FAT) standard. Currently supports FAT-0 and FAT-1 token standards.

## Installation

The easiest way to install is with `pip` or `pipenv` from PyPi:

`pipenv install fat`


You can also clone the repo and build it from source. The recommended way to do this is with `pipenv`:

`git clone git@github.com:samuelvanderwaal/fat-py.git`

`cd fat-py`

Install requirements from the Pipfile:

`pipenv install`

Activate the virtual environment:

`pipenv shell`

See `pipenv`'s [documentation](https://pipenv-fork.readthedocs.io/en/latest/basics.html) for more usage details.

## Quick Start

Issue a new token:

```python
from fat.fat0 import Issuance
from factom import Factomd

factomd = Factomd()

issuance = Issuance(
    token_id="mytoken",
    issuer_id="8888...",
    supply=-1,
    symbol="tkn1",
    ec_address="EC3...",
    ec_priv_key="ES3...",
    server_priv_key="sk1..."
)

issuance.issue_token(factomd)
```



Build and submit a token transaction:

```python
from fat.fat0 import Transaction
from fat import FATd

fatd = FATd()

address1 = "FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW"
private_fct_key1 = "Fs..."
address2 = "FA3j68XNwKwvHXV2TKndxPpyCK3KrWTDyyfxzi8LwuM5XRuEmhy6"
chain_id = "a9d7791caffd852f8e3710e3c38f1ad1b056d4ecb2d4d54216581dfd0dac8edd"

tx1 = Transaction()
tx1.add_input(address1, 100)
tx1.add_output(address2, 100)
tx1.add_signer(private_fct_key1)
tx1.set_chain_id(chain_id)
tx1.sign()

fatd.submit_transaction(tx1)
```





## Usage

The two main ways to use this library are the Issuance and Transaction classes. In addition, the library exposes all the fatd RPC methods which can be accessed through the FATd class.

### Issuance

The Issuance class supports object initialization through multiple methods:

Individual property assignment:

```Python
issuance = Issuance()
issuance.token_id = "mytoken"
issuance.issuer_id = "888888a37cbf303c0bfc8d0cc7e77885c42000b757bd4d9e659de994477a0904"
issuance.supply = -1
issuance.symbol = "tkn1"
issuance.ec_address = "EC3cQ1QnsE5rKWR1B5mzVHdTkAReK5kJwaQn5meXzU9wANyk7Aej"
issuance.ec_priv_key = "ES..."
issuance.server_priv_key = "sk1..."
```

Passing all values as part of the constructor:

```python
issuance = Issuance(
	token_id="mytoken",
    issuer_id="8888...",
    supply=-1,
    symbol="tkn1",
    ec_address="EC3...",
    ec_priv_key="ES3...",
    server_priv_key="sk1..."
)
```

Once the issuance object has all the required values, the `issue_token()` method can be used to perform all the necessary `factomd` calls to issue and initialize a new token. 

```Python
from fat.fat0 import Issuance
from factom import Factomd

factomd = Factomd()

issuance = Issuance(
	token_id="mytoken",
    issuer_id="8888...",
    supply=-1,
    symbol="tkn1",
    ec_address="EC3...",
    ec_priv_key="ES3...",
    server_priv_key="sk1..."
)

issuance.issue_token(factomd)

```

Issuance supports both the Python native `str` type and key objects from the `factom_keys` library for EC and server ID keys. When strings are passed to it, internally it uses the `factom_keys` library to validate the key and address values. 

```python
...
from factom_keys.ec import ECAddress

ec_address1 = ECAddress(key_string="EC3cQ1QnsE5rKWR1B5mzVHdTkAReK5kJwaQn5meXzU9wANyk7Aej")
ec_address2 = "EC3cQ1QnsE5rKWR1B5mzVHdTkAReK5kJwaQn5meXzU9wANyk7Aej"
issuance = Issuance()
...
issuance.ec_address = ec_address1
# or
issuance.ec_address = ec_address2
```

FAT-0 and FAT-1 issuance has the same usage, just import the specific Issuance class needed. Use import aliases if both are required simultaneously:

```python
from fat.fat0 import Issuance as FAT0Issuance
from fat.fat1 import Issuance as FAT1Issuance
```



### Transaction

The Transaction class also supports multiple methods of initialization:

Passing all values through the constructor:

```python
tx1 = Transaction(
	inputs={"FA...": 100, "FA3...": 50},
    outputs={"FA3Z...": 150},
    chain_id="a9d7791caffd852f8e3710e3c38f1ad1b056d4ecb2d4d54216581dfd0dac8edd",
    signers=["FS...", "Fs..."]
)
tx1.sign()
```

Adding values individually:

```python
tx1 = Transaction()
tx1.add_input(coinbase_address, 100)
tx1.add_output(address1, 50)
tx1.add_output(address2, 50)
tx1.add_signer(issuer_signer)
tx1.set_chain_id(chain_id)
tx1.sign()
```

Builder method:

```python
tx1 = Transaction()
(
 tx1.add_input(coinbase_address, 100)
    .add_output(address1, 50)
    .add_output(address2, 50)
    .add_signer(issuer_signer)
    .set_chain_id(chain_id)
    .sign()
)
```

Transaction supports both the native Python `str` type and key objects from the `factom_keys` library for Factoid private keys, Factoid addresses and for server ID private keys.

```Python
...
from factom_keys.ec import FactoidAddress, FactoidPrivateKey
from factom_keys.serverid import ServerIDPrivateKey

address1 = FactoidAddress(address_string="FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW")
address2 = "FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW"
fct_priv_key1 = FactoidPrivateKey(key_string="Fs...")
fct_priv_key2 = "Fs..."

tx = Transaction()
tx.add_input(address1, 50)
tx.add_signer(fct_priv_key1)
# or
tx.add_input(address2, 50)
tx.add_signer(fct_priv_key2)
```



Once a transaction has been built and signed, it can be passed to the `submit_transaction()` method on FATd for submission to the blockchain. 

FAT-0:

```python
from fat.fat0 import Transaction
from fat import FATd

fatd = FATd()

address1 = "FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW"
private_fct_key1 = "Fs..."
address2 = "FA3j68XNwKwvHXV2TKndxPpyCK3KrWTDyyfxzi8LwuM5XRuEmhy6"
chain_id = "a9d7791caffd852f8e3710e3c38f1ad1b056d4ecb2d4d54216581dfd0dac8edd"

tx1 = Transaction()
tx1.add_input(address1, 100)
tx1.add_output(address2, 100)
tx1.add_signer(private_fct_key1)
tx1.set_chain_id(chain_id)
tx1.sign()

fatd.submit_transaction(tx1)
```

FAT-1:

```python
from fat.fat1 import Transaction
from fat import FATd

fatd = FATd()

address1 = "FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW"
private_fct_key1 = "Fs..."
address2 = "FA3j68XNwKwvHXV2TKndxPpyCK3KrWTDyyfxzi8LwuM5XRuEmhy6"
chain_id = "a9d7791caffd852f8e3710e3c38f1ad1b056d4ecb2d4d54216581dfd0dac8edd"

tx1 = Transaction()
tx1.add_input(address1, [1,3])
tx1.add_output(address2, [1,3])
tx1.add_signer(private_fct_key1)
tx1.set_chain_id(chain_id)
tx1.sign()

fatd.submit_transaction(tx1)
```



### FATd RPC Methods

All FATd RPC and Daemon methods are exposed via the FATd class:

```python
from fat import FATd

fatd= FATd()

chain_id = "a9d7791caffd852f8e3710e3c38f1ad1b056d4ecb2d4d54216581dfd0dac8edd"
address = "FA2gCmih3PaSYRVMt1jLkdG4Xpo2koebUpQ6FpRRnqw5FfTSN2vW"

fatd.get_issuance(chain_id=chain_id)
fad.get_balance(address, chain_id=chain_id)
fatd.get_daemon_properties()
```

