from flask import Flask, render_template, jsonify, redirect, request, session, flash
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = "caircocoders-ednalan"

# Database configuration
DB_HOST = "localhost"
DB_NAME = "sampledb0"
DB_USER = "postgres"
DB_PASS = "51654372985"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


@app.route('/')
def index():
    # Check if the user is logged in
    if 'username' in session:
        username = session['username']
        role = session['role']
        return render_template('index.html', username=username, role=role)
    else:
        return render_template('index.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if 'username' in session:
        username = session['username']
        role = session['role']
        return render_template('contact.html', username=username, role=role)
    else:
        return render_template('contact.html')
    
    if request.method == 'POST':
        return send_message()
    else:
        return render_template('contact.html')


@app.route('/cars')
def cars():
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM carbrands ORDER BY brand_id")
    carbrands = cur.fetchall()
    if 'username' in session:
        username = session['username']
        role = session['role']
        return render_template('cars.html', username=username, role=role)
    else:
        return render_template('cars.html', carbrands=carbrands)



@app.route('/car-details')
def car_details():
    return render_template('car-details.html')


@app.route('/about-us')
def about_us():
     if 'username' in session:
        username = session['username']
        role = session['role']
        return render_template('about-us.html', username=username, role=role)
     else:
        return render_template('about-us.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the username and password are valid
        if username and password:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cur.fetchone()
            cur.close()

            if user:
                # Store the user's information in the session
                session['username'] = user['username']
                session['role'] = user['role']
                flash('Logged in successfully!', 'success')
                return redirect('/')
            else:
                flash('Invalid username or password', 'error')
                return redirect('/login')
        else:
            flash('Please enter both username and password', 'error')
            return redirect('/login')
    else:
        return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Check if the username and password are provided and if the passwords match
        if username and password and password == confirm_password:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Check if the username is already taken
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cur.fetchone()

            if existing_user:
                flash('Username already exists', 'error')
                return redirect('/register')
            else:
                # Create a new user
                cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                            (username, password, 'user'))
                conn.commit()
                flash('Registered successfully! Please login.', 'success')
                return redirect('/login')
        else:
            flash('Please enter a valid username and password, and make sure the passwords match', 'error')
            return redirect('/register')
    else:
        return render_template('register.html')

@app.route("/carbrand", methods=["POST"])
def car_brand():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    brand_id = request.form.get('brand_id')

    if brand_id:
        cur.execute("SELECT * FROM carmodels WHERE brand_id = %s ORDER BY car_model ASC", [brand_id])
        cars = cur.fetchall()
        car_characteristics = []

        for car in cars:
            car_characteristics.append({
                'model_id': car['model_id'],
                'car_model': car['car_model'],
            })

        return jsonify(car_characteristics)

    return jsonify([])


@app.route("/carcharacteristics", methods=["POST"])
def car_characteristics():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    brand_id = request.form.get('brand_id')
    model_id = request.form.get('model_id')

    if brand_id and model_id:
        cur.execute("SELECT * FROM carmodels WHERE brand_id = %s AND model_id = %s", [brand_id, model_id])
        car = cur.fetchone()

        if car:
            car_characteristics = {
                'car_photo': car['car_photo'],
                'brand_name': car['brand_name'],
                'model_id': car['model_id'],
                'car_model': car['car_model'],
                'body_type': car['body_type'],
                'number_doors': car['number_doors'],
                'price_range': car['price_range'],
                'year': car['year'],
                'mileage': car['mileage'],
                'transmission': car['transmission'],
                'fuel_type': car['fuel_type'],
                'color': car['color'],
                'technical_condition': car['technical_condition'],
                'customs_cleared': car['customs_cleared'],
                'driven_from': car['driven_from'],
                'engine_size': car['engine_size'],
                'engine_name': car['engine_name'],
                'engine_hp': car['engine_hp'],
                'location': car['location'],
                'seller_id': car['seller_id']
            }

            return jsonify(car_characteristics)

    return jsonify({})


@app.route("/filter", methods=["POST"])
def filter_cars():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    brand_id = request.form.get('brand_id')
    model_id = request.form.get('model_id')
    transmission = request.form.get('transmission')
    body_type = request.form.get('body_type')
    number_doors = request.form.get('number_doors')
    min_price = request.form.get('min_price')
    max_price = request.form.get('max_price')
    min_year = request.form.get('min_year')
    max_year = request.form.get('max_year')
    min_mileage = request.form.get('min_mileage')  
    max_mileage = request.form.get('max_mileage')
    engine_size = request.form.get('engine_size') 
    engine_name = request.form.get('engine_name') 
    engine_hp = request.form.get('engine_hp')   
    location = request.form.get('location')

    query = "SELECT * FROM carmodels WHERE 1=1"
    params = []

    if brand_id:
        query += " AND brand_id = %s"
        params.append(brand_id)
    if model_id:
        query += " AND model_id = %s"
        params.append(model_id)
    if transmission:
        query += " AND transmission = %s"
        params.append(transmission)
    if body_type:
        query += " AND body_type = %s" 
        params.append(body_type)
    if number_doors:
        query += " AND number_doors = %s" 
        params.append(number_doors)
    if min_price:
        query += " AND price_range >= %s"
        params.append(min_price)
    if max_price:
        query += " AND price_range <= %s"
        params.append(max_price)
    if min_year:
        query += " AND year >= %s"
        params.append(min_year)
    if max_year:
        query += " AND year <= %s"
        params.append(max_year)
    if min_mileage:
        query += " AND mileage >= %s"
        params.append(min_mileage)
    if max_mileage:
        query += " AND mileage <= %s"
        params.append(max_mileage)
    if engine_size:
        query += " AND engine_size = %s"
        params.append(engine_size)
    if engine_name:
        query += " AND engine_name = %s"
        params.append(engine_name)
    if engine_hp:
        query += " AND engine_hp = %s"
        params.append(engine_hp)
    if location:
        query += " AND location = %s"
        params.append(location)  

    query += " ORDER BY car_model ASC"
    cur.execute(query, params)
    cars = cur.fetchall()

    filtered_cars = []
    for car in cars:
        filtered_cars.append({
            'car_photo': car['car_photo'],
            'model_id': car['model_id'],
            'car_model': car['car_model'],
            'body_type': car['body_type'],
            'number_doors': car['number_doors'],
            'price_range': car['price_range'],
            'year': car['year'],
            'mileage': car['mileage'],
            'transmission': car['transmission'],
            'fuel_type': car['fuel_type'],
            'color': car['color'],
            'technical_condition': car['technical_condition'],
            'customs_cleared': car['customs_cleared'],
            'driven_from': car['driven_from'],
            'engine_size': car['engine_size'],
            'engine_name': car['engine_name'],
            'engine_hp': car['engine_hp'],
            'location': car['location'],
            'seller_id': car['seller_id']
        })

    return jsonify(filtered_cars)


@app.route("/addcar", methods=["POST"])
def add_car():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    brand_id = request.form.get('brand_id')
    car_model = request.form.get('car_model')
    body_type = request.form.get('body_type')
    number_doors = request.form.get('number_doors')
    price_range = request.form.get('price_range')
    year = request.form.get('year')
    mileage = request.form.get('mileage')
    transmission = request.form.get('transmission')
    fuel_type = request.form.get('fuel_type')
    color = request.form.get('color')
    technical_condition = request.form.get('technical_condition')
    customs_cleared = request.form.get('customs_cleared')
    driven_from = request.form.get('driven_from')
    engine_size = request.form.get('engine_size')
    engine_name = request.form.get('engine_name')
    engine_hp = request.form.get('engine_hp')
    location = request.form.get('location')
    seller_id = request.form.get('seller_id')

    query = "INSERT INTO carmodels (brand_id, car_model, body_type, number_doors, price_range, year, mileage, transmission, fuel_type, color, technical_condition, customs_cleared, driven_from, engine_size, engine_name, engine_hp, location, seller_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    cur.execute(query, (brand_id, car_model, body_type, number_doors, price_range, year, mileage, transmission, fuel_type, color, technical_condition, customs_cleared, driven_from, engine_size, engine_name, engine_hp, location, seller_id))
    conn.commit()
    
    return redirect('/cars')

@app.route("/deletecar", methods=["POST"])
def delete_car():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    model_id = request.form.get('model_id')
    
    query = "DELETE FROM carmodels WHERE model_id = %s"
    
    cur.execute(query, [model_id])
    conn.commit()
    
    return redirect('/cars')

@app.route('/sellers', methods=['GET'])
def get_seller_info():
    model_id = request.args.get('model_id')
    
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    query = "SELECT s.seller_name, s.seller_email, s.seller_phone, s.seller_location FROM sellers s INNER JOIN carmodels c ON s.seller_id = c.seller_id WHERE c.model_id = %s"
    
    try:
        cur.execute(query, (model_id,))
        seller_info = cur.fetchone()

        if seller_info:
            response = {
                'seller_name': seller_info['seller_name'],
                'seller_email': seller_info['seller_email'],
                'seller_phone': seller_info['seller_phone'],
                'seller_location': seller_info['seller_location']
            }
        else:
            response = {
                'seller_name': 'Seller not found',
                'seller_email': 'N/A',
                'seller_phone': 'N/A',
                'seller_location': 'N/A'
            }

        cur.close()
        conn.commit()

        return jsonify(response)
    except Exception as e:
        cur.close()
        conn.rollback()
        return str(e), 500
    
@app.route('/send-message', methods=['POST'])
def send_message():
    if 'message_sent' in session:
        flash('You have already sent a message!', 'warning')
        return redirect('/contact')

    name = request.form.get('name')
    subject = request.form.get('subject')
    message = request.form.get('message')

    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("INSERT INTO messages (name, subject, message) VALUES (%s, %s, %s)",
                (name, subject, message))
    conn.commit()
    cur.close()

    session['message_sent'] = True
    flash('Message sent successfully!', 'success')
    return redirect('/contact')



@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect('/')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
