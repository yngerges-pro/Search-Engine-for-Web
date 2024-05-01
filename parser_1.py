from db_connection import DBConnection
from bs4 import BeautifulSoup
from pymongo.errors import PyMongoError  # MongoDB error handling

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
        for card in professor_cards:
            professor_data = {}

            # Extracting professor details from the HTML structure
            name_tag = card.find("h3", class_="mb-0")
            professor_data["name"] = name_tag.text.strip() if name_tag else "Unknown"

            title_tag = card.find("div", class_="mb-1 text-muted")
            professor_data["title"] = title_tag.get_text(strip=True) if title_tag else "Unknown"

# Still trying to understand why value and info does not exist
#-----------------------------------------------------------------------------------------------------------------
            span_tags = card.find("ul").find_all("span", class_= "sr-only")
            value = span_tags[0].find_next_siblings() if span_tags[0] else "Unknown"
            if value:
                professor_data["phone"] = value.text.strip()

            info = span_tags[1].find_next_siblings() if span_tags[1] else "Unknown"
            if info:
                professor_data["office"] = info.text.strip()
#------------------------------------------------------------------------------------------------------------------

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
