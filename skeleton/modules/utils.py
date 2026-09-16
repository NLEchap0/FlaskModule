import os
import json
from flask import jsonify
from models.conn import db
from models.model import Product

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
    #product = Product(**data)
    product = Product(name = data['name'],
                      description = data['description'],
                      price= data['price']
                      )
    try:
        db.session.add(product)
        db.session.commit()
        return jsonify(product.to_dict()), 201
    except Exception as e:
        response = {'error':str(e), 'message':'error while saving product'}
        return jsonify(response), 500


def read_products():
    #read all Product obejct as model and return a json list
    data = []
    products = Product.query.all()
    for product in products:
        data.append( product.to_dict() )
    return data

