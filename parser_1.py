from db_connection import DBConnection
from bs4 import BeautifulSoup
from pymongo.errors import PyMongoError  # MongoDB error handling

import re
from crawlers import Crawler

# Instantiate DBConnection to connect to MongoDB
db_connection = DBConnection()
pages_collection = db_connection.db["pages"]
professors_collection = db_connection.db["professors"]

# Retrieve the HTML content from MongoDB using the specified URL
faculty_page = pages_collection.find_one(
    {"url": "https://www.cpp.edu/engineering/ce/faculty.shtml"}
)

# Check if the faculty page is found and contains HTML content
if not faculty_page:
    print("Faculty page not found in the database.")
elif "html" not in faculty_page:
    print("No HTML content found in the faculty page.")
else:
    html_content = faculty_page["html"]
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract professor information from the HTML content
    professor_cards = soup.find_all("div", class_="card-body d-flex flex-column align-items-start")

    if not professor_cards:
        print("No professor information found.")
    else:
        professor_data = {}
        highest_id = 0
        for card in professor_cards:
            highest_id += 1

            #Assigns a number for every id
            professor_data["_id"] = highest_id

            # Extracting professor details from the HTML structure from "Faculty & Staff"
            name_tag = card.find("h3", class_="mb-0")
            professor_data["name"] = name_tag.text.strip() if name_tag else "Unknown"

            title_tag = card.find("div", class_="mb-1 text-muted")
            professor_data["title"] = title_tag.get_text(strip=True) if title_tag else "Unknown"

            email_tag = card.find("a", href=lambda x: x and "mailto:" in x)
            professor_data["email"] = email_tag["href"].replace("mailto:", "") if email_tag else "Unknown"

            website_tag = card.find("a", href=lambda x: x and "http" in x)
            professor_data["website"] = website_tag["href"] if website_tag else "Unknown"

            #Insert the professor data into the MongoDB collection
            try:
                professors_collection.insert_one(professor_data)
            except PyMongoError as e:
                print(f"Failed to insert professor data: {e}")

    CrawObj = Crawler()

    regex = re.compile("^https://www\.cpp\.edu/faculty/")
    lookFor = {"website": {"$regex": regex}}

    # Retrieve the HTML content from MongoDB using the specified URL
    Professors_Pages = professors_collection.find(lookFor)
    #temp = list(Professors_Pages)

    for link in Professors_Pages:
        #Extract Professor's "Research Interest" 
        html = CrawObj.retrieveHTML(link["website"])

        bs = BeautifulSoup(html, "html.parser")
            
        div_tag = bs.find("div", {"class":"row mbtm row-eq-height-fac"})
        Research = div_tag.find("aside").find("div", {"class":"accolades"}).get_text(strip=True) if div_tag else "unknown"

        another_tag = bs.find("div", {"class" : "section-menu"})
        Education = another_tag.find("div", {"class":"col"}).get_text(strip=True) if another_tag else "unknown"
        
        tag = bs.find("div", {"class" : "fac-info"})
        Contact = tag.find("div", {"class" : "span10"}).get_text(strip=True) if tag else "unknown"

        try:
            professors_collection.update_one({"_id":link["_id"]},{"$set":{"Research-Interest":Research}})
            professors_collection.update_one({"_id":link["_id"]},{"$set":{"Education":Education}})
            professors_collection.update_one({"_id":link["_id"]},{"$set":{"Contact-Info":Contact}})
        except PyMongoError as e:
            print(f"Failed to insert professor data: {e}")

    print("Professor information successfully stored in MongoDB.")
    print("Professor Research successfully stored in MongoDB.")

    

