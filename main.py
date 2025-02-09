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
    conn = get_db_connection()
    cursor = conn.cursor()

    # Load the SQL query from a file
    query = load_sql_file("sql/list_tags.sql")
    cursor.execute(query)
    tags = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify([{"name": tag[0]} for tag in tags])


@app.route("/recipes", methods=["GET"])
def recipes():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch recipes with associated product names
    query = load_sql_file("sql/list_recipes.sql")
    cursor.execute(query)
    recipes = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template("recipes.html", recipes=recipes)


@app.route("/recipes/add", methods=["GET", "POST"])
def add_recipe():
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        # Capture form data
        product_id = request.form.get("product_id")
        raw_materials = request.form.getlist("raw_material_id[]")
        quantities = request.form.getlist("quantity[]")

        # Debug: Print form data to verify
        print(f"Product ID: {product_id}")
        print(f"Raw Materials: {raw_materials}")
        print(f"Quantities: {quantities}")

        if not product_id or not raw_materials or not quantities:
            print("Error: Missing product_id, raw materials, or quantities")
            return "Error: Missing product_id, raw materials, or quantities", 400

        try:
            # Insert the recipe and get the new recipe ID
            query = load_sql_file("sql/add_recipe.sql")
            cursor.execute(query, (product_id, ))
            recipe_id = cursor.fetchone()[0]

            # Debug: Check if the recipe ID was generated
            print(f"New Recipe ID: {recipe_id}")

            # Insert raw materials into recipe_raw_materials
            query = load_sql_file("sql/add_recipe_raw_material.sql")
            for raw_material_id, quantity in zip(raw_materials, quantities):
                print(
                    f"Adding raw material {raw_material_id} with quantity {quantity} to recipe {recipe_id}"
                )
                cursor.execute(query, (recipe_id, raw_material_id, quantity))

            # Commit the transaction
            conn.commit()
            print("Recipe successfully added!")
        except Exception as e:
            conn.rollback()
            print(f"Database Error: {str(e)}")
            return f"Error: {str(e)}", 500
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for("recipes"))

    # GET: Display the recipe form
    query = load_sql_file("sql/list_products.sql")
    cursor.execute(query)
    products = cursor.fetchall()

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
    # Retrieve and validate the product_id parameter.
    product_id = request.args.get("product_id")
    if not product_id:
        return jsonify({"error": "Missing product_id"}), 400

    try:
        product_id = int(product_id)
    except ValueError:
        return jsonify({"error": "Invalid product_id format"}), 400

    try:
        # Open a database connection and load the SQL query.
        conn = get_db_connection()
        cursor = conn.cursor()
        query = load_sql_file("sql/fetch_recipe.sql")

        # Execute the query with the product_id parameter.
        cursor.execute(query, (product_id,))
        rows = cursor.fetchall()

        # Retrieve column names from the cursor description.
        columns = [col[0] for col in cursor.description]

        # Convert the rows into a list of dictionaries.
        recipe_data = [dict(zip(columns, row)) for row in rows]

        cursor.close()
        conn.close()
    except Exception as e:
        app.logger.error("Error fetching recipe for product %s: %s", product_id, str(e), exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": str(e)}), 500

    return jsonify(recipe_data)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
