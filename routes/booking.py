from flask import Blueprint, request, jsonify
from sqlalchemy.orm import joinedload
from config.database import Booking, SessionLocal, BookingStatusEnum, Service

booking_routes = Blueprint('booking_routes', __name__)

def create_response(success, message, status_code):
    return jsonify({'success': success, 'message': message}), status_code

# Create a booking
@booking_routes.route('/bookings', methods=['POST'])
def create_booking():
    session = SessionLocal()
    data = request.json
    service_name = data.get('service_name')
    customer_id = request.user.get('id')

    if not service_name:
        return create_response(False, 'Service name is required', 400)

    try:
        service = session.query(Service).filter(Service.name == service_name).first()

        if not service:
            return create_response(False, 'Service not found', 404)

        new_booking = Booking(
            service_id=service.id,
            customer_id=customer_id,
            status=BookingStatusEnum.pending
        )

        session.add(new_booking)
        session.commit()

        return jsonify({'message': 'Booking created successfully', 'booking_id': new_booking.id}), 201
    except Exception as e:
        return create_response(False, f"An error occurred: {str(e)}", 500)
    finally:
        session.close()

# Get all bookings for a customer
@booking_routes.route('/customers/<int:customer_id>/bookings', methods=['GET'])
def get_customer_bookings(customer_id):
    session = SessionLocal()
    try:
        bookings = session.query(Booking).options(joinedload(Booking.service)).filter(Booking.customer_id == customer_id).all()
        bookings_list = [{'id': booking.id, 'service_id': booking.service_id, 'status': booking.status.name} for booking in bookings]
        return jsonify(bookings_list), 200
    except Exception as e:
        return create_response(False, f"An error occurred: {str(e)}", 500)
    finally:
        session.close()

# Get all bookings for a provider
@booking_routes.route('/providers/<int:provider_id>/bookings', methods=['GET'])
def get_provider_bookings(provider_id):
    session = SessionLocal()
    try:
        bookings = session.query(Booking).filter(Booking.provider_id == provider_id).all()
        bookings_list = [{'id': booking.id, 'service_id': booking.service_id, 'status': booking.status.name} for booking in bookings]
        return jsonify(bookings_list), 200
    except Exception as e:
        return create_response(False, f"An error occurred: {str(e)}", 500)
    finally:
        session.close()

# Accept a booking
@booking_routes.route('/bookings/<int:booking_id>/accept', methods=['PUT'])
def accept_booking(booking_id):
    session = SessionLocal()
    provider_id = request.user.get('id')

    try:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return create_response(False, 'Booking not found', 404)

        booking.provider_id = provider_id
        booking.status = BookingStatusEnum.confirmed
        session.commit()
        return create_response(True, 'Booking accepted successfully', 200)
    except Exception as e:
        return create_response(False, f"An error occurred: {str(e)}", 500)
    finally:
        session.close()

# Cancel a booking
@booking_routes.route('/bookings/<int:booking_id>/cancel', methods=['PUT'])
def cancel_booking(booking_id):
    session = SessionLocal()
    try:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return create_response(False, 'Booking not found', 404)

        booking.status = BookingStatusEnum.cancelled
        session.commit()
        return create_response(True, 'Booking cancelled successfully', 200)
    except Exception as e:
        return create_response(False, f"An error occurred: {str(e)}", 500)
    finally:
        session.close()

# Get a booking
@booking_routes.route('/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    session = SessionLocal()
    try:
        booking = session.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            return create_response(False, 'Booking not found', 404)

        return jsonify({
            'id': booking.id,
            'service_id': booking.service_id,
            'customer_id': booking.customer_id,
            'status': booking.status.name
        }), 200
    except Exception as e:
        return create_response(False, f"An error occurred: {str(e)}", 500)
    finally:
        session.close()
