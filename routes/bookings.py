from flask import Blueprint, request, jsonify
from config.database import Booking, Service, SessionLocal, BookingStatus
from sqlalchemy.orm import Session
import datetime

bookings_routes = Blueprint('bookings_routes', __name__)

# Create a new booking
@bookings_routes.route('/bookings', methods=['POST'])
def create_booking():
    session = SessionLocal()
    try:
        booking_data = request.get_json()
        service_id = booking_data.get('service_id')

        if not service_id:
            return jsonify({'error': 'Service ID is required.'}), 400

        service = session.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'error': 'Service not found.'}), 404

        user_id = request.user.get('id') 

        # Create the booking
        new_booking = Booking(
            service_id=service_id,
            user_id=user_id,
            status=BookingStatus.PENDING
        )
        session.add(new_booking)
        session.commit()
        session.refresh(new_booking)

        return jsonify({
            'id': new_booking.id,
            'service_id': new_booking.service_id,
            'user_id': new_booking.user_id,
            'status': new_booking.status.name,
            'created_at': new_booking.created_at.isoformat()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Update a booking 
@bookings_routes.route('/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    session = SessionLocal()
    try:
        booking_data = request.get_json()
        new_status = booking_data.get('status')

        if new_status not in BookingStatus.__members__:
            return jsonify({'error': 'Invalid booking status.'}), 400

        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return jsonify({'error': 'Booking not found.'}), 404

        booking.status = BookingStatus[new_status]
        session.commit()
        session.refresh(booking)

        return jsonify({
            'id': booking.id,
            'service_id': booking.service_id,
            'user_id': booking.user_id,
            'status': booking.status.name,
            'created_at': booking.created_at.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
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
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get all bookings
@bookings_routes.route('/bookings', methods=['GET'])
def get_all_bookings():
    session = SessionLocal()
    try:
        bookings = session.query(Booking).all()
        return jsonify([
            {
                'id': booking.id,
                'service_id': booking.service_id,
                'user_id': booking.user_id,
                'status': booking.status.name,
                'created_at': booking.created_at.isoformat()
            } for booking in bookings
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get bookings by user ID
@bookings_routes.route('/bookings/user/<int:user_id>', methods=['GET'])
def get_bookings_by_user(user_id):
    session = SessionLocal()
    try:
        bookings = session.query(Booking).filter(Booking.user_id == user_id).all()
        return jsonify([
            {
                'id': booking.id,
                'service_id': booking.service_id,
                'user_id': booking.user_id,
                'status': booking.status.name,
                'created_at': booking.created_at.isoformat()
            } for booking in bookings
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get bookings by service ID
@bookings_routes.route('/bookings/service/<int:service_id>', methods=['GET'])
def get_bookings_by_service(service_id):
    session = SessionLocal()
    try:
        bookings = session.query(Booking).filter(Booking.service_id == service_id).all()
        return jsonify([
            {
                'id': booking.id,
                'service_id': booking.service_id,
                'user_id': booking.user_id,
                'status': booking.status.name,
                'created_at': booking.created_at.isoformat()
            } for booking in bookings
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
