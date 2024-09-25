from flask import Blueprint, request, jsonify
from config.database import Service, SessionLocal, CategoryEnum , ServiceEnum , Category , ProviderService , User

service_provider_routes = Blueprint('service_provider_routes', __name__)

# POST a Provider Service
@service_provider_routes.route('/providers/services', methods=['POST'])
def add_provider_service():
    session = SessionLocal()
    provider_id = request.user.get('id')  
    data = request.json
    service_name = data.get('service_name')
    price = data.get('price')
    description = data.get('description')

    try:
        service = session.query(Service).filter(Service.name == ServiceEnum[service_name]).first()
        if not service:
            return jsonify({'error': 'Service not found'}), 404

        provider_service = ProviderService(
            provider_id=provider_id,
            service_id=service.id,
            price=price,
            description=description
        )
        session.add(provider_service)
        session.commit()
        return jsonify({'message': 'Service added successfully'}), 201
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get all provider services for a specific provider
@service_provider_routes.route('/providers/<int:provider_id>/services', methods=['GET'])
def get_provider_services(provider_id):
    session = SessionLocal()
    try:
        provider_services = session.query(ProviderService).filter(ProviderService.provider_id == provider_id).all()
        services_list = [{
            'id': ps.id,
            'service_name': ps.service.name.value,
            'price': ps.price,
            'description': ps.description
        } for ps in provider_services]
        return jsonify(services_list), 200
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get a specific provider service by ID
@service_provider_routes.route('/providers/services/<int:service_id>', methods=['GET'])
def get_provider_service(service_id):
    session = SessionLocal()
    try:
        provider_service = session.query(ProviderService).filter(ProviderService.id == service_id).first()
        if provider_service:
            return jsonify({
                'id': provider_service.id,
                'service_name': provider_service.service.name.value,
                'price': provider_service.price,
                'description': provider_service.description
            }), 200
        return jsonify({'error': 'Service not found'}), 404
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

@service_provider_routes.route('/providers/services/<int:service_id>', methods=['PUT'])
def update_provider_service(service_id):
    session = SessionLocal()
    data = request.json

    try:
        provider_service = session.query(ProviderService).filter(ProviderService.id == service_id).first()
        if not provider_service:
            return jsonify({'error': 'Service not found'}), 404

        service_name = data.get('service_name')
        if service_name:
            service = session.query(Service).filter(Service.name == ServiceEnum[service_name]).first()
            if not service:
                return jsonify({'error': 'Service not found'}), 404
            provider_service.service_id = service.id

        provider_service.price = data.get('price', provider_service.price)
        provider_service.description = data.get('description', provider_service.description)

        session.commit()
        return jsonify({'message': 'Service updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

@service_provider_routes.route('/providers/services/<int:service_id>', methods=['DELETE'])
def delete_provider_service(service_id):
    session = SessionLocal()
    try:
        provider_service = session.query(ProviderService).filter(ProviderService.id == service_id).first()
        if not provider_service:
            return jsonify({'error': 'Service not found'}), 404

        session.delete(provider_service)
        session.commit()
        return jsonify({'message': 'Service deleted successfully'}), 204
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()