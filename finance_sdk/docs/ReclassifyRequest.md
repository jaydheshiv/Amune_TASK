# ReclassifyRequest

Schema for reclassifying a transaction category.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**category** | **str** | New category name | 

## Example

```python
from finance_sdk.models.reclassify_request import ReclassifyRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ReclassifyRequest from a JSON string
reclassify_request_instance = ReclassifyRequest.from_json(json)
# print the JSON string representation of the object
print(ReclassifyRequest.to_json())

# convert the object into a dict
reclassify_request_dict = reclassify_request_instance.to_dict()
# create an instance of ReclassifyRequest from a dict
reclassify_request_from_dict = ReclassifyRequest.from_dict(reclassify_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


