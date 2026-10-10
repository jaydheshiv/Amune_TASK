# finance_sdk.TransactionsApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_transaction**](TransactionsApi.md#create_transaction) | **POST** /transactions/ | Create a new transaction
[**delete_transaction**](TransactionsApi.md#delete_transaction) | **DELETE** /transactions/{transaction_id} | Delete a transaction
[**get_summary**](TransactionsApi.md#get_summary) | **GET** /transactions/summary | Get monthly summary
[**list_transactions**](TransactionsApi.md#list_transactions) | **GET** /transactions/ | List all transactions
[**reclassify_transaction**](TransactionsApi.md#reclassify_transaction) | **PATCH** /transactions/{transaction_id}/reclassify | Reclassify transaction category


# **create_transaction**
> TransactionOut create_transaction(transaction_create)

Create a new transaction

Create a new income or expense transaction.

### Example


```python
import finance_sdk
from finance_sdk.models.transaction_create import TransactionCreate
from finance_sdk.models.transaction_out import TransactionOut
from finance_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = finance_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with finance_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = finance_sdk.TransactionsApi(api_client)
    transaction_create = finance_sdk.TransactionCreate() # TransactionCreate | 

    try:
        # Create a new transaction
        api_response = api_instance.create_transaction(transaction_create)
        print("The response of TransactionsApi->create_transaction:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TransactionsApi->create_transaction: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **transaction_create** | [**TransactionCreate**](TransactionCreate.md)|  | 

### Return type

[**TransactionOut**](TransactionOut.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_transaction**
> delete_transaction(transaction_id)

Delete a transaction

Delete a transaction by its ID.

### Example


```python
import finance_sdk
from finance_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = finance_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with finance_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = finance_sdk.TransactionsApi(api_client)
    transaction_id = 56 # int | 

    try:
        # Delete a transaction
        api_instance.delete_transaction(transaction_id)
    except Exception as e:
        print("Exception when calling TransactionsApi->delete_transaction: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **transaction_id** | **int**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_summary**
> List[CategorySummary] get_summary(month=month)

Get monthly summary

Retrieve monthly category aggregates with income and expense totals.

### Example


```python
import finance_sdk
from finance_sdk.models.category_summary import CategorySummary
from finance_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = finance_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with finance_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = finance_sdk.TransactionsApi(api_client)
    month = 'month_example' # str | Filter by month (YYYY-MM) (optional)

    try:
        # Get monthly summary
        api_response = api_instance.get_summary(month=month)
        print("The response of TransactionsApi->get_summary:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TransactionsApi->get_summary: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **month** | **str**| Filter by month (YYYY-MM) | [optional] 

### Return type

[**List[CategorySummary]**](CategorySummary.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_transactions**
> List[TransactionOut] list_transactions(month=month, type=type, category=category)

List all transactions

Retrieve transactions with optional filtering.

### Example


```python
import finance_sdk
from finance_sdk.models.transaction_out import TransactionOut
from finance_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = finance_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with finance_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = finance_sdk.TransactionsApi(api_client)
    month = 'month_example' # str | Filter by month (YYYY-MM) (optional)
    type = 'type_example' # str | Filter by type (income or expense) (optional)
    category = 'category_example' # str | Filter by category (optional)

    try:
        # List all transactions
        api_response = api_instance.list_transactions(month=month, type=type, category=category)
        print("The response of TransactionsApi->list_transactions:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TransactionsApi->list_transactions: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **month** | **str**| Filter by month (YYYY-MM) | [optional] 
 **type** | **str**| Filter by type (income or expense) | [optional] 
 **category** | **str**| Filter by category | [optional] 

### Return type

[**List[TransactionOut]**](TransactionOut.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **reclassify_transaction**
> TransactionOut reclassify_transaction(transaction_id, reclassify_request)

Reclassify transaction category

Manually update the category of a transaction, overriding auto-tagging.

### Example


```python
import finance_sdk
from finance_sdk.models.reclassify_request import ReclassifyRequest
from finance_sdk.models.transaction_out import TransactionOut
from finance_sdk.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = finance_sdk.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with finance_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = finance_sdk.TransactionsApi(api_client)
    transaction_id = 56 # int | 
    reclassify_request = finance_sdk.ReclassifyRequest() # ReclassifyRequest | 

    try:
        # Reclassify transaction category
        api_response = api_instance.reclassify_transaction(transaction_id, reclassify_request)
        print("The response of TransactionsApi->reclassify_transaction:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling TransactionsApi->reclassify_transaction: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **transaction_id** | **int**|  | 
 **reclassify_request** | [**ReclassifyRequest**](ReclassifyRequest.md)|  | 

### Return type

[**TransactionOut**](TransactionOut.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

