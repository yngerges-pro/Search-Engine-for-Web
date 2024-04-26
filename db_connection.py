from pymongo import MongoClient

class DBConnection:
    def __init__(self, host='localhost', port=27017, db_name='cpp_search_engine'):
        self.client = MongoClient(f'mongodb://{host}:{port}/')
        self.db = self.client[db_name]
        self.collection = self.db['pages']

    def insert_page(self, data):
        if 'url' not in data or 'html' not in data:  
            raise ValueError("URL and HTML are required fields.")  
          # Insert the page into the database
        self.collection.insert_one(data)  

    def get_all_pages(self):
        return list(self.collection.find())

    def update_page(self, url, updated_data):
 
        # Check if the page exists
        if not self.collection.find_one({'url': url}):
            raise ValueError(f"Page with URL '{url}' not found.")
        
        # Update the page in the database
        self.collection.update_one({'url': url}, {'$set': updated_data})

    def delete_page(self, url):
        
        # Check if the page exists
        if not self.collection.find_one({'url': url}):
            raise ValueError(f"Page with URL '{url}' not found.")
        
        # Delete the page from the database
        self.collection.delete_one({'url': url})