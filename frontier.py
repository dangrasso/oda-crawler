from abc import ABC, abstractmethod
from collections import deque
from itertools import chain
from typing import Iterable


class Frontier(ABC):
    """
    This class abstracts away the idea of a frontier of urls for the crawler.
    It should be possible to add new urls to the frontier, either at low or high priority, as well as retrieve the next and know the frontier size.
    """

    @abstractmethod
    def pop(self) -> str:
        """Extract the next url from the frontier"""
        pass

    @abstractmethod
    def enqueue_next(self, urls: Iterable[str]):
        """Add all given urls to the frontier with the highest priority"""
        pass

    @abstractmethod
    def enqueue_last(self, urls: Iterable[str]):
        """Add all given urls to the frontier with the lowest priority"""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """Returns how many urls of the frontier"""
        pass

    @abstractmethod
    def __iter__(self):
        """Returns an iterator"""
        pass


# Round 1: a simple deque
class InMemoryDequeFrontier(Frontier):
    """
    This class provides a Frontier implementation that keeps urls in memory and works like a deque
    """

    def __init__(self):
        self._deque: deque[str] = deque()

    def enqueue_next(self, urls: Iterable[str]):
        self._deque.extend(urls)

    def enqueue_last(self, urls: Iterable[str]):
        self._deque.extendleft(urls)

    def pop(self):
        return self._deque.pop()

    def __len__(self) -> int:
        return len(self._deque)

    def __iter__(self):
        return iter(self._deque)


# Round 2: using both deque and set to avoid duplicates (at the expense of memory)
class InMemoryHybridFrontier(Frontier):
    """
    This class provides a Frontier implementation that keeps urls in memory and works like a deque but also filters out duplicates
    """

    def __init__(self):
        self._seen: set[str] = set()
        self._deque: deque[str] = deque()

    def enqueue_next(self, urls: Iterable[str]):
        new_urls = {u for u in urls if u not in self._seen}
        self._deque.extend(new_urls)
        self._seen.update(new_urls)

    def enqueue_last(self, urls: Iterable[str]):
        new_urls = {u for u in urls if u not in self._seen}
        self._deque.extendleft(new_urls)
        self._seen.update(new_urls)

    def pop(self):
        popped = self._deque.pop()
        self._seen.discard(popped)  # this allows re-visiting
        return popped

    def __len__(self) -> int:
        return len(self._deque)

    def __iter__(self):
        return iter(self._deque)


# Round 3: based on 2 sets to avoid duplicates (within same prio)
class InMemorySetFrontier(Frontier):
    """
    This class provides a Frontier implementation that keeps urls in memory and works like a set, avoiding duplicates.
    There could still be duplicates between low and high prio.
    """

    def __init__(self):
        self._set_high_prio: set[str] = set()
        self._set_low_prio: set[str] = set()

    def enqueue_next(self, urls: Iterable[str]):
        self._set_high_prio.update(urls)

    def enqueue_last(self, urls: Iterable[str]):
        self._set_low_prio.update(urls)

    def pop(self):
        return self._set_high_prio.pop() if len(self._set_high_prio) > 0 else self._set_low_prio.pop()

    def __len__(self) -> int:
        return len(self._set_high_prio) + len(self._set_low_prio)

    def __iter__(self):
        return chain(self._set_high_prio, self._set_low_prio)
