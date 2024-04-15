import asyncio
import time
from urllib.parse import urlparse
from collections import deque
from urllib.parse import urljoin
import aiohttp

import requests
from bs4 import BeautifulSoup


class UrlToCrawl:
    def __init__(self, url, depth, parent):
        self._url = url
        self._depth = depth
        self._parent = parent

    @property
    def url(self):
        return self._url

    @property
    def parent(self):
        return self._parent

    @property
    def depth(self):
        return self._depth

    def __str__(self):
        return f"({self._url}, depth={self._depth}, parent={self._parent})"


class Crawler:
    def __init__(self, url):
        self._url_to_crawl = UrlToCrawl(url, 0, 0)
        self._queue = deque()
        self._visited = set()

    def visitSync(self, url_to_crawl):
        url = url_to_crawl.url
        if url not in self._visited:
            print(f"visiting {url}")
            self._visited.add(url)
            response = requests.get(url)
            return self._extractLinks(url_to_crawl, response.text)
        else:
            print(f"already visited {url}")
            return []

    async def _fetchAsync(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                return await resp.text()

    async def visitAsync(self, urls_to_visit):
        coros = [ self._fetchAsync(url.url) for url in urls_to_visit ]
        garbage = []
        bodies = await asyncio.gather(*coros) #wow thanks for the anonymous list
        i = 0 # ...
        for url in urls_to_visit:
            #if url not in garbage:
            print(f"visiting {url}")
            garbage.append(self._extractLinks(url, bodies[i]))

            i = i + 1

        return garbage

    async def crawlAsync(self, max_depth=2, batch_size=5):
        next_links = self.visitSync(self._url_to_crawl)
        self._queue.extend(next_links)

        while len(self._queue) > 0:
            links_to_visit = []
            if len(self._queue) >= batch_size:
                for x in range(batch_size):
                     links_to_visit.append(self._queue.popleft())
            else:
                for x in range(len(self._queue)):
                     links_to_visit.append(self._queue.popleft())

            next_links = await self.visitAsync(links_to_visit)
            #if depth <= max_depth:
            for link in next_links:
#                print(str(len(next_links)) + " " + str(len(self._queue)) + " " + str(len(link)))
                for l in link:
                    if l.depth < max_depth:
                        self._queue.append(l)

            if len(self._queue) > 0:
                print(f"next: {str(self._queue[0])}")

    def crawlSync(self, max_depth=2):
        next_links = self.visitSync(self._url_to_crawl)
        self._queue.extend(next_links)

        while len(self._queue) > 0 and self._queue[0].depth < max_depth:
            link_to_visit = self._queue.popleft()
            next_links = self.visitSync(link_to_visit)
            self._queue.extend(next_links)

            if len(self._queue) > 0:
                print(f"next: {str(self._queue[0])}")

    def _extractLinks(self, root_url_to_crawl, body):
        soup = BeautifulSoup(body, "html.parser")
        anchors = soup.find_all("a")
        links = []
        for anchor in anchors:
            href = anchor.get("href")
            if href and href.startswith("http:"):
                print(f"WARNING: found non-encrypted link {href}")
            if href and (href.startswith("https") or href.startswith("/")):
                absolute_url = urljoin(root_url_to_crawl.url, href)
                links.append(UrlToCrawl(absolute_url, root_url_to_crawl.depth + 1, root_url_to_crawl))
                #print(absolute_url)
        return links


async def main():
    #start_time = time.time()
    #Crawler("https://new.cs.unca.edu").crawlSync(max_depth=2)
    #elapsed_time = time.time() - start_time
    #print(f"crawlSync took {elapsed_time:.3f} seconds to complete.")
    start_time = time.time()
    await Crawler("https://new.cs.unca.edu").crawlAsync(max_depth=2, batch_size=20)
    elapsed_time = time.time() - start_time
    print(f"crawlAsync took {elapsed_time:.3f} seconds to complete.")

if __name__ == "__main__":
    asyncio.run(main())
