from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/images'

# Path to catalog.json file
catalog_file_path = os.path.join(os.path.dirname(__file__), 'catalog.json')

# Load catalog from JSON file on server start
if os.path.exists(catalog_file_path):
    with open(catalog_file_path, 'r') as f:
        catalog = json.load(f)
else:
    catalog = []

# Save the catalog to JSON whenever you add or update an item
def save_catalog():
    with open(catalog_file_path, 'w') as f:
        json.dump(catalog, f, indent=4)

# Mock login credentials
USER_CREDENTIALS = {'kiran': '1801'}

@app.route('/')
def index():
    query = request.args.get('query', '').lower()  # Convert query to lowercase
    category = request.args.get('category', 'all').lower()
    subcategory = request.args.get('subcategory', '').lower()

    # Start with all items
    filtered_catalog = catalog

    # Filter by search query
    if query:
        filtered_catalog = [item for item in filtered_catalog if query in item['name'].lower() or query in item['description'].lower()]
    
    # Filter by category if it's not "all"
    if category != 'all':
        filtered_catalog = [item for item in filtered_catalog if item['category'].lower() == category]
    
    # Filter by subcategory if specified
    if subcategory:
        filtered_catalog = [item for item in filtered_catalog if item['subcategory'].lower() == subcategory]

    limited_catalog = filtered_catalog[:6]  # Limit to the first 6 items for display
    return render_template('index.html', catalog=limited_catalog)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid login credentials!', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))

@app.route('/add_clothing', methods=['GET', 'POST'])
def add_clothing():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        category = request.form['category'].capitalize()  
        subcategory = request.form['subcategory'].capitalize()  
        brand = request.form['brand']
        color = request.form['color']
        size = request.form['size']

        # Handle multiple image upload
        images = request.files.getlist('images')
        image_filenames = []

        for image in images:
            if image:
                filename = secure_filename(image.filename)  # Secure the filename
                image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filenames.append(filename)

        global catalog  # Ensure catalog is a global variable

        # Add new clothing item to the catalog
        catalog.append({
            'name': name,
            'description': description,
            'category': category,
            'subcategory': subcategory,
            'brand': brand,
            'color': color,
            'size': size,
            'images': image_filenames  # Storing multiple images
        })

        save_catalog()  # Save the updated catalog to the JSON file

        return redirect(url_for('index'))

    return render_template('add_clothing.html')

@app.route('/edit_clothing/<int:item_id>', methods=['GET', 'POST'])
def edit_clothing(item_id):
    if request.method == 'POST':
        # Update clothing item
        item = catalog[item_id]
        item['name'] = request.form['name']
        item['description'] = request.form['description']
        item['category'] = request.form['category'].capitalize()
        item['subcategory'] = request.form['subcategory'].capitalize()
        item['brand'] = request.form['brand']
        item['color'] = request.form['color']
        item['size'] = request.form['size']

        # Handle updated images if any are uploaded
        images = request.files.getlist('images')
        if images and images[0].filename:  # Check if new images are uploaded
            image_filenames = []
            for image in images:
                if image:
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_filenames.append(filename)
            item['images'] = image_filenames  # Replace old images with new ones if uploaded

        save_catalog()  # Save changes to JSON file
        flash('Clothing item updated successfully!', 'success')
        return redirect(url_for('index'))
    else:
        # Load item data for editing
        item = catalog[item_id]
        return render_template('edit_clothing.html', item=item, item_id=item_id)

@app.route('/delete_clothing/<int:index>', methods=['POST'])
def delete_clothing(index):
    if session.get('logged_in'):
        catalog.pop(index)
        save_catalog()  # Save the updated catalog after deletion
        flash('Clothing item deleted!', 'success')
    return redirect(url_for('index'))

@app.route('/item/<int:item_id>')
def item_detail(item_id):
    item = catalog[item_id]  # Retrieve the item based on the ID
    return render_template('item_detail.html', item=item)

if __name__ == '__main__':
    app.run(debug=True)
