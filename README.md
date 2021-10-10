# Product Crawler

This tool crawls the product catalogue of the online grocery store oda.com. 
The codebase defines abstractions that can be used to build custom adapters for different crawling use cases.


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


## How to Run

```
python main.py
```

## Choices

### Language
I chose Python as an occasion to learn more / refresh what I know. I mostly used python for scripting or small projects. 
To make my life a bit easier and learn more I used "modern" Python features such as type hints and data classes, ignoring compatibility.

### Libraries
I tried to stay within the standard library, but decided to use 2 very popular libs (Requests, Beautifulsoup4) to solve less-interesting-but-tricky problems such as dealing with http and parsing html.
I decided to focus on the main problem and treat these 2 as commodities. 
In a real project I would also use a crawling/scraping framework, but that would have taken away all the fun :)

### Output
I chose CSV as a simple, versatile format that can be imported directly in several visualization tools, making it suitable for non-technical users as well.

## Approach

I focused on the crawling part, prioritizing Reusability/Maintainability and then Efficiency.

- I started by implementing a simple casual crawler to figure out the main concepts, like the frontier, the list of visited nodes and the main loop.
- I then looked at oda.com to make the crawling a bit smarter, limiting the search space to:
   1. Product pages, the main target
   2. Category pages, useful to discover all products
- I tried to isolate all the Oda-specific logic into functions (e.g. should_visit, should_collect, collect), defining the Crawler's natural extension points.
- I added the Product scraping part, using local copies of product pages to speed up the process.
- After it was working, I focused on improving Reusability, by extracting the Crawler abstract class and chopping down functions into smaller cohesive ones.
- I let the crawler run for a while longer, seeing the frontier growing exponentially and many visits being spent on non-product pages. I focused on improving efficiency by prioritizing product pages over category pages.
- While at it I extracted the Frontier into its own abstraction and made thw whole "state" injectable, in order to improve Extensibility and opening up for a more distributed crawling.
- I experimented with a couple of Frontier implementations to avoid duplicates in the frontier (see frontier.py)
- Added ability to stop the program and get dumps of frontier/visited/products.

I didn't spend time on the configurability and visualization parts, mainly because I found the crawling part more interesting.


## Limitations and Tradeoffs

### Memory / Scaling
Several parts of this codebase rely on the assumption that the crawl frontier, the set of visited urls and the collected products will fit in memory. While this could be a fair assumption given the current use case and time constraints, it may need improvements in a production system.

For example:
- the crawl frontier could be kept elsewhere. A messaging queue could fit this use case very well. We could use a priority queue or simulate the dual priority by having 2 queues. One caveat with the queue approach is that it can limit our ability to check if a new url is already in the frontier. If the queue size becomes a problem we could mitigate by adding a lookup in front of it.
- the visited urls require random access, because we constantly check them to avoid cycles and waste. An in-memory cache would shine there, paired with some clever hashing of the keys. Redis for example. For a long-running crawler we could even add a ttl.
- the collected products could be stored in a db or flushed to disk at regular intervals.

### Performance
The bottleneck here is the added delay between http requests. Regardless of how efficient each crawler is, or how many concurrent crawlers we throw at the problem, in order to avoid DDOS-ing the site we're going to stay within a *shared* budget of req/s. Not finding anything in https://oda.com/robots.txt I kept it around 1 req/s. 

If we set aside this bottleneck we could improve performance, for example by:
- spawning concurrent crawlers sharing the same frontier/visited-set/products-store, or partitioning the search space
- replacing blocking code with asynchronous calls (e.g. for http requests)

### Error Handling
There is only basic error handling in place.
I added retries with a fixed backoff in case of throttling, but the product parsing part still crashes too easily.

Example/Fun-fact: https://oda.com/no/products/6250-toro-nellik-malt/ has no categories

### Static Parsing
This tool performs static parsing (no js is executed). This trades flexibility for simplicity and performance. 
In order to parse online stores with client heavy front-ends, we may want to add a custom Parser implementation using something like Selenium or Puppeteer to reproduce a full browser environment.

### Testing
There are no automated tests, but the code should be easily testable. 
One example is the ability to inject the state in the Crawler class. Another is the isolation of the page fetching logic in a function that could be mocked.

### Politeness
The delay between requests is currently hardcoded, as well as an exclusion list on some paths. 
We could automate scanning Robots.txt and adhering to the policies it describes. 
On top of that we could tune the request rate based on the avg response latency, or increase in case of throttling. 


## Other Ideas

### Configurability
A configuration could be stored in a (e.g. json) file and loaded on startup. This could include:

 - max visits
 - initial url
 - delay between http requests
 - verbosity

 Oda-specific:
 - list of regex for should_visit, should_collect
 - output file name

We could also add some/all of these as args.
 
### Save / Resume feature
The state (frontier/visited/collected trio) could be saved to disk and loaded. This would allow different runs to build on each other's progress.
I started adding the saving part, but skipped the loading one.

