from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask.json import loads

import json

from utils import get_db_connection, load_sql_file

app = Flask(__name__, static_folder="static")

# Add the 'fromjson' filter
app.jinja_env.filters['fromjson'] = loads

# -----------------------------------------------------------------------------
# ROUTES
# -----------------------------------------------------------------------------


@app.route("/")
def home():
    """
    Home page route.
    Displays the home page with navigation blocks to other pages.
    """
    return render_template("home.html")


@app.route("/products")
def products():
    """
    Home page route. Instantiate database tables (if not already exists) & Fetches all products from the 'products' table
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

    query = load_sql_file("sql/list_product_variant_details.sql")
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
    GET: Show a form to add a new product.
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
        flavor_id = request.form.get("flavor_id") or None  # optional
        size_id = request.form.get("size_id")

        # Form Validation
        # ---------

        # Check if SKU already exists
        query = "SELECT COUNT(*) FROM products WHERE sku = %s;"
        cursor.execute(query, (sku, ))
        sku_exists = cursor.fetchone()[0] > 0

        if sku_exists:

            # Fetch dropdown options
            query = load_sql_file("sql/list_categories.sql")
            cursor.execute(query)
            categories = cursor.fetchall()

            query = load_sql_file("sql/list_flavors.sql")
            cursor.execute(query)
            flavors = cursor.fetchall()

            query = load_sql_file("sql/list_sizes.sql")
            cursor.execute(query)
            sizes = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template(
                "add_product.html",
                error_message=
                f"The SKU '{sku}' already exists. Please use a unique SKU.",
                categories=categories,
                flavors=flavors,
                sizes=sizes,
            )

        # Insert product
        query = load_sql_file("sql/add_product.sql")
        cursor.execute(
            query,
            (name, sku, price, description, category_id, flavor_id, size_id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("products"))

    # Fetch dropdown options
    query = load_sql_file("sql/list_categories.sql")
    cursor.execute(query)
    categories = cursor.fetchall()

    query = load_sql_file("sql/list_flavors.sql")
    cursor.execute(query)
    flavors = cursor.fetchall()

    query = load_sql_file("sql/list_sizes.sql")
    cursor.execute(query)
    sizes = cursor.fetchall()

    conn.close()
    return render_template("add_product.html",
                           categories=categories,
                           flavors=flavors,
                           sizes=sizes)


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
        flavor_id = request.form.get("flavor_id") or None  # Optional
        size_id = request.form.get("size_id") or None  # Optional

        # Update product
        query = load_sql_file("sql/edit_product.sql")
        cursor.execute(query, (name, sku, price, description, category_id,
                               flavor_id, size_id, product_id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("products"))

    # Fetch product details
    query = load_sql_file("sql/select_product_to_edit.sql")
    cursor.execute(query, (product_id, ))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        conn.close()
        return "Product not found.", 404

    # Fetch dropdown options
    query = load_sql_file("sql/list_categories.sql")
    cursor.execute(query)
    categories = cursor.fetchall()

    query = load_sql_file("sql/list_flavors.sql")
    cursor.execute(query)
    flavors = cursor.fetchall()

    query = load_sql_file("sql/list_sizes.sql")
    cursor.execute(query)
    sizes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("edit_product.html",
                           product=product,
                           categories=categories,
                           flavors=flavors,
                           sizes=sizes)


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
    cursor.execute(query, (product_id, ))
    conn.commit()

    cursor.close()
    conn.close()

    # Redirect back to the home page
    return redirect(url_for("products"))

@app.route("/product/<int:product_id>", methods=["GET"])
def product_detail(product_id):
    """
    Fetch and display product details along with its snapshots.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Load queries from SQL files
    product_query = load_sql_file("sql/get_product_details.sql")
    snapshot_query = load_sql_file("sql/get_product_snapshots.sql")

    # Fetch product details
    cursor.execute(product_query, (product_id,))
    product = cursor.fetchone()

    if not product:
        cursor.close()
        conn.close()
        return "Product not found.", 404

    # Ensure price is a float before passing it to the template
    product = list(product)  # Convert tuple to list (mutable)
    try:
        product[3] = float(product[3])  # Convert price to float
    except ValueError:
        product[3] = 0.00  # Default value if conversion fails

    # Fetch snapshots for the product
    cursor.execute(snapshot_query, (product_id,))
    snapshots = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("product_detail.html", product=product, snapshots=snapshots)

