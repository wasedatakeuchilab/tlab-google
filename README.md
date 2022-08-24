# Python Goolge API Wrapper for Takeuchi Lab <!-- omit in toc -->

<p align="center">
<a href="https://github.com/wasedatakeuchilab/tlab-google/actions?query=workflow%3ATest" target="_blank">
    <img src="https://github.com/wasedatakeuchilab/tlab-google/workflows/Test/badge.svg" alt="Test">
</a>
<a href="https://codecov.io/gh/wasedatakeuchilab/tlab-google" target="_blank">
    <img src="https://img.shields.io/codecov/c/github/wasedatakeuchilab/tlab-google?color=%2334D058" alt="Coverage">
</a>
</p>

**_tlab-google_** is a Python package that provides
an easier way to use Google API such as [Gmail API](https://developers.google.com/gmail/api).

_Google_ have already provided Python packages for Google API, such as [google-api-python-client](https://github.com/googleapis/google-api-python-client).
However, it is complicated a little for Python beginners.
That is why we created the package.

- [Requirements](#requirements)
- [Installation](#installation)
- [Getting Started](#getting-started)
  - [Gmail API](#gmail-api)
    - [Send a Message](#send-a-message)
    - [Search Messages](#search-messages)
    - [Get a Message](#get-a-message)
- [License](#license)

## Requirements

- Python 3.10 or above
- Waseda email address (that ends with `.waseda.jp`)

## Installation

You can install it with `pip` + `git`.

```sh
$ pip install git+https://github.com/wasedatakeuchilab/tlab-google
```

## Getting Started

### Gmail API

#### Send a Message

```python
import tlab_google
from email.mime import text

# Specify scopes to request
scopes = tlab_google.GmailAPI.get_default_scopes()

# Get a new credentials for Google API
creds = tlab_google.new_credentials(scopes)

# Create a GmailAPI instance
api = tlab_google.GmailAPI(creds)

# Create a message
to = "foobar@example.com"  # Replace it with your email address
subject = "API Test"
body = "This is a test mail of Gmail API."
message = text.MIMEText(body)
message["to"] = to
message["subject"] = subject

# Send a message
api.send_message(message)

# You can save the credentials and reuse it
creds_file = "credentials.json"
creds.save(creds_file)  # Save
creds = tlab_google.load_credentials(creds_file)  # Load again
```

#### Search Messages

```python
import tlab_google

creds_file = "credentials.json"
creds = tlab_google.load_credentials(creds_file)
api = tlab_google.GmailAPI(creds)

# The query format is the same as that of the search box of Gmail app
query = "subject:(Laboratory)"  # Replace it with your query string

# Search messages in Gmail box
results, next_page_token, size = api.list_message(query)
```

#### Get a Message

```python
import tlab_google
import base64

creds_file = "credentials.json"
creds = tlab_google.load_credentials(creds_file)
api = tlab_google.GmailAPI(creds)

# Get a message
msg_id = "foo"  # Replace it with your id
gmail = api.get_email(msg_id)

# Get its subject
headers = {header["name"]: header["value"] for header in gmail["payload"]["headers"]}
subject = headers["Subject"]

# Get its body
body = gmail["payload"]["body"]["data"]  # base64 encoded string

# Decode the body
decoded_body = base64.urlsafe_b64decode(body.encode()).decode()
```

## License

[MIT License](./LICENSE)

Copyright (c) 2022 Shuhei Nitta
