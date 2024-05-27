import unittest
import psycopg2
import psycopg2.extras
from flask import Flask
from flask_testing import TestCase
from app import app, get_db_connection

class BaseTestCase(TestCase):
    def create_app(self):
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test_secret_key'
        app.config['DB_HOST'] = 'localhost'
        app.config['DB_NAME'] = 'test_sampledb0'
        app.config['DB_USER'] = 'postgres'
        app.config['DB_PASS'] = '51654372985'
        return app

    def setUp(self):
        self.conn = get_db_connection()
        self.create_tables()
        self.populate_tables()

    def tearDown(self):
        self.drop_tables()
        self.conn.close()

    def create_tables(self):
        cur = self.conn.cursor()
        cur.execute('''
        CREATE TABLE users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(50) NOT NULL,
            role VARCHAR(50) NOT NULL
        );
        CREATE TABLE carbrands (
            brand_id SERIAL PRIMARY KEY,
            brand_name VARCHAR(50) NOT NULL
        );
        CREATE TABLE carmodels (
            model_id SERIAL PRIMARY KEY,
            brand_id INT REFERENCES carbrands(brand_id),
            car_model VARCHAR(50),
            body_type VARCHAR(50),
            number_doors INT,
            price_range INT,
            year INT,
            mileage INT,
            transmission VARCHAR(50),
            fuel_type VARCHAR(50),
            color VARCHAR(50),
            technical_condition VARCHAR(50),
            customs_cleared BOOLEAN,
            driven_from VARCHAR(50),
            engine_size FLOAT,
            engine_name VARCHAR(50),
            engine_hp INT,
            location VARCHAR(50),
            seller_id INT
        );
        ''')
        self.conn.commit()
        cur.close()

    def drop_tables(self):
        cur = self.conn.cursor()
        cur.execute('''
        DROP TABLE IF EXISTS carmodels;
        DROP TABLE IF EXISTS carbrands;
        DROP TABLE IF EXISTS users;
        ''')
        self.conn.commit()
        cur.close()

    def populate_tables(self):
        cur = self.conn.cursor()
        cur.execute('''
        INSERT INTO users (username, password, role) VALUES
        ('testuser', 'password', 'user'),
        ('admin', 'adminpassword', 'admin');
        
        INSERT INTO carbrands (brand_name) VALUES
        ('Toyota'),
        ('Ford');

        INSERT INTO carmodels (brand_id, car_model, body_type, number_doors, price_range, year, mileage, transmission, fuel_type, color, technical_condition, customs_cleared, driven_from, engine_size, engine_name, engine_hp, location, seller_id) VALUES
        (1, 'Camry', 'Sedan', 4, 30000, 2020, 10000, 'Automatic', 'Gasoline', 'White', 'Good', True, 'USA', 2.5, 'V6', 301, 'New York', 1);
        ''')
        self.conn.commit()
        cur.close()

class FlaskTestCase(BaseTestCase):

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_login(self):
        response = self.client.post('/login', data=dict(username='testuser', password='password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully!', response.data)

    def test_invalid_login(self):
        response = self.client.post('/login', data=dict(username='invaliduser', password='invalidpassword'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid username or password', response.data)

    def test_register(self):
        response = self.client.post('/register', data=dict(username='newuser', password='newpassword', confirm_password='newpassword'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registered successfully! Please login.', response.data)

    def test_register_existing_user(self):
        response = self.client.post('/register', data=dict(username='testuser', password='newpassword', confirm_password='newpassword'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username already exists', response.data)

    def test_cars(self):
        response = self.client.get('/cars')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Toyota', response.data)
        self.assertIn(b'Ford', response.data)

    def test_logout(self):
        self.client.post('/login', data=dict(username='testuser', password='password'), follow_redirects=True)
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged out successfully!', response.data)

if __name__ == '__main__':
    unittest.main()
