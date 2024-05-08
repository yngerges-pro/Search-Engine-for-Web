import urllib.request
from bs4 import BeautifulSoup
import urllib.parse
from db_connection import DBConnection  # Import DBConnection from the separate file
from urllib.error import HTTPError, URLError
import time
# Define Frontier class
class Frontier:
    def __init__(self, initial_url):
        self.urls = [initial_url]
        self.visited = set()

    def done(self):
        return len(self.urls) == 0

    def nextURL(self):
        return self.urls.pop(0)

    def addURL(self, url):
        if url not in self.visited:
            self.urls.append(url)
            self.visited.add(url)

# Modify Crawler to use DBConnection
# pages.py (Crawler class)
class Crawler:
    def __init__(self, frontier=None, db_connection=None):
        self.frontier = frontier
        self.db_connection = db_connection
        self.retry_attempts = 3  # Maximum retry attempts
        self.retry_delay = 5  # Delay in seconds between retries

    def retrieveHTML(self, url):
        for attempt in range(self.retry_attempts):
            try:
                response = urllib.request.urlopen(url)
                return response.read()  # Retrieve HTML content
            except HTTPError as e:
                if e.code == 500:
                    print(f"HTTP 500 error on {url}: {e}. Attempt {attempt + 1} of {self.retry_attempts}")
                    time.sleep(self.retry_delay)  # Wait before retrying
                else:
                    print(f"Failed to retrieve {url}: {e}")
                    return None
            except URLError as e:
                print(f"URL Error on {url}: {e}")
                return None
        return None  # Return None if all attempts fail

    def storePage(self, url, html):
        if html:
            page_data = {
                "url": url,
                "html": html #decoded_html,  # Store decoded HTML
            }
            self.db_connection.insert_page(page_data)  # Store in MongoDB
        else:
            print(f"Cannot store {url}: Invalid HTML content")

    def target_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return bool(soup.find("h1", text="Faculty and Staff"))

    def run(self,url):
        while not self.frontier.done():
            url = self.frontier.nextURL()
            html = self.retrieveHTML(url)
            self.storePage(url, html)

            if self.target_page(html):
                self.frontier.urls = []
            else:
                soup = BeautifulSoup(html, "html.parser")
                for link in soup.find_all("a", href=True):
                    relative_url = link["href"]
                    if not relative_url.startswith("http"):
                        full_url = urllib.parse.urljoin(url, relative_url)
                    else:
                        full_url = relative_url
                    self.frontier.addURL(full_url)

# Instantiate DBConnection and create Crawler with Frontier
db_connection = DBConnection()  # Create DBConnection instance
initial_url = "https://www.cpp.edu/engineering/ce/index.shtml"
frontier = Frontier(initial_url)

crawler = Crawler(frontier, db_connection)  # Pass DBConnection to Crawler
crawler.run(initial_url)  # Start the crawler

print("Crawling Completed")