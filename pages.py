import urllib.request
from bs4 import BeautifulSoup
import urllib.parse
from db_connection import DBConnection  # Import DBConnection from the separate file

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
    def __init__(self, frontier, db_connection):
        self.frontier = frontier
        self.db_connection = db_connection

    def retrieveHTML(self, url):
        response = urllib.request.urlopen(url)
        return response.read()

    def storePage(self, url, html):
        page_data = {
            "url": url,
            "html": html.decode("utf-8"),  # Correct field name 'html'
        }
        self.db_connection.insert_page(page_data)  # Store in MongoDB

    def target_page(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return bool(soup.find("h1", text="Permanent Faculty"))

    def run(self):
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
                    base_url = "https://www.cpp.edu/sci/computer-science/"
                    if not relative_url.startswith("http"):
                        full_url = urllib.parse.urljoin(base_url, relative_url)
                    else:
                        full_url = relative_url
                    self.frontier.addURL(full_url)

# Instantiate DBConnection and create Crawler with Frontier
db_connection = DBConnection()  # Create DBConnection instance
initial_url = "https://www.cpp.edu/sci/computer-science/"
frontier = Frontier(initial_url)

crawler = Crawler(frontier, db_connection)  # Pass DBConnection to Crawler
crawler.run()  # Start the crawler

print("Crawling Completed")
