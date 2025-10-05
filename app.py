from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
import enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///airline.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'a_very_secret_key_that_should_be_changed'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app) # Initialize Bcrypt for password hashing

# --- MODELS ---

# New User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class FlightStatus(enum.Enum):
    SCHEDULED = 'Scheduled'
    ON_TIME = 'On Time'
    DELAYED = 'Delayed'
    DEPARTED = 'Departed'
    ARRIVED = 'Arrived'

class Passenger(db.Model):
    pid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    contact = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)

class Flight(db.Model):
    flight_no = db.Column(db.String(10), primary_key=True)
    frm = db.Column(db.String(50), nullable=False)
    too = db.Column(db.String(50), nullable=False)
    dep_date = db.Column(db.String(20), nullable=True)
    dep_time = db.Column(db.String(20), nullable=True)
    arr_date = db.Column(db.String(20), nullable=True)
    arr_time = db.Column(db.String(20), nullable=True)
    status = db.Column(db.Enum(FlightStatus), nullable=False, default=FlightStatus.SCHEDULED)

class Shipment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contents = db.Column(db.String(200), nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    is_insured = db.Column(db.Boolean, default=False)
    flight_no = db.Column(db.String(10), db.ForeignKey('flight.flight_no'), nullable=False)
    cost_per_kg = db.Column(db.Float, nullable=False, default=5.0)
    handling_fee = db.Column(db.Float, nullable=False, default=10.0)

    @property
    def total_cost(self):
        return (self.weight_kg * self.cost_per_kg) + self.handling_fee

with app.app_context():
    db.create_all()

# --- AUTHENTICATION HELPER ---

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- AUTHENTICATION ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login failed. Please check your username and password.', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- MAIN APPLICATION ROUTES (PROTECTED) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/passengers')
@login_required
def passengers():
    search_query = request.args.get('search')
    if search_query:
        passengers_data = Passenger.query.filter(Passenger.name.ilike(f'%{search_query}%')).all()
    else:
        passengers_data = Passenger.query.order_by(Passenger.pid.desc()).all()
    return render_template('passengers.html', passengers=passengers_data, search_query=search_query)

@app.route('/add_passenger', methods=['POST'])
@login_required
def add_passenger():
    if request.method == 'POST':
        name, age, sex = request.form['name'], request.form['age'], request.form['sex']
        address, contact, email = request.form['address'], request.form['contact'], request.form['email']
        new_passenger = Passenger(name=name, age=age, sex=sex, address=address, contact=contact, email=email)
        db.session.add(new_passenger)
        db.session.commit()
        flash('Passenger added successfully!', 'success')
    return redirect(url_for('passengers'))

@app.route('/edit_passenger/<int:pid>', methods=['GET', 'POST'])
@login_required
def edit_passenger(pid):
    passenger = Passenger.query.get_or_404(pid)
    if request.method == 'POST':
        passenger.name, passenger.age, passenger.sex = request.form['name'], request.form['age'], request.form['sex']
        passenger.address, passenger.contact, passenger.email = request.form['address'], request.form['contact'], request.form['email']
        db.session.commit()
        flash('Passenger updated successfully!', 'success')
        return redirect(url_for('passengers'))
    return render_template('edit_passenger.html', passenger=passenger)

@app.route('/delete_passenger', methods=['POST'])
@login_required
def delete_passenger():
    passenger = Passenger.query.get(request.form['pid'])
    db.session.delete(passenger)
    db.session.commit()
    flash('Passenger deleted successfully!', 'info')
    return redirect(url_for('passengers'))

@app.route('/flights')
@login_required
def flights():
    flights_data = Flight.query.order_by(Flight.flight_no.desc()).all()
    return render_template('flights.html', flights=flights_data, flight_statuses=[s.value for s in FlightStatus])

@app.route('/add_flight', methods=['POST'])
@login_required
def add_flight():
    if request.method == 'POST':
        new_flight = Flight(
            flight_no=request.form['flight_no'],
            frm=request.form['from'],
            too=request.form['to'],
            dep_date=request.form['dep_date'],
            dep_time=request.form['dep_time'],
            arr_date=request.form['arr_date'],
            arr_time=request.form['arr_time'],
            status=FlightStatus(request.form['status'])
        )
        db.session.add(new_flight)
        db.session.commit()
        flash('Flight added successfully!', 'success')
    return redirect(url_for('flights'))

@app.route('/edit_flight/<string:flight_no>', methods=['GET', 'POST'])
@login_required
def edit_flight(flight_no):
    flight = Flight.query.get_or_404(flight_no)
    if request.method == 'POST':
        flight.frm, flight.too = request.form['from'], request.form['to']
        flight.dep_date, flight.dep_time = request.form['dep_date'], request.form['dep_time']
        flight.arr_date, flight.arr_time = request.form['arr_date'], request.form['arr_time']
        flight.status = FlightStatus(request.form['status'])
        db.session.commit()
        flash('Flight updated successfully!', 'success')
        return redirect(url_for('flights'))
    return render_template('edit_flight.html', flight=flight, flight_statuses=[s.value for s in FlightStatus])

@app.route('/delete_flight', methods=['POST'])
@login_required
def delete_flight():
    flight = Flight.query.get(request.form['flight_no'])
    db.session.delete(flight)
    db.session.commit()
    flash('Flight deleted successfully!', 'info')
    return redirect(url_for('flights'))

@app.route('/shipments')
@login_required
def shipments():
    flights_data = Flight.query.all()
    shipments_data = Shipment.query.order_by(Shipment.id.desc()).all()
    return render_template('shipments.html', shipments=shipments_data, flights=flights_data)

@app.route('/add_shipment', methods=['POST'])
@login_required
def add_shipment():
    if request.method == 'POST':
        new_shipment = Shipment(
            contents=request.form['contents'],
            weight_kg=float(request.form['weight_kg']),
            category=request.form['category'],
            is_insured='is_insured' in request.form,
            flight_no=request.form['flight_no'],
            cost_per_kg=float(request.form['cost_per_kg']),
            handling_fee=float(request.form['handling_fee'])
        )
        db.session.add(new_shipment)
        db.session.commit()
        flash('Shipment added successfully!', 'success')
    return redirect(url_for('shipments'))

@app.route('/edit_shipment/<int:sid>', methods=['GET', 'POST'])
@login_required
def edit_shipment(sid):
    shipment = Shipment.query.get_or_404(sid)
    if request.method == 'POST':
        shipment.contents, shipment.weight_kg = request.form['contents'], float(request.form['weight_kg'])
        shipment.category, shipment.is_insured = request.form['category'], 'is_insured' in request.form
        shipment.flight_no = request.form['flight_no']
        shipment.cost_per_kg, shipment.handling_fee = float(request.form['cost_per_kg']), float(request.form['handling_fee'])
        db.session.commit()
        flash('Shipment updated successfully!', 'success')
        return redirect(url_for('shipments'))
    flights = Flight.query.all()
    return render_template('edit_shipment.html', shipment=shipment, flights=flights)

@app.route('/delete_shipment', methods=['POST'])
@login_required
def delete_shipment():
    shipment = Shipment.query.get(request.form['id'])
    db.session.delete(shipment)
    db.session.commit()
    flash('Shipment deleted successfully!', 'info')
    return redirect(url_for('shipments'))

if __name__ == "__main__":
    app.run(port=8000, debug=True)

