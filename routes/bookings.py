from flask import Blueprint, request, jsonify
from config.database import Booking, User, Service, BookingEnum ,SessionLocal
from sqlalchemy.orm import sessionmaker
from datetime import datetime

bookings_routes = Blueprint('booking_routes', __name__)

# Create a booking
@bookings_routes.route('/bookings', methods=['POST'])
def create_booking():
    session = SessionLocal()
    try:
        booking_data = request.get_json()
        user_id = request.user.get('id')
        service_id = booking_data.get('service_id')
        booking_time = booking_data.get('booking_time')

        if not service_id or not booking_time:
            return jsonify({'error': 'Service ID and booking time are required.'}), 400

        service = session.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'error': 'Service not found.'}), 404

        new_booking = Booking(
            user_id=user_id,
            service_id=service_id,
            booking_time=datetime.fromisoformat(booking_time),
            status=BookingEnum.pending.value
        )

        session.add(new_booking)
        session.commit()
        session.refresh(new_booking)

        return jsonify({
            'id': new_booking.id,
            'user_id': new_booking.user_id,
            'service_id': new_booking.service_id,
            'booking_time': new_booking.booking_time.isoformat(),
            'status': new_booking.status
        }), 201

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get all bookings for a user
@bookings_routes.route('/bookings', methods=['GET'])
def get_user_bookings():
    session = SessionLocal()
    try:
        user_id = request.user.get('id')
        bookings = session.query(Booking).filter(Booking.user_id == user_id).all()

        bookings_list = [{
            'id': booking.id,
            'service_id': booking.service_id,
            'booking_time': booking.booking_time.isoformat(),
            'status': booking.status
        } for booking in bookings]

        return jsonify(bookings_list), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Update a booking
@bookings_routes.route('/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    session = SessionLocal()
    try:
        booking_data = request.get_json()
        booking_time = booking_data.get('booking_time')
        status = booking_data.get('status')

        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return jsonify({'error': 'Booking not found.'}), 404

        if booking_time:
            booking.booking_time = datetime.fromisoformat(booking_time)

        if status and status in [status.value for status in BookingEnum]:
            booking.status = status

        session.commit()
        session.refresh(booking)

        return jsonify({
            'id': booking.id,
            'service_id': booking.service_id,
            'booking_time': booking.booking_time.isoformat(),
            'status': booking.status
        }), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Delete a booking
@bookings_routes.route('/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    session = SessionLocal()
    try:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return jsonify({'error': 'Booking not found.'}), 404

        session.delete(booking)
        session.commit()

        return jsonify({'message': 'Booking deleted successfully.'}), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()