@app.route("/product/<int:product_id>/create_snapshot", methods=["GET"])
def create_snapshot_form(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    product_query = load_sql_file("sql/get_product_details.sql")
    recipe_query = load_sql_file("sql/get_product_recipes.sql")

    cursor.execute(product_query, (product_id,))
    product = cursor.fetchone()

    cursor.execute(recipe_query, (product_id,))
    recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("create_snapshot.html", product=product, recipes=recipes)

@app.route("/products/<int:product_id>/snapshots/<int:snapshot_version>")
def view_snapshot(product_id, snapshot_version):
    """
    Fetches and displays a specific product snapshot.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch snapshot details
    query = load_sql_file("sql/get_product_snapshot.sql")
    cursor.execute(query, (product_id, snapshot_version))
    snapshot = cursor.fetchone()

    cursor.close()
    conn.close()

    if not snapshot:
        return "Snapshot not found.", 404

    return render_template("view_snapshot.html", snapshot=snapshot)

@app.route("/create_snapshot", methods=["POST"])
def create_snapshot():
    try:
        product_id = request.form.get("product_id")
        recipe_version = request.form.get("recipe_version")

        print("Product ID:", product_id)
        print("Recipe Version:", recipe_version)

        if not product_id or not recipe_version:
            raise ValueError("Missing product_id or recipe_version")

        # Load SQL files
        insert_query = load_sql_file("sql/insert_product_snapshot.sql")
        product_details_query = load_sql_file("sql/get_product_details_for_snapshot.sql")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch product details
        cursor.execute(product_details_query, (product_id,))
        product_details = cursor.fetchone()

        if not product_details:
            raise ValueError("Product not found")

        name, sku, category_id, category_name, flavor_id, flavor_name, size_id, size_name = product_details

        print("Executing Insert Query with:", product_id, recipe_version, name, sku, category_id, category_name, flavor_id, flavor_name, size_id, size_name)

        # Execute insert query
        cursor.execute(insert_query, (
            product_id, product_id, name, sku, category_id, category_name,
            flavor_id, flavor_name, size_id, size_name, recipe_version
        ))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"success": True, "message": "Snapshot created successfully!"})

    except Exception as e:
        print("Error inserting snapshot:", str(e))
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/search_products", methods=["GET"])
def search_products():
    """
    Searches for products by name (case-insensitive) and returns matching results.
    """
    query = request.args.get("query", "").strip()

    print(f"Searching for products with query: {query}")

    if not query:
        return jsonify([])  # Return empty list if no query provided

    conn = get_db_connection()
    cursor = conn.cursor()

    # Load SQL query from file
    sql_query = load_sql_file("sql/search_products.sql")

    try:
        cursor.execute(sql_query, ('%' + query + '%',))  # Search by name (LIKE %query%)
        products = cursor.fetchall()
        cursor.close()
        conn.close()

        print(f"Found {len(products)} products matching the query.")

        # Format response as a list of dictionaries
        return jsonify([{
            "id": product[0],
            "name": product[1]
        } for product in products])

    except Exception as e:
        cursor.close()
        conn.close()
        return jsonify({"error": str(e)}), 500  # Return error response


@app.route("/fetch_product_snapshots", methods=["GET"])
def fetch_product_snapshots():
    """
    Fetches all existing product snapshots for a given product ID.
    """
    product_id = request.args.get("product_id")

    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Load SQL query from file
    sql_query = load_sql_file("sql/get_product_snapshots.sql")

    cursor.execute(sql_query, (product_id,))
    snapshots = cursor.fetchall()

    cursor.close()
    conn.close()

    # Format response as a list of dictionaries
    results = [{
        "snapshot_id": snapshot[0],
        "version": snapshot[1],
        "created_at": snapshot[2]
    } for snapshot in snapshots]

    return jsonify(results)


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
        cursor.execute(query, (id, ))
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
    cursor.execute(query, (id, ))
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
        cursor.execute(query, (name, ))
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
    cursor.execute(query, (id, ))
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
    cursor.execute(query, (id, ))
    conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for("flavors"))


@app.route("/sizes")
def sizes():
    """
    Fetches all sizes from the database and displays them.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = load_sql_file("sql/list_sizes.sql")
    cursor.execute(query)
    sizes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("sizes.html", sizes=sizes)


@app.route("/sizes/add", methods=["GET", "POST"])
def add_size():
    """
    GET: Show a form to add a new size.
    POST: Insert the new size into the 'sizes' table.
    """
    if request.method == "POST":
        name = request.form.get("name")
        weight_g = request.form.get("weight_g") or None  # Weight is optional

        query = load_sql_file("sql/add_size.sql")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (name, weight_g))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("sizes"))

    return render_template("add_size.html")


