# Oda Product Crawler

This tool crawls the product catalogue of the online grocery store [Oda](http://oda.com). The codebase defines abstractions that can be used to build custom adapters for different crawling use cases.

The project is my solution to a home assignment when applying for a position at the company in oct 2021. For a detailed presentation of my solution (choices/approach/tradeoffs/improvements) check out my [notes on the solution](NOTES.md).


## Prerequisites

- python >3.9
- pipenv

You can then install dependencies like:
```
pipenv install
```

This project has 2 dependencies:
- `requests` as http client
- `beautifulsoup4` as html parser


## How to Test
```
python -m unittest discover tests
```

## How to Run
```
python main.py
```

There is a hardcoded max number of page visits, but it's possible to stop the parsing at any moment with `CTRL+C`.

Before stopping, the program will save the current state in 3 files:
- `oda_frontier_<DATETIME>.json`, for debugging
- `oda_visited_<DATETIME>.json`, for debugging
- `oda_products_<DATETIME>.csv` <-- this is the main application output

## Results
This is the outcome of a full run. Check out the [/output](output) folder.

### Burndown chart
Here we get a glimpse of how the crawler discovered and visited all urls.

![frontier_burndown](https://user-images.githubusercontent.com/5155314/136757236-472f820d-71ba-4703-a7a2-f2f9aac56587.png)

This shows:
- an initial discovery phase
- a peak around 1500 visits (with the frontier topping at ~2800 urls)
- almost-linear smooth slope going through all the products in the frontier
- a final "bumpy" ride when reaching the bottom part of the frontier, discovering the remaining products

### Visualizations

All products grouped by categories (and subcategories):
![visualizations/mosaic_categories_with_legend_900x600.png]

All products grouped by category, sized by price:
![visualizations/price_categories_mosaic_legend_1000x600.png]

Guess which category is the red one where half the products are cheap while the other half expensive.