from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

# Configure PostgreSQL Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://anthizo_healthcare_db_user:SHZhEPNBiZNiyEqylgnQVj8YlCMWpFRg@dpg-cuoi150gph6c73dn8lsg-a/anthizo_healthcare_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define Appointment Model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID
    patient_name = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)

# Create Database Tables
with app.app_context():
    db.create_all()

# Route: Book Appointment
@app.route('/appointments', methods=['POST'])
def book_appointment():
    """Book a new appointment"""
    data = request.get_json()

    # Validate required fields
    if not all(k in data for k in ['patient_name', 'doctor_name', 'date', 'time']):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if doctor already has an appointment at the given time
    existing_appt = Appointment.query.filter_by(doctor_name=data['doctor_name'], date=data['date'], time=data['time']).first()
    if existing_appt:
        return jsonify({"error": "Doctor already has an appointment at this time"}), 400

    # Create new appointment
    new_appt = Appointment(
        patient_name=data['patient_name'],
        doctor_name=data['doctor_name'],
        date=data['date'],
        time=data['time']
    )

    db.session.add(new_appt)
    db.session.commit()

    return jsonify({"message": "Appointment booked successfully", "appointment": {
        "id": new_appt.id,
        "patient_name": new_appt.patient_name,
        "doctor_name": new_appt.doctor_name,
        "date": new_appt.date,
        "time": new_appt.time
    }}), 201

# Route: Get All Appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():
    """Retrieve all booked appointments"""
    appointments = Appointment.query.all()
    return jsonify([{
        "id": appt.id,
        "patient_name": appt.patient_name,
        "doctor_name": appt.doctor_name,
        "date": appt.date,
        "time": appt.time
    } for appt in appointments]), 200

# Route: Cancel Appointment
@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    """Cancel an appointment by ID"""
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({"error": "Invalid appointment ID"}), 404

    db.session.delete(appointment)
    db.session.commit()
    
    return jsonify({"message": "Appointment canceled", "appointment": {
        "id": appointment.id,
        "patient_name": appointment.patient_name,
        "doctor_name": appointment.doctor_name,
        "date": appointment.date,
        "time": appointment.time
    }}), 200

if __name__ == '__main__':
    app.run(debug=True)