@app.route("/sizes/edit/<int:id>", methods=["GET", "POST"])
def edit_size(id):
    """
    GET: Show a form pre-populated with the current size details.
    POST: Update the size in the 'sizes' table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form.get("name")
        weight_g = request.form.get("weight_g") or None  # Weight is optional

        query = load_sql_file("sql/edit_size.sql")
        cursor.execute(query, (name, weight_g, id))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("list_sizes"))

    # Fetch size details
    query = load_sql_file("sql/select_size_to_edit.sql")
    cursor.execute(query, (id, ))
    size = cursor.fetchone()

    cursor.close()
    conn.close()

    if not size:
        return "Size not found.", 404

    return render_template("edit_size.html", size=size)


@app.route("/sizes/delete/<int:id>", methods=["POST"])
def delete_size(id):
    """
    Deletes a size from the 'sizes' table by its ID.
    """
    query = load_sql_file("sql/delete_size.sql")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, (id, ))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("list_sizes"))


@app.route("/manufacturing_orders")
def manufacturing_orders():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = load_sql_file("sql/list_manufacturing_orders.sql")
    cursor.execute(query)
    manufacturing_orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("manufacturing_orders.html",
                           manufacturing_orders=manufacturing_orders)


@app.route("/manufacturing_orders/add", methods=["GET", "POST"])
def add_manufacturing_order():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        weight_g = float(request.form.get("weight_g"))
        units_to_produce = int(request.form.get("units_to_produce"))
        planned_start_date = request.form.get("planned_start_date")

        # Calculate total grams required
        total_grams = weight_g * units_to_produce

        query = load_sql_file("sql/add_manufacturing_order.sql")
        cursor.execute(query,
                       (product_id, units_to_produce, planned_start_date))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("manufacturing_orders"))

    # Fetch products with grams per unit
    query = load_sql_file("sql/fetch_products.sql")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("add_manufacturing_order.html",
                           products=products,
                           sizes=sizes)


@app.route("/manufacturing_orders/edit/<int:id>", methods=["GET", "POST"])
def edit_manufacturing_order(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        size_id = request.form.get("size_id")
        units_to_produce = request.form.get("units_to_produce")
        planned_start_date = request.form.get("planned_start_date")

        query = load_sql_file("sql/edit_manufacturing_order.sql")
        cursor.execute(
            query,
            (product_id, size_id, units_to_produce, planned_start_date, id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("manufacturing_orders"))

    # Fetch manufacturing order details
    query = load_sql_file("sql/select_manufacturing_order.sql")
    cursor.execute(query, (id, ))
    manufacturing_order = cursor.fetchone()

    if not manufacturing_order:
        cursor.close()
        conn.close()
        return "Manufacturing order not found.", 404

    # Fetch dropdown options
    query = load_sql_file("sql/list_products.sql")
    cursor.execute(query)
    products = cursor.fetchall()

    query = load_sql_file("sql/list_sizes.sql")
    cursor.execute(query)
    sizes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("edit_manufacturing_order.html",
                           manufacturing_order=manufacturing_order,
                           products=products,
                           sizes=sizes)


@app.route("/manufacturing_orders/delete/<int:id>", methods=["POST"])
def delete_manufacturing_order(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = load_sql_file("sql/delete_manufacturing_order.sql")
    cursor.execute(query, (id, ))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("manufacturing_orders"))


@app.route("/manufacturing_orders/update_status/<int:id>", methods=["POST"])
def update_manufacturing_order_status(id):
    """
    Update the status of a manufacturing order.
    """
    new_status = request.form.get("status")  # 'In Progress' or 'Complete'
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch the MO details
    query = load_sql_file("sql/select_mo_details.sql")
    cursor.execute(query, (id, ))
    mo = cursor.fetchone()

    if not mo:
        cursor.close()
        conn.close()
        return "Manufacturing order not found.", 404

    product_id, units_to_produce, current_status = mo

    if current_status == "Complete":
        cursor.close()
        conn.close()
        return "Cannot change status of a completed manufacturing order.", 400

    # Handle transitions
    if current_status == "Pending" and new_status == "In Progress":
        # Reserve raw materials
        query = load_sql_file("sql/list_bom_for_product.sql")
        cursor.execute(query, (product_id, ))
        raw_materials = cursor.fetchall()

        for rm_id, available, accounted, quantity_per_unit in raw_materials:
            total_required = units_to_produce * quantity_per_unit
            if available < total_required:
                cursor.close()
                conn.close()
                return f"Not enough raw material (ID: {rm_id}). Needed: {total_required}, Available: {available}", 400
            # Reserve the materials
            query = load_sql_file("sql/reserve_raw_materials.sql")
            cursor.execute(query, (total_required, total_required, rm_id))

    elif current_status == "In Progress" and new_status == "Complete":
        # Deduct raw materials
        query = load_sql_file("sql/list_bom_for_product.sql")
        cursor.execute(query, (product_id, ))
        raw_materials = cursor.fetchall()

        for rm_id, accounted, quantity_per_unit in raw_materials:
            total_used = units_to_produce * quantity_per_unit
            query = load_sql_file("sql/deduct_raw_materials.sql")
            cursor.execute(query, (total_used, rm_id))

    # Update the MO status
    query = load_sql_file("sql/update_mo_status.sql")
    cursor.execute(query, (new_status, id))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("list_manufacturing_orders"))


@app.route("/raw_materials")
def raw_materials():
    """
    Display all raw materials with their associated details and tags.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch raw materials
    query = load_sql_file("sql/list_raw_materials.sql")
    cursor.execute(query)
    raw_materials = cursor.fetchall()

    # Process tags column
    formatted_raw_materials = []
    for raw_material in raw_materials:
        raw_material = list(raw_material)  # Convert tuple to list
        tags = raw_material[8]  # Extract tags column

        # Handle tags if it's a list containing a JSON string
        if isinstance(tags, list) and len(tags) == 1 and isinstance(
                tags[0], str):
            try:
                raw_material[8] = json.loads(
                    tags[0])  # Deserialize JSON string
            except json.JSONDecodeError:
                raw_material[8] = []  # Default to empty list on error
        elif not isinstance(tags, list):
            raw_material[8] = [
            ]  # Default to empty list if tags are not a list

        formatted_raw_materials.append(raw_material)

    print(formatted_raw_materials)

    cursor.close()
    conn.close()

    return render_template("raw_materials.html",
                           raw_materials=formatted_raw_materials)


