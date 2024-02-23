from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from pymongo import InsertOne
import pandas as pd


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_product', methods=['POST'])
def process_product():
    choice = request.form.get('choice')

    if choice == 'add_single':
        # Handle single product addition
        product_name = request.form.get('product_name')
        label_image = request.files.get('label_image')
        product_images = request.files.getlist('product_images')
        inserted_document_id = add_single_product(product_name)
        details_from_db = get_product_details(product_name)
        return render_template('success.html', details={**details_from_db, 'Document ID': inserted_document_id})

    elif choice == 'add_bulk':
        # Handle bulk product addition
        excel_file = request.files.get('excel_file')
        inserted_document_ids = process_bulk_data(excel_file)
        return render_template('success_bulk.html', details={'Document IDs': inserted_document_ids})

    elif choice == 'delete_product':
        # Handle product deletion
        delete_product_name = request.form.get('delete_product_name')
        deleted_count = delete_product(delete_product_name)
        
        if deleted_count > 0:
            return render_template('success_delete.html', message=f'{deleted_count} product(s) deleted successfully!')
        else:
            return render_template('success_delete.html', message='Product not found for deletion.')

    return render_template('error.html', message='Invalid choice.')

@app.route('/bulk_insert', methods=['GET', 'POST'])
def bulk_insert():
    if request.method == 'POST':
        excel_file = request.files.get('excel_file')

        # Process the bulk data and get product IDs
        product_ids = process_bulk_data(excel_file)

        # Debugging: Print product IDs to the console
        print("Product IDs:", product_ids)

        # Redirect to the success page with product IDs
        return render_template('success_bulk.html', product_ids=product_ids)

    # return render_template('bulk_insert.html')

# Add the necessary function for processing bulk data
def process_bulk_data(excel_file):
   

    return "Excel sheet added sucessfully"

def add_single_product(product_name):
    connection_string = 'mongodb+srv://mandardeo:JrDwnJSxK9AAHc8S@cluster0.eosrlqk.mongodb.net/?retryWrites=true&w=majority'
    client = MongoClient(connection_string)
    db = client['Digital_catalog']
    collection = db['label']

    existing_document = collection.find_one({'product_name': product_name})

    if existing_document:
        print(f"Product '{product_name}' already exists with ID: {existing_document['_id']}")
        return existing_document['_id']
    else:
        document = {'product_name': product_name}
        result = collection.insert_one(document)
        inserted_id = result.inserted_id
        print(f"Inserted document ID: {inserted_id}")
        client.close()
        return inserted_id

def get_product_details(product_name):
    connection_string = 'mongodb://localhost:27017'
    client = MongoClient(connection_string)
    db = client['Digital_catalog']
    collection = db['label']

    # Fetch details from MongoDB based on the product_name
    product_document = collection.find_one({'product_name': product_name})

    # Close MongoDB client connection
    client.close()

    print("Retrieved document from MongoDB:", product_document)

    if product_document:
        return {
            'Product Name': product_document['product_name'],
            'Origin': product_document.get('origin', 'N/A'),
            'Size US': product_document.get('size_US', 'N/A'),
            'Size UK': product_document.get('size_UK', 'N/A'),
            'Size FR': product_document.get('size_FR', 'N/A'),
            'Size JP': product_document.get('size_JP', 'N/A'),
            'Barcode': product_document.get('barcode', 'N/A'),
            'Image': product_document.get('image', 'N/A'),
            'Image Type': product_document.get('image_type', 'N/A'),
        }
    else:
        return {'Product Name': 'Not Found'}

@app.route('/delete_product', methods=['GET', 'POST '])
def delete_product():
    if request.method == 'POST':
        product_name_to_delete = request.form.get('product_name')

        # TODO: Implement logic to delete the product from the database
        # For example, you might use MongoDB's collection.delete_one method
        # collection.delete_one({'product_name': product_name_to_delete})

        return render_template('success_delete.html', product_name=product_name_to_delete)

    # If the request method is GET, render the page to input the product name
    return render_template('delete_product.html')
def delete_product(product_name):
    connection_string = 'mongodb://localhost:27017'
    client = MongoClient(connection_string)
    db = client['Digital_catalog']
    collection = db['label']

    # Delete the product from MongoDB based on the product_name
    result = collection.delete_many({'product_name': product_name})
    deleted_count = result.deleted_count

    # Close MongoDB client connection
    client.close()

    return deleted_count

if __name__ == "__main__":
    app.run(debug=True)
