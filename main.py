from flask import Flask, render_template, request, redirect, url_for

from utils import get_db_connection, load_sql_file

app = Flask(__name__)


# -----------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    """
    Home page route. Iinstantiate database tables (if not already exists) & Fetches all products from the 'products' table
    and displays them in a simple HTML table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables if not exists 
    # ---------
    
    query = load_sql_file("sql/ddl.sql")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()

    # Select all products
    # ---------
    
    query = load_sql_file("sql/list_product_variants.sql")
    cursor.execute(query)
    products = cursor.fetchall()  # returns list of tuples
    cursor.close()
    conn.close()

    # Return html table with products
    # ---------
    
    return render_template("products.html", products=products)

@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    """
    GET: Show a form to add a new product, including category options.
    POST: Insert the new product into the 'products' table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        sku = request.form.get("sku")
        price = request.form.get("price")
        description = request.form.get("description")
        category_id = request.form.get("category_id")

        # Insert product
        query = load_sql_file("sql/add_product.sql")
        cursor.execute(query, (name, sku, price, description, category_id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("index"))

    # Fetch categories for the form
    query = load_sql_file("sql/list_categories.sql")
    cursor.execute(query)
    categories = cursor.fetchall()

    conn.close()
    return render_template("add_product.html", categories=categories)


@app.route("/edit_product/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    """
    GET: Show a form pre-populated with the current product details.
    POST: Update the product in the 'products' table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        sku = request.form.get("sku")
        price = request.form.get("price")
        description = request.form.get("description")
        category_id = request.form.get("category_id")

        # Update product
        query = load_sql_file("sql/edit_product.sql")
        cursor.execute(query, (name, sku, price, description, category_id, product_id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("index"))

    # Fetch product details
    query = load_sql_file("sql/select_product_to_edit.sql")
    cursor.execute(query, (product_id,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        conn.close()
        return "Product not found.", 404

    # Fetch all categories
    query = load_sql_file("sql/list_categories.sql")
    cursor.execute(query)
    categories = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("edit_product.html", product=product, categories=categories)




@app.route("/delete_product/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    """
    Deletes a product from the 'products' table by its ID.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete the product by ID
    # -----------
    
    query = load_sql_file("sql/delete_product.sql")
    cursor.execute(query, (product_id,))
    conn.commit()

    cursor.close()
    conn.close()

    # Redirect back to the home page
    return redirect(url_for("index"))


@app.route("/categories")
def categories():

    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all categories
    # -----------
    
    query = load_sql_file("sql/list_categories.sql")
    cursor.execute(query)
    categories = cursor.fetchall()
    conn.close()
    
    return render_template("categories.html", categories=categories)

@app.route("/categories/add", methods=["GET", "POST"])
def add_category():
    if request.method == "POST":

        # Get form details
        name = request.form.get("name")
        description = request.form.get("description")
        
        conn = get_db_connection()
        cursor = conn.cursor()

        # INSERT (add) category
        # -----------

        query = load_sql_file("sql/add_category.sql")
        cursor.execute(query, (name, description))
        conn.commit()
        conn.close()
        return redirect(url_for("categories"))

    elif request.method == "GET":
        return render_template("add_category.html")

@app.route("/categories/edit/<int:id>", methods=["GET", "POST"])
def edit_category(id):

    # Create db connection
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        # Get form details
        # -------------
        
        name = request.form.get("name")
        description = request.form.get("description")

        # UPDATE (edit) category
        # -------------
        
        query = load_sql_file("sql/edit_category.sql")
        cursor.execute(query, (name, description, id))
        conn.commit()
        conn.close()
        
        return redirect(url_for("categories"))
        
    else:

        # GET/Fetch/Select category to render form for edit
        # -------------
        
        query = load_sql_file("sql/select_category_to_edit.sql")
        cursor.execute(query, (id,))
        category = cursor.fetchone()
        conn.close()
        
        return render_template("edit_category.html", category=category)

@app.route("/categories/delete/<int:id>", methods=["POST"])
def delete_category(id):

    # Create db connection
    # ------------
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # DELETE category
    # ------------
    
    query = load_sql_file("sql/delete_category.sql")
    cursor.execute(query, (id,))
    conn.commit()
    conn.close()
    
    return redirect(url_for("categories"))

@app.route("/flavors")
def flavors():
    """
    Fetches all flavors from the database and displays them in a table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = load_sql_file("sql/list_flavors.sql")
    cursor.execute(query)
    flavors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("flavors.html", flavors=flavors)


@app.route("/flavors/add", methods=["GET", "POST"])
def add_flavor():
    """
    GET: Show a form to add a new flavor.
    POST: Insert the new flavor into the 'flavors' table.
    """
    if request.method == "POST":
        # Get form data
        name = request.form.get("name")

        # Insert into flavors table
        query = load_sql_file("sql/add_flavor.sql")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (name))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("flavors"))

    return render_template("add_flavor.html")

@app.route("/flavors/edit/<int:id>", methods=["GET", "POST"])
def edit_flavor(id):
    """
    GET: Show a form pre-populated with the current flavor details.
    POST: Update the flavor in the 'flavors' table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")

        # Update flavor
        query = load_sql_file("sql/edit_flavor.sql")
        cursor.execute(query, (name, id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("flavors"))

    # Fetch flavor details
    query = load_sql_file("sql/select_flavor_to_edit.sql")
    cursor.execute(query, (id,))
    flavor = cursor.fetchone()

    cursor.close()
    conn.close()

    if not flavor:
        return "Flavor not found.", 404

    return render_template("edit_flavor.html", flavor=flavor)

@app.route("/flavors/delete/<int:id>", methods=["POST"])
def delete_flavor(id):
    """
    Deletes a flavor from the 'flavors' table by its ID.
    """
    query = load_sql_file("sql/delete_flavor.sql")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (id,))
    conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for("flavors"))

        
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5000)
