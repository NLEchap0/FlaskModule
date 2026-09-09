from flask import Blueprint, render_template, request, redirect, url_for
from modules.utils import validate_product, save_product, read_products

app = Blueprint('frontend', __name__)


@app.route("/")
def home():
    return render_template('base.html')

@app.route('/form')
def product_form():
    return render_template('product_form.html')

@app.route('/form', methods=['POST'])
def product_form_submit():
    data = {
        "name" : request.form.get('name', "").strip(),    #short form for name = request.form['name'] if 'name' in request.form else None
        "description" : request.form.get('description', "").strip(),
        "price": request.form.get('price', "").strip(),
        "category": request.form.get('category', "").strip()
    }
    
    errors = validate_product(data)
    data['price'] = float( data['price'] )
    
    
    if errors:
        return render_template('product_form.html', errors=errors, form_data=data)
    
    save_product(data)
    
    return redirect(url_for('frontend.products_list'))

@app.route("/products", methods=["GET"])
def products_list():
    products = read_products()
    return render_template('products_list.html', products=products)
