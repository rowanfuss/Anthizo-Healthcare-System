from flask import Flask, request, jsonify

app = Flask(__name__)

# Sample Data (Temporary storage)
appointments = []

@app.route('/appointments', methods=['POST'])
def book_appointment():
    """Book a new appointment"""
    data = request.get_json()
    
    # Basic Validation: Ensure necessary fields are provided
    if 'patient_name' not in data or 'doctor_name' not in data or 'date' not in data or 'time' not in data:
        return jsonify({"error": "Missing required fields"}), 400

    # Check for duplicate appointment
    for appt in appointments:
        if appt["date"] == data["date"] and appt["time"] == data["time"] and appt["doctor_name"] == data["doctor_name"]:
            return jsonify({"error": "Doctor already has an appointment at this time"}), 400

    appointments.append(data)
    return jsonify({"message": "Appointment booked successfully", "appointment": data}), 201

@app.route('/appointments', methods=['GET'])
def get_appointments():
    """Retrieve all booked appointments"""
    return jsonify(appointments), 200

@app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
def cancel_appointment(appointment_id):
    """Cancel an appointment by ID"""
    if 0 <= appointment_id < len(appointments):
        deleted_appointment = appointments.pop(appointment_id)
        return jsonify({"message": "Appointment canceled", "appointment": deleted_appointment}), 200
    return jsonify({"error": "Invalid appointment ID"}), 404

if __name__ == '__main__':
    app.run(debug=True)
