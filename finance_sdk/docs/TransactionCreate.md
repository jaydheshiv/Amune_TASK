# TransactionCreate

Schema for creating a new transaction.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**description** | **str** | Transaction description | 
**amount** | **float** | Transaction amount (must be positive) | 
**transaction_type** | **str** | Type of transaction: income or expense | 

## Example

```python
from finance_sdk.models.transaction_create import TransactionCreate

# TODO update the JSON string below
json = "{}"
# create an instance of TransactionCreate from a JSON string
transaction_create_instance = TransactionCreate.from_json(json)
# print the JSON string representation of the object
print(TransactionCreate.to_json())

# convert the object into a dict
transaction_create_dict = transaction_create_instance.to_dict()
# create an instance of TransactionCreate from a dict
transaction_create_from_dict = TransactionCreate.from_dict(transaction_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


