# Shopify API

[![Build Status](https://github.com/Shopify/shopify_python_api/workflows/CI/badge.svg)](https://github.com/Shopify/shopify_python_api/actions)
[![PyPI version](https://badge.fury.io/py/ShopifyAPI.svg)](https://badge.fury.io/py/ShopifyAPI)
[![codecov](https://codecov.io/gh/Shopify/shopify_python_api/branch/master/graph/badge.svg?token=pNTx0TARUx)](https://codecov.io/gh/Shopify/shopify_python_api)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Shopify/shopify_python_api/blob/master/LICENSE)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

The [Shopify Admin API](https://shopify.dev/docs/admin-api) Python Library

## Usage

### Requirements
You should be signed up as a partner on the [Shopify Partners Dashboard](https://www.shopify.com/partners) so that you can create and manage shopify applications.

### Installation

To easily install or upgrade to the latest release, use [pip](http://www.pip-installer.org/).

```shell
pip install --upgrade ShopifyAPI
```

### Getting Started
#### Public and Custom Apps

1. First create a new application in the [Partners Dashboard](https://www.shopify.com/partners), and retrieve your API Key and API Secret Key.
1. We then need to supply these keys to the Shopify Session Class so that it knows how to authenticate.

   ```python
   shopify.Session.setup(api_key=API_KEY, secret=API_SECRET)
   ```
1.  In order to access a shop's data, apps need an access token from that specific shop. We need to authenticate with that shop using OAuth, which we can start in the following way:

    ```python
    shop_url = "SHOP_NAME.myshopify.com"
    api_version = '2020-10'
    state = binascii.b2a_hex(os.urandom(15)).decode("utf-8")
    redirect_uri = "http://myapp.com/auth/shopify/callback"
    scopes = ['read_products', 'read_orders']

    newSession = shopify.Session(shop_url, api_version)
    auth_url = newSession.create_permission_url(scopes, redirect_uri, state)
    # redirect to auth_url
    ```

1. Once the merchant accepts, the shop redirects the owner to the `redirect_uri` of your application with a parameter named 'code'. This is a temporary token that the app can exchange for a permanent access token. You should compare the state you provided above with the one you recieved back to ensure the request is correct. Now we can exchange the code for an access_token when you get the request from shopify in your callback handler:

    ```python
    session = shopify.Session(shop_url, api_version)
    access_token = session.request_token(request_params) # request_token will validate hmac and timing attacks
    # you should save the access token now for future use.
    ```

1.  Now you're ready to make authorized API requests to your shop!:

    ```python
    session = shopify.Session(shop_url, api_version, access_token)
    shopify.ShopifyResource.activate_session(session)

    shop = shopify.Shop.current() # Get the current shop
    product = shopify.Product.find(179761209) # Get a specific product

    # execute a graphQL call
    shopify.GraphQL().execute("{ shop { name id } }")
    ```

    Alternatively, you can use temp to initialize a Session and execute a command:

     ```python
     with shopify.Session.temp(shop_url, api_version, token):
        product = shopify.Product.find()
     ```

1.  It is best practice to clear your session when you're done. A temporary session does this automatically:

     ```python
     shopify.ShopifyResource.clear_session()
     ```

#### Private Apps
Private apps are a bit quicker to use because OAuth is not needed. You can create the private app in the Shopify Merchant Admin. You can use the Private App password as your `access_token`:

##### With full session
```python
session = shopify.Session(shop_url, api_version, private_app_password)
shopify.ShopifyResource.activate_session(session)
# ...
shopify.ShopifyResource.clear_session()
```

##### With temporary session

```python
with shopify.Session.temp(shop_url, api_version, private_app_password):
    shopify.GraphQL().execute("{ shop { name id } }")
```

### Billing
_Note: Your application must be public to test the billing process. To test on a development store use the `'test': True` flag_

1.  Create charge after session has been activated
    ```python
    application_charge = shopify.ApplicationCharge.create({
        'name': 'My public app',
        'price': 123,
        'test': True,
        'return_url': 'https://domain.com/approve'
    })
    # Redirect user to application_charge.confirmation_url so they can approve the charge
    ```
1.  After approving the charge, the user is redirected to `return_url` with `charge_id` parameter (_Note: This action is no longer necessary if the charge is created with [API version 2021-01 or later](https://shopify.dev/changelog/auto-activation-of-charges-and-subscriptions)_)
    ```python
    charge = shopify.ApplicationCharge.find(charge_id)
    shopify.ApplicationCharge.activate(charge)
    ```
1.  Check that `activated_charge` status is `active`
    ```python
    activated_charge = shopify.ApplicationCharge.find(charge_id)
    has_been_billed = activated_charge.status == 'active'
    ```

### Session tokens

The Shopify Python API library provides helper methods to decode [session tokens](https://shopify.dev/concepts/apps/building-embedded-apps-using-session-tokens). You can use the `decode_from_header` function to extract and decode a session token from an HTTP Authorization header.

#### Basic usage

```python
from shopify import session_token

decoded_payload = session_token.decode_from_header(
    authorization_header=your_auth_request_header,
    api_key=your_api_key,
    secret=your_api_secret,
)
```

#### Create a decorator using `session_token`

Here's a sample decorator that protects your app views/routes by requiring the presence of valid session tokens as part of a request's headers.

```python
from shopify import session_token


def session_token_required(func):
    def wrapper(*args, **kwargs):
        request = args[0]  # Or flask.request if you use Flask
        try:
            decoded_session_token = session_token.decode_from_header(
                authorization_header = request.headers.get('Authorization'),
                api_key = SHOPIFY_API_KEY,
                secret = SHOPIFY_API_SECRET
            )
            with shopify_session(decoded_session_token):
                return func(*args, **kwargs)
        except session_token.SessionTokenError as e:
            # Log the error here
            return unauthorized_401_response()

    return wrapper


def shopify_session(decoded_session_token):
    shopify_domain = decoded_session_token.get("dest")
    access_token = get_offline_access_token_by_shop_domain(shopify_domain)

    return shopify.Session.temp(shopify_domain, SHOPIFY_API_VERSION, access_token)


@session_token_required  # Requests to /products require session tokens
def products(request):
    products = shopify.Product.find()
    ...
```

### ApiAccess for handling access scope operations

There are common operations that are used for managing access scopes in apps. Such operations include serializing, deserializing and normalizing scopes. Other operations can include checking whether two sets of scopes grant the same API access or whether one set covers the access granted by another set.

To encapsulate the access granted by access scopes, you can use the `ApiAccess` value object.

#### Constructing an ApiAccess

```python
api_access = ApiAccess(["read_products", "write_orders"]) # List of access scopes
another_api_access = ApiAccess("read_products, write_products") # String of comma-delimited access scopes
```

#### Serializing ApiAccess

```python
api_access = ApiAccess(["read_products", "write_orders"])

access_scopes_list = list(api_access) # ["read_products", "write_orders"]
comma_delmited_access_scopes = str(api_access) # "read_products,write_orders"
```

#### Comparing ApiAccess objects

##### Checking for API access equality

```python
expected_api_access = ApiAccess(["read_products", "write_orders"])

actual_api_access = ApiAccess(["read_products", "read_orders", "write_orders"])
non_equal_api_access = ApiAccess(["read_products", "write_orders", "read_themes"])

actual_api_access == expected_api_access # True
non_equal_api_access == expected_api_access # False
```

##### Checking if ApiAccess covers the access of another

```python
superset_access = ApiAccess(["write_products", "write_orders", "read_themes"])
subset_access = ApiAccess(["read_products", "write_orders"])

superset_access.covers(subset_access) # True
```

### Advanced Usage
It is recommended to have at least a basic grasp on the principles of the [pyactiveresource](https://github.com/Shopify/pyactiveresource) library, which is a port of rails/ActiveResource to Python and upon which this package relies heavily.

Instances of `pyactiveresource` resources map to RESTful resources in the Shopify API.

`pyactiveresource` exposes life cycle methods for creating, finding, updating, and deleting resources which are equivalent to the `POST`, `GET`, `PUT`, and `DELETE` HTTP verbs.

```python
product = shopify.Product()
product.title = "Shopify Logo T-Shirt"
product.id                          # => 292082188312
product.save()                      # => True
shopify.Product.exists(product.id)  # => True
product = shopify.Product.find(292082188312)
# Resource holding our newly created Product object
# Inspect attributes with product.attributes
product.price = 19.99
product.save()                      # => True
product.destroy()
# Delete the resource from the remote server (i.e. Shopify)
```

### Prefix options

Some resources such as `Fulfillment` are prefixed by a parent resource in the Shopify API (e.g. `orders/450789469/fulfillments/255858046`). In order to interact with these resources, you must specify the identifier of the parent resource in your request.

```python
shopify.Fulfillment.find(255858046, order_id=450789469)
```

### Console
This package also includes the `shopify_api.py` script to make it easy to open an interactive console to use the API with a shop.
1.  Obtain a private API key and password to use with your shop (step 2 in "Getting Started")
1.  Save your default credentials: `shopify_api.py add yourshopname`
1.  Start the console for the connection: `shopify_api.py console`
1.  To see the full list of commands, type: `shopify_api.py help`

### GraphQL

This library also supports Shopify's new [GraphQL API](https://help.shopify.com/en/api/graphql-admin-api). The authentication process is identical. Once your session is activated, simply construct a new graphql client and use `execute` to execute the query.

```python
result = shopify.GraphQL().execute('{ shop { name id } }')
```


## Using Development Version

#### Building and installing dev version
```shell
python setup.py sdist
pip install --upgrade dist/ShopifyAPI-*.tar.gz
```

**Note** Use the `bin/shopify_api.py` script when running from the source tree. It will add the lib directory to start of sys.path, so the installed version won't be used.

#### Running Tests
```shell
pip install setuptools --upgrade
python setup.py test
```

## Relative Cursor Pagination
Cursor based pagination support has been added in 6.0.0.

```
import shopify

page1 = shopify.Product.find()
if page1.has_next_page():
  page2 = page1.next_page()

# to persist across requests you can use next_page_url and previous_page_url
next_url = page1.next_page_url
page2 = shopify.Product.find(from_=next_url)
```

## Set up pre-commit locally [OPTIONAL]
[Pre-commit](https://pre-commit.com/) is set up as a GitHub action that runs on pull requests and pushes to the `master` branch. If you want to run pre-commit locally, install it and set up the git hook scripts
```shell
pip install -r requirements.txt
pre-commit install
```

## Limitations

Currently there is no support for:

* asynchronous requests
* persistent connections

## Additional Resources
* [Partners Dashboard](https://partners.shopify.com)
* [developers.shopify.com](https://developers.shopify.com)
* [Shopify.dev](https://shopify.dev)
* [Ask questions on the Shopify forums](http://ecommerce.shopify.com/c/shopify-apis-and-technology)
