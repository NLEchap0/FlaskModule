import os
import json


PRODUCTS_DATA_FILE = "products.json"

def validate_product(data):
    errors = {}
    if not data.get('name') or not data['name']:
        errors['name'] = "Name is required"
        
    if not data.get('category') or not data['category']:
        errors['category'] = "Category is required"
    
    if not data.get('price') or not data['price']:
        errors['price'] = "Price is required"
    else:
        #TODO chk if number
        try:
            if float(data['price']) < 0:
                errors['price'] = "Price must be >= 0"
        except (TypeError, ValueError):
            # except Exception as e: #chatces all exceptions, not elegant
            errors['price'] = "Price must be a number"
            
     
    ''' we use the dict approach for future use of the keys'''   
    # errors = []
    # if not data.get('name') or not data['name']:
    #    errors.append( "Name is required" )
    
    return errors

def save_product(data):
    #TODO read all products
    products = read_products()
    
    #TODO append new product to list of products
    products.append(data)
    
    #TODO save
    save_all_products(products)

def save_all_products(products):
    with open(PRODUCTS_DATA_FILE, "w") as f:
        json.dump(products, f, indent=2)

def read_products():
    try:
        with open(PRODUCTS_DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
