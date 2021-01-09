# Bitcoin Microservice
REST API to interact with Bitcoin wallets.

## Configuration file
You have to set two things: RPC parameters for node comunication and Flask parameters for the main server. There are no default values.

```
[RPC]
user=
password=
host=
port=

[Server]
host=
port=
```

## Methods

### validate_address - GET
```
http://base_url/validate_address/<address>
```
Verify that the address passed as argument is a correct Bitcoin address.
Response:
```
{
	"isValid": true/false
}
```

### get_new_address - GET
```
http://base_url/get_new_address
```
Gives back a new fresh address of the wallet.
Response:
```
{
	"address": "<address>"
}
```

### get_balance - GET
```
http://base_url/get_balance/<address>/<OPTIONAL-min_conf>
```
Gives back the balance of the address given with 8 decimal digits of precision. Optionally you can pass the number of minimum confermation of the transaction you consider valid for the balance.
Response:
```
{
	"balance": <balance>
}
```

### transfer - POST
```
http://base_url/transfer

Data:
{
	"to": "<to_address>",
	"amount": <amount to transfer>,
	OPTIONAL
	"comment": "<comment>"
}
```
Transfer the amount specified to the address given. Optionally, a comment can be passed to remember locally the transaction informations. The amount passed is considered as the amount to pass plus the fee.
Response:
```
{
	"txid": "<txid>"
}
```

### errors
Whenever an error occurs the following response will be given:
```
{
	"error": "<error_description>"
}
```
