from flask import Blueprint, request, jsonify
from config.database import Service , ServiceEnum , CategoryEnum , Category, SessionLocal

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
        provider_id = request.user.get('id')

        if name not in [service.value for service in ServiceEnum]:
            return jsonify({'error': 'Invalid service name.'}), 400
        
        if not all([name, price, description]):
            return jsonify({'error': 'Incomplete data. All fields are required.'}), 400
        
        existing_service = session.query(Service).filter(Service.name == name, Service.provider_id == provider_id).first()
        if existing_service:
            return jsonify({'error': 'Service already exists.'}), 400
        
        category_name = None
        if name in ['plumbing', 'electrician', 'handyman']:
            category_name = CategoryEnum.home_repairs.value
        elif name == 'cleaning':
            category_name = CategoryEnum.cleaning.value
        elif name in ['gardening', 'welding']:
            category_name = CategoryEnum.gardening.value
        else:
            return jsonify({'error': 'No category found for this service.'}), 400
        
        category = session.query(Category).filter(Category.name == category_name).first()
        if not category:
            return jsonify({'error': 'Category not found.'}), 400

        new_service = Service(
            name=name,
            description=description,
            price=price,
            provider_id=provider_id,
            category_id=category.id
        )

        session.add(new_service)
        session.commit()
        session.refresh(new_service)

        return jsonify({
            'id': new_service.id,
            'name': new_service.name,
            'description': new_service.description,
            'price': new_service.price,
            'provider_id': new_service.provider_id,
            'category_id': new_service.category_id
        }), 201
    
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Update a service
@services_routes.route('/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    session = SessionLocal()
    try:
        service_data = request.get_json()
        name = service_data.get('name')
        description = service_data.get('description')
        price = service_data.get('price')
        provider_id = request.user.get('id')

        if not all([name, price, description]):
            return jsonify({'error': 'Incomplete data. All fields are required.'}), 400

        existing_service = session.query(Service).filter(Service.id == service_id).first()

        if not existing_service:
            return jsonify({'error': 'Service not found.'}), 404

        if existing_service.provider_id != provider_id:
            return jsonify({'error': 'You do not have permission to update this service.'}), 403

        duplicate_service = session.query(Service).filter(
            Service.name == name,
            Service.provider_id == provider_id
        ).first()

        if duplicate_service and duplicate_service.id != service_id:
            return jsonify({'error': 'Service already exists.'}), 400

        existing_service.name = name
        existing_service.description = description
        existing_service.price = price
        
        category_name = None
        if name in ['plumbing', 'electrician', 'handyman']:
            category_name = CategoryEnum.home_repairs.value
        elif name == 'cleaning':
            category_name = CategoryEnum.cleaning.value
        elif name in ['gardening', 'welding']:
            category_name = CategoryEnum.gardening.value
        else:
            return jsonify({'error': 'No category found for this service.'}), 400

        category = session.query(Category).filter(Category.name == category_name).first()
        if not category:
            return jsonify({'error': 'Category not found.'}), 400

        existing_service.category_id = category.id

        session.commit()
        session.refresh(existing_service)

        return jsonify({
            'id': existing_service.id,
            'name': existing_service.name,
            'description': existing_service.description,
            'price': existing_service.price,
            'provider_id': existing_service.provider_id,
            'category_id': existing_service.category_id
        }), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Delete a service
@services_routes.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    session = SessionLocal()
    try:
        service = session.query(Service).filter(Service.id == service_id).first()

        if not service:
            return jsonify({'error': 'Service not found.'}), 404

        provider_id = request.user.get('id')
        if service.provider_id != provider_id:
            return jsonify({'error': 'You do not have permission to delete this service.'}), 403

        session.delete(service)
        session.commit()

        return jsonify({'message': 'Service deleted successfully.'}), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get all services
@services_routes.route('/services', methods=['GET'])
def get_all_services():
    session = SessionLocal()
    try:
        services = session.query(Service).all()
        
        services_list = [{
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'price': service.price,
            'provider_id': service.provider_id,
            'category_id': service.category_id
        } for service in services]

        return jsonify(services_list), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get a service by ID
@services_routes.route('/services/<int:service_id>', methods=['GET'])
def get_service_by_id(service_id):
    session = SessionLocal()
    try:
        service = session.query(Service).filter(Service.id == service_id).first()

        if not service:
            return jsonify({'error': 'Service not found.'}), 404

        service_data = {
            'id': service.id,
            'name': service.name,
            'description': service.description,
            'price': service.price,
            'provider_id': service.provider_id,
            'category_id': service.category_id
        }

        return jsonify(service_data), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()