@app.route("/fetch_raw_materials", methods=["GET"])
def fetch_raw_materials():
    """
    Fetches all raw materials to update dropdown options dynamically.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = load_sql_file("sql/list_raw_materials.sql")
    cursor.execute(query)
    raw_materials = cursor.fetchall()

    cursor.close()
    conn.close()

    # Convert tuple results to dictionaries for JSON response
    raw_materials_list = [{
        "id": rm[0],
        "name": rm[1],
        "vendor": rm[2],
        "unit_of_measure_name": rm[3]
    } for rm in raw_materials]

    return jsonify(raw_materials_list)


@app.route("/raw_materials/add", methods=["GET", "POST"])
def add_raw_material():
    """
    Add a new raw material with dynamic tag support.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        vendor_id = request.form.get("vendor_id")
        unit_of_measure_id = request.form.get("unit_of_measure_id")
        moq = request.form.get("moq")
        tags = request.form.get("tags").split(
            ",")  # Split comma-separated tags into a list

        # Add new tags to the `tags` table
        for tag in tags:
            query = load_sql_file("sql/add_tag.sql")
            cursor.execute(query,
                           (tag.strip(), ))  # Add tag, ignore duplicates

        # Add raw material with tags as JSONB
        query = load_sql_file("sql/add_raw_material.sql")
        cursor.execute(
            query,
            (name, vendor_id, unit_of_measure_id, moq, json.dumps(tags)))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("raw_materials"))

    # Fetch dropdown options
    query = load_sql_file("sql/list_vendors.sql")
    cursor.execute(query)
    vendors = cursor.fetchall()

    query = load_sql_file("sql/list_unit_of_measure.sql")
    cursor.execute(query)
    unit_of_measure = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("add_raw_material.html",
                           vendors=vendors,
                           unit_of_measure=unit_of_measure)


