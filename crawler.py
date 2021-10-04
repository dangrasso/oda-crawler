import random
from abc import ABC, abstractmethod
from time import sleep
import requests
from bs4 import BeautifulSoup

from util import get_base_url, to_absolute_url


class Crawler(ABC):

    def __init__(self, url, max=10):
        self.visited = set()  # IDEA: abstract away the cache of visited pages and make it injectable, to support a shared cache middleware
        self.frontier = {url} # IDEA: abstract away the frontier and make it injectable, to support a message queue middleware
        self.max = max

    @abstractmethod
    def should_visit(self, url: str) -> bool:
        """
        Predicate: should the url be visited?
        """
        pass

    @abstractmethod
    def should_prioritize_visit(self, url: str) -> bool:
        """
        Predicate: should the url be visited before others?
        """
        pass

    @abstractmethod
    def should_collect(self, url: str, status_code: int) -> bool:
        """
        Predicate: should the url be collected?
        """
        pass

    @abstractmethod
    def collect(self, url: str, html: str, status_code: int) -> None:
        """
        Consumer: defines the logic for collecting the content of a page.
        It is only invoked on pages with urls satisfyiong the should_collect() predicate.
        """
        pass

    def fetch_content_status(self, url: str) -> tuple[str, int]:
        res = requests.get(url)
        if res.ok:
            return (res.content, res.status_code)
        print(f"Got {res.status_code} response for '{url}'")
        return (None, res.status_code)

    def parse_links(self, url: str, html: str) -> set[str]:
        soup = BeautifulSoup(html, "html.parser") # TODO: optimize by moving 'out' the html parsing
        anchors = soup.find_all("a")
        base_url = get_base_url(url)
        urls = {to_absolute_url(base_url, a.attrs['href']) for a in anchors if 'href' in a.attrs}
        return urls

    def visit(self, url: str) -> None:
        self.visited.add(url)
        print(f"[v:{len(self.visited)}|f:{len(self.frontier)}] Visiting: {url}")
        
        (content, status_code) = self.fetch_content_status(url)

        # delay after each fetch, to avoid flooding the server
        rnd_delay = round(random.uniform(1.0, 3.0), 2)
        sleep(rnd_delay) 
        
        if content is not None:
            new_urls = {u for u in self.parse_links(url, content) if self.should_visit(u) and u not in self.visited}
            new_urls_prioritized = {u for u in new_urls if self.should_prioritize_visit(u)}
            new_urls_other = new_urls.difference(new_urls_prioritized)

            # IDEA: convert from set to an ordered structure
            self.frontier.update(new_urls_prioritized)
            self.frontier.update(new_urls_other)

        if (self.should_collect(url, status_code)):
            self.collect(url, content, status_code)

    def crawl(self) -> None:
        while(len(self.frontier) > 0 and len(self.visited) < self.max):
            next_url = self.frontier.pop()
            if next_url not in self.visited:
                self.visit(next_url)
