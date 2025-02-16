import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from dotenv import load_dotenv
from database import db  # ✅ Import the single database instance

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)

# Set Database Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Initialize Extensions (NO duplicate instances!)
db.init_app(app)  # Bind SQLAlchemy to Flask app
migrate = Migrate(app, db)  # Setup Flask-Migrate

# ✅ Print DATABASE_URL for Debugging
print("Using DATABASE_URL:", os.getenv("DATABASE_URL"))

# Define Appointment Model
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Unique ID
    patient_name = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    time = db.Column(db.String(20), nullable=False)

# ✅ No need to manually call `db.create_all()`, Flask-Migrate handles this

# Route: Book Appointment
@app.route('/appointments', methods=['POST'])
def book_appointment():
    """Book a new appointment"""
    data = request.get_json()

    # Validate required fields
    if not all(k in data for k in ['patient_name', 'doctor_name', 'date', 'time']):
        return jsonify({"error": "Missing required fields"}), 400

    # Check if doctor already has an appointment at the given time
    existing_appt = Appointment.query.filter_by(
        doctor_name=data['doctor_name'], date=data['date'], time=data['time']
    ).first()
    if existing_appt:
        return jsonify({"error": "Doctor already has an appointment at this time"}), 400

    # Create new appointment
    new_appt = Appointment(**data)

    db.session.add(new_appt)
    db.session.commit()

    return jsonify({
        "message": "Appointment booked successfully",
        "appointment": {
            "id": new_appt.id,
            "patient_name": new_appt.patient_name,
            "doctor_name": new_appt.doctor_name,
            "date": new_appt.date,
            "time": new_appt.time
        }
    }), 201

# Route: Get All Appointments
@app.route('/appointments', methods=['GET'])
def get_appointments():
    """Retrieve all booked appointments"""
    appointments = Appointment.query.all()
    return jsonify([
        {
            "id": appt.id,
            "patient_name": appt.patient_name,
            "doctor_name": appt.doctor_name,
            "date": appt.date,
            "time": appt.time
        }
        for appt in appointments
    ]), 200

# Route: Cancel Appointment
@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    """Cancel an appointment by ID"""
    appointment = Appointment.query.get(appointment_id)

    if not appointment:
        return jsonify({"error": "Invalid appointment ID"}), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({
        "message": "Appointment canceled",
        "appointment": {
            "id": appointment.id,
            "patient_name": appointment.patient_name,
            "doctor_name": appointment.doctor_name,
            "date": appointment.date,
            "time": appointment.time
        }
    }), 200

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