@app.route("/raw_materials/edit/<int:id>", methods=["GET", "POST"])
def edit_raw_material(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        vendor_id = request.form.get("vendor_id")
        unit_of_measure_id = request.form.get("unit_of_measure_id")
        moq = request.form.get("moq")
        tags = request.form.get("tags")  # Get CSV string of tags

        # Split CSV into a list of tag strings
        if tags:
            tags_list = [{"value": tag.strip()} for tag in tags.split(',')]

        # Serialize tags to JSON
        tags_json = json.dumps(tags_list)

        # Update raw material in the database
        query = load_sql_file("sql/edit_raw_material.sql")
        cursor.execute(
            query, (name, vendor_id, unit_of_measure_id, moq, tags_json, id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("raw_materials"))

    # Fetch raw material details
    query = load_sql_file("sql/select_raw_material_to_edit.sql")
    cursor.execute(query, (id, ))
    raw_material = cursor.fetchone()

    if not raw_material:
        cursor.close()
        conn.close()
        return "Raw material not found.", 404

    # Fetch dropdown options
    query = load_sql_file("sql/list_vendors.sql")
    cursor.execute(query)
    vendors = cursor.fetchall()

    query = load_sql_file("sql/list_unit_of_measure.sql")
    cursor.execute(query)
    unit_of_measure = cursor.fetchall()

    query = load_sql_file("sql/list_tags.sql")
    cursor.execute(query)
    tags = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "edit_raw_material.html",
        raw_material=raw_material,
        vendors=vendors,
        unit_of_measure=unit_of_measure,
        tags=tags,
    )


@app.route("/raw_materials/delete/<int:id>", methods=["POST"])
def delete_raw_material(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = load_sql_file("sql/delete_raw_material.sql")
    cursor.execute(query, (id, ))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("raw_materials"))


@app.route("/raw_materials/stock_adjustment/<int:id>", methods=["GET", "POST"])
def stock_adjustment(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        # Get form data
        adjustment_amount = float(request.form.get("adjustment_amount"))
        adjustment_reason = request.form.get("adjustment_reason")

        # Fetch raw material details
        query = load_sql_file("sql/select_raw_material.sql")
        cursor.execute(query, (id, ))
        raw_material = cursor.fetchone()

        if not raw_material:
            cursor.close()
            conn.close()
            return "Raw material not found.", 404

        # Update total inventory directly
        query = load_sql_file("sql/update_total_inventory.sql")
        cursor.execute(query, (adjustment_amount, id))

        # Log stock adjustment for tracking (optional)
        query = load_sql_file("sql/add_stock_adjustment.sql")
        cursor.execute(
            query, (id, adjustment_amount, raw_material[2], adjustment_reason))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("raw_materials"))

    # Fetch raw material details for display
    query = load_sql_file("sql/select_raw_material.sql")
    cursor.execute(query, (id, ))
    raw_material = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("stock_adjustment.html", raw_material=raw_material)


@app.route("/vendors")
def vendors():
    conn = get_db_connection()
    cursor = conn.cursor()

    query = load_sql_file("sql/list_vendors.sql")
    cursor.execute(query)
    vendors = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("vendors.html", vendors=vendors)


@app.route("/vendors/fetch", methods=["GET"])
def fetch_vendors():
    """
    Fetch all vendors from the database for dynamic dropdown updates.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Load the SQL query from a file
    query = load_sql_file("sql/list_vendors.sql")
    cursor.execute(query)
    vendors = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify([{
        "id": vendor[0],
        "name": vendor[1]
    } for vendor in vendors])


@app.route("/vendors/add", methods=["GET", "POST"])
def add_vendor():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        address = request.form.get("address")
        description = request.form.get("description")
        notes = request.form.get("notes")

        query = load_sql_file("sql/add_vendor.sql")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, (name, email, address, description, notes))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for("vendors"))

    return render_template("add_vendor.html")


@app.route("/vendors/edit/<int:id>", methods=["GET", "POST"])
def edit_vendor(id):
    """
    GET: Fetch the vendor details and display the edit form.
    POST: Update the vendor details in the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        # Get form data
        name = request.form.get("name")
        email = request.form.get("email")
        address = request.form.get("address")
        description = request.form.get("description")
        notes = request.form.get("notes")

        # Update vendor in the database
        query = load_sql_file("sql/edit_vendor.sql")
        cursor.execute(query, (name, email, address, description, notes, id))
        conn.commit()

        cursor.close()
        conn.close()
        return redirect(url_for("vendors"))

    # Fetch vendor details for the edit form
    query = load_sql_file("sql/select_vendor.sql")
    cursor.execute(query, (id, ))
    vendor = cursor.fetchone()

    if not vendor:
        cursor.close()
        conn.close()
        return "Vendor not found.", 404

    cursor.close()
    conn.close()

    return render_template("edit_vendor.html", vendor=vendor)


@app.route("/vendors/delete/<int:id>", methods=["POST"])
def delete_vendor(id):
    """
    Deletes a vendor by ID from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete vendor by ID
    query = load_sql_file("sql/delete_vendor.sql")
    cursor.execute(query, (id, ))
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for("vendors"))


@app.route("/tags/fetch", methods=["GET"])
def fetch_tags():
    """
    Fetch all tags from the database for autocomplete suggestions.
    """
    print('fetch_tags()')

    conn = get_db_connection()
    cursor = conn.cursor()

    # Load the SQL query from a file
    query = load_sql_file("sql/list_tags.sql")
    cursor.execute(query)
    tags = cursor.fetchall()

    cursor.close()
    conn.close()

    # Ensure proper extraction of tag values
    clean_tags = []
    for tag_tuple in tags:
        tag_data = tag_tuple[0]  # Extract the first element from tuple
        if isinstance(tag_data, str):
            try:
                parsed_tag = json.loads(tag_data)  # Convert JSON string to dict
                if isinstance(parsed_tag, list):  # If it's a list of dicts
                    clean_tags.extend(tag["value"] for tag in parsed_tag if "value" in tag)
                elif isinstance(parsed_tag, dict) and "value" in parsed_tag:  # If it's a single dict
                    clean_tags.append(parsed_tag["value"])
            except json.JSONDecodeError:
                clean_tags.append(tag_data)  # If it's already a string, keep it as is
        elif isinstance(tag_data, dict) and "value" in tag_data:
            clean_tags.append(tag_data["value"])

    print(clean_tags)  # Debugging output to verify extraction

    return jsonify(clean_tags)  # Return a clean list of tag strings


@app.route("/recipes", methods=["GET"])
def recipes():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Load recipes query
    recipes_query = load_sql_file("sql/list_recipes.sql")
    cursor.execute(recipes_query)
    rows = cursor.fetchall()

    # Extract column names from cursor description
    columns = [desc[0] for desc in cursor.description]

    # Convert rows to dictionaries
    recipes = []
    for row in rows:
        recipe = dict(zip(columns, row))

        # Ensure raw_materials is parsed correctly
        if isinstance(recipe.get("raw_materials"), str):
            recipe["raw_materials"] = json.loads(recipe["raw_materials"])
        elif recipe.get("raw_materials") is None:
            recipe["raw_materials"] = []

        # Ensure recipe_id and product_id are explicitly included
        recipe["recipe_id"] = recipe.get("recipe_id")
        recipe["product_id"] = recipe.get("product_id")  # Add product_id
        recipes.append(recipe)

    # Load products query
    products_query = load_sql_file("sql/list_products.sql")
    cursor.execute(products_query)
    products = cursor.fetchall()  # Fetch products

    cursor.close()
    conn.close()

    # Get selected product from query parameter
    selected_product_id = request.args.get("product_id", "")

    print(json.dumps(recipes, indent=2))

    return render_template("recipes.html",
                           recipes=recipes,
                           products=products,
                           selected_product_id=selected_product_id)


@app.route("/recipes/add", methods=["GET", "POST"])
def add_recipe():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        product_id = request.form.get("product_id")
        raw_materials = request.form.getlist("raw_material_id[]")
        quantities = request.form.getlist("quantity[]")

        if not product_id:
            return "Error: Product ID is required", 400

        # Ensure a version is assigned
        query = load_sql_file("sql/add_recipe.sql")
        cursor.execute(query,
                       (product_id, product_id))  # Pass product_id twice
        recipe_id, version = cursor.fetchone()

        # Insert raw materials into recipe_raw_materials
        query = load_sql_file("sql/add_recipe_raw_material.sql")
        for raw_material_id, quantity in zip(raw_materials, quantities):
            cursor.execute(query, (recipe_id, raw_material_id, quantity))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect(url_for("recipes"))

    # Fetch available products
    query = load_sql_file("sql/list_products.sql")
    cursor.execute(query)
    products = cursor.fetchall()

    # Fetch raw materials
    query = load_sql_file("sql/list_raw_materials.sql")
    cursor.execute(query)
    raw_materials = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("add_recipe.html",
                           products=products,
                           raw_materials=raw_materials)


@app.route("/recipes/edit/<int:id>", methods=["GET", "POST"])
def edit_recipe(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        raw_material_ids = request.form.getlist("raw_material_id[]")
        quantities = request.form.getlist("quantity[]")

        # Delete existing recipe items
        query = load_sql_file("sql/delete_recipe_items.sql")
        cursor.execute(query, (id, ))

        # Insert updated recipe items
        query = load_sql_file("sql/add_recipe_item.sql")
        for raw_material_id, quantity in zip(raw_material_ids, quantities):
            cursor.execute(query, (id, raw_material_id, quantity))

        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("recipes"))

    # Fetch recipe details
    query = load_sql_file("sql/select_recipe.sql")
    cursor.execute(query, (id, ))
    recipe = cursor.fetchone()

    # Fetch recipe items
    query = load_sql_file("sql/list_recipe_items.sql")
    cursor.execute(query, (id, ))
    recipe_items = cursor.fetchall()

    # Fetch products and raw materials
    query = load_sql_file("sql/list_products.sql")
    cursor.execute(query)
    products = cursor.fetchall()

    query = load_sql_file("sql/list_raw_materials.sql")
    cursor.execute(query)
    raw_materials = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("edit_recipe.html",
                           recipe=recipe,
                           recipe_items=recipe_items,
                           products=products,
                           raw_materials=raw_materials)


@app.route("/recipes/delete/<int:id>", methods=["POST"])
def delete_recipe(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete the recipe and its items
    query = load_sql_file("sql/delete_recipe.sql")
    cursor.execute(query, (id, ))
    conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for("recipes"))


@app.route("/fetch_recipe", methods=["GET"])
def fetch_recipe():
    """
    Fetches the active recipe for the selected product, including required raw materials and inventory levels.
    """
    product_id = request.args.get("product_id")
    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400

    try:
        product_id = int(product_id)
    except ValueError:
        return jsonify({"error": "Invalid product_id format"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch only the active recipe for this product
    query = load_sql_file("sql/fetch_active_recipe.sql")
    cursor.execute(query, (product_id, ))
    rows = cursor.fetchall()

    # Extract column names from cursor description
    columns = [col[0] for col in cursor.description]

    # Convert rows to a list of dictionaries
    recipe_data = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return jsonify(recipe_data)


@app.route("/recipes/view/<int:recipe_id>")
def view_recipe(recipe_id):
    """ View details of a specific recipe version. """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = load_sql_file("sql/get_recipe_details.sql")
    cursor.execute(query, (recipe_id, ))
    recipe = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template("recipe_details.html", recipe=recipe)


@app.route("/recipes/activate/<int:id>", methods=["POST"])
def activate_recipe(id):
    """ Activate a recipe version (set all others to inactive). """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Deactivate all recipes for the product
    query = load_sql_file("sql/deactivate_recipes.sql")
    cursor.execute(query, (id, ))

    # Activate the selected recipe
    query = load_sql_file("sql/activate_recipe.sql")
    cursor.execute(query, (id, ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("recipes"))


@app.route("/recipes/deactivate/<int:id>", methods=["POST"])
def deactivate_recipe(id):
    """ Deactivate a recipe version. """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = load_sql_file("sql/deactivate_recipe.sql")
    cursor.execute(query, (id, ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for("recipes"))

@app.route("/recipes/fetch_versions", methods=["GET"])
def fetch_recipe_versions():
    recipe_version = request.args.get("recipe_version")

    conn = get_db_connection()
    cursor = conn.cursor()

    query = load_sql_file("sql/get_recipe_details.sql")
    cursor.execute(query, (recipe_version,))
    recipe_details = cursor.fetchall()

    cursor.close()
    conn.close()

    # Debugging log
    print(f"Recipe Details for version {recipe_version}: {recipe_details}")

    # Convert SQL result into JSON response
    response_data = [
        {
            "raw_material": row[0],  # Raw Material Name
            "quantity": row[1],  # Quantity
            "unit_of_measure": row[2],  # UoM Tag
            "vendor_name": row[3]  # Vendor Name
        } 
        for row in recipe_details
    ]

    print(f"JSON Response: {response_data}")  # Debugging Output
    return jsonify(response_data)


@app.route("/recipes/fetch_details", methods=["GET"])
def fetch_recipe_details():
    recipe_id = request.args.get("recipe_id")
    if not recipe_id:
        return jsonify({"error": "Missing recipe_id"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    query = load_sql_file("sql/fetch_recipe_details.sql")
    cursor.execute(query, (recipe_id, ))
    details = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify([{
        "raw_material_name": d[0],
        "quantity": d[1],
        "unit": d[2]
    } for d in details])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
