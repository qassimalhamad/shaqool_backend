from flask import Blueprint, request, jsonify
from config.database import Service , ServiceEnum , SessionLocal

services_routes = Blueprint('services_routes', __name__)

# Create a service
@services_routes.route('/services', methods=['POST'])
def create_service():
    session = SessionLocal()
    try:
        service_data = request.get_json()
        name = service_data.get('name')
        description = service_data.get('description')
        price = service_data.get('price')

        if name not in [service.value for service in ServiceEnum]:
            return jsonify({'error': 'Invalid service name.'}), 400

        if not all([name, description, price]):
            return jsonify({'error': 'Incomplete data. All fields are required.'}), 400

        new_service = Service(
            name=name,
            description=description,
            price=price
        )

        session.add(new_service)
        session.commit()
        session.refresh(new_service)

        return jsonify({
            'id': new_service.id,
            'name': new_service.name,
            'description': new_service.description,
            'price': new_service.price
        }), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Update a service
@services_routes.route('/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    session = SessionLocal()
    try:
        service = session.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'error': 'Service not found'}), 404

        service_data = request.get_json()
        name = service_data.get('name')
        description = service_data.get('description')
        price = service_data.get('price')

        if name and name not in [service.value for service in ServiceEnum]:
            return jsonify({'error': 'Invalid service name.'}), 400

        if not all([name, description, price]):
            return jsonify({'error': 'Incomplete data. All fields are required.'}), 400

        if name:
            service.name = name
        service.description = description
        service.price = price

        session.commit()
        session.refresh(service)
        return jsonify({
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'price': service.price
        }), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Delete a service
@services_routes.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    session = SessionLocal()
    try:
        service = session.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'error': 'Service not found'}), 404

        session.delete(service)
        session.commit()
        return jsonify({'message': 'Service deleted successfully'}), 200
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()