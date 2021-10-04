# Product Crawler

This tool crawls the product catalogue of a web shop. It is targeted for the online grocery store oda.com, but the codebase defines abstractions that can be used to build custom adapters for any other store.


## Prerequisites

- python 3.9
- pipenv

You can then install dependencies like:
```
pipenv install
```

This project has 2 dependencies:
- `requests` as http client
- `beautifulsoup4` as html parser

## Run

```
python main.py
```

## Limitations

This tool performs static parsing (no js is executed). This trades simplicity and performance for flexibility. In order to parse online stores with client heavy front-ends, we may want to add a custom Parser implementation using something like Selenium to simulate a browser environment.