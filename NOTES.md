# Notes on the solution

This document describes the solution highlighting the main choices, how I approached the problem, the current limitations/tradeoffs and some ideas on potential improvements.

## Main Choices

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
I focused on the crawling part, prioritizing Extensibility, Maintainability and then Efficiency.
I didn't spend time on the configurability and visualization parts, mainly because I found the crawling part more interesting.

#### Step 0: learn
I started by implementing a simple casual crawler to figure out the main concepts, like the frontier, the list of visited nodes and the main loop.

#### Step 1: customize
I then looked at oda.com to make the crawling a bit smarter, limiting the search space to:
   - **Product pages**, the main target
   - **Category pages**, useful to discover all products

I tried to isolate all the Oda-specific logic into functions (e.g. should_visit, should_collect, collect), 
defining the Crawler's "natural" extension points.

I added the Product collection/scraping part, using local copies of product pages to speed up the process.
I also added a few 'Politeness' features, based on the robots.txt file.

#### Step 2: generalize
After it was working, I focused on improving Extensibility, by extracting the Crawler abstract class and chopping down functions into smaller cohesive ones.

When doing this I considered, for example, the use-case of finding broken links.
This helped me remove some assumptions regarding status codes that I initially baked into the Crawler.

#### Step 3: optimize
I let the crawler run for a while longer and noticed that:
   1. many visits were spent on category pages
   2. the frontier was growing with many duplicates

I addressed (1) by prioritizing product pages over category pages, using a `deque` for the frontier.

When attacking (2) I decided to abstract away the concept of Frontier.
This allowed me to test a few implementations (see [frontier.py](./crawler/frontier.py)), and choose one based on 2 sets.

#### Step 4: improve extensibility
Thinking about how to make the crawling distributed, I made the state (frontier,visited,products) **injectable**.
This means that multiple crawlers could cooperate on the same frontier, for example.
Generalizing the Frontier in the previous step was also partly due to this.

#### Final touches
I added a few features before wrapping up, like:
- ability to stop the program and get dumps of frontier/visited/products.
- retry, backoff on throttling errors
- breakdown of category path into levels and a few tests


## Limitations and Tradeoffs

### Memory / Scaling
Several parts of this codebase rely on the assumption that the crawl frontier, the set of visited urls and the collected products will fit in memory. While this could be a fair assumption given the current use case and time constraints, it may need improvements in a production system.

For example:
- the crawl frontier could be kept elsewhere. A messaging queue could fit this use case very well. 
  We could use a priority queue or simulate the dual priority by having 2 queues. 
  One caveat with the queue approach is that it can limit our ability to check for duplicates. 
  If this is the case and the queue size becomes a problem we could mitigate by adding a lookup in front of it.
- the visited urls require random access, because we constantly check them to avoid cycles and waste. 
  An in-memory cache would shine there, paired with some clever hashing of the keys. Redis for example.
  For a long-running crawler we could even add a ttl.
- the collected products could be stored in a db or flushed to disk at regular intervals.

### Performance
The bottleneck here is the added delay between http requests.
Regardless of how efficient each crawler is, or how many concurrent crawlers we throw at the problem, 
in order to avoid DDOS-ing the site we're going to stay within a *shared* budget of req/s. 

Not finding anything in https://oda.com/robots.txt I kept the req rate around 1 req/s.

If we set aside this bottleneck we could improve performance, fpr example by:
- spawning concurrent crawlers sharing the same frontier/visited-set/products-store
- replacing blocking code with async/await

### Error Handling
There is only basic error handling in place.
I added retries with a fixed backoff in case of throttling, but the product parsing part is still quite fragile.

Example/Fun-fact: https://oda.com/no/products/6250-toro-nellik-malt/ has no categories

On top of that the whole parsing results are gone in case of a crash, which is not great.

### Static Parsing
This tool performs static parsing (no js is executed). This trades flexibility for simplicity and performance. 
In order to parse online stores with client heavy front-ends, we may want to add a custom `fetch_content` implementation using something like Selenium or Puppeteer to reproduce a full browser environment.

### Testing
There are only a few unit tests, but the code should be easily testable. 
One example is the ability to inject the state in the Crawler class. Another is the isolation of the page fetching logic in a function that could be mocked.

### Politeness
The delay between requests is currently hardcoded, as well as an exclusion list on some paths. 
We could automate scanning Robots.txt and adhering to the policies it describes. 
On top of that we could tune the request rate based on the avg response latency, or decrease in case of throttling. 

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
 
### Save / Resume feature
The state (frontier/visited/collected trio) could be saved to disk and loaded. This would allow a user to pause and resume progress.
I implemented the saving part for debugging reasons, but skipped the loading.
