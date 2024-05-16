from db_connection import DBConnection
from bs4 import BeautifulSoup
from pymongo.errors import PyMongoError  # MongoDB error handling
import re
from crawlers import Crawler

# Instantiate DBConnection to connect to MongoDB
db_connection = DBConnection()
pages_collection = db_connection.db["pages"]
professors_collection = db_connection.db["professors"]

# Instantiate Crawler
crawler = Crawler()

# Retrieve the HTML content from MongoDB using the specified URL
faculty_page = pages_collection.find_one({"url": "https://www.cpp.edu/engineering/ce/faculty.shtml"})

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
        highest_id = 0
        for card in professor_cards:
            professor_data = {}

            highest_id += 1

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

            # Insert the professor data into the MongoDB collection
            try:
                professors_collection.insert_one(professor_data)
            except PyMongoError as e:
                print(f"Failed to insert professor data: {e}")

print("Professor information successfully stored in MongoDB.")

# Retrieve professors' data from MongoDB
professors = professors_collection.find({"website": {"$regex": "^https://www\.cpp\.edu/faculty/"}})


# Iterate through each professor's data
for professor in professors:
    # Extract professor's additional information from their website
    html = crawler.retrieveHTML(professor["website"])
    soup = BeautifulSoup(html, "html.parser")
    
    # # Extract research interests
    # research_div = soup.find("div", class_="accolades")
    # research_interests = ''
    # if research_div:
    #     research_interests = ' '.join(text for text in research_div.stripped_strings if not text.startswith('Research Interests'))
    # else:
    #     research_interests = "Unknown"
    
    # # Extract education information
    # education_div = soup.find("div", class_="section-menu")
    # education = education_div.find("div", class_="col").get_text(strip=True) if education_div else "Unknown"
    
    # # Extract contact information
    # contact_div = soup.find("div", class_="fac-info")
    # contact_info = contact_div.find("div", class_="span10").get_text(strip=True) if contact_div else "Unknown"
    
    # # Replace newline characters with spaces
    # research_interests = research_interests.replace("\n", " ")
    # education = education.replace("\n", " ")
    # contact_info = contact_info.replace("\n", " ")
    
    # # Combine all information into one block as a string
    # info = f"{research_interests} {education} {contact_info}"

    everything_search = soup.find("div", class_="row pgtop")
    eve = everything_search.get_text(strip=True) if everything_search else "unknown"
    eve_info = eve.replace("\n"," ")

    info = f"{eve_info}"

    
    # Update professor's record in the database with the extracted information
    try:
        professors_collection.update_one(
            {"_id": professor["_id"]},
            {"$set": {"info": info}}
        )
    except PyMongoError as e:
        print(f"Failed to update professor data: {e}")

print("Professor information successfully updated in MongoDB.")
