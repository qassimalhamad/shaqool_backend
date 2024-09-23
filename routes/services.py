from flask import Blueprint, request, jsonify
from config.database import Service, ServiceEnum, CategoryEnum, Category, User, SessionLocal

services_routes = Blueprint('services_routes', __name__)

# Create multiple services
@services_routes.route('/services', methods=['POST'])
def create_services():
    session = SessionLocal()
    try:
        services_data = request.get_json()  # Expecting a list of services
        provider_id = request.user.get('id')

        if not isinstance(services_data, list):
            return jsonify({'error': 'Invalid input. Expected a list of services.'}), 400

        created_services = []
        for service_data in services_data:
            service_type = service_data.get('service_type')
            description = service_data.get('description')
            price = service_data.get('price')

            if service_type not in [service.value for service in ServiceEnum]:
                return jsonify({'error': f'Invalid service type: {service_type}.'}), 400

            if not all([service_type, price, description]):
                return jsonify({'error': 'Incomplete data. All fields are required for each service.'}), 400
            
            existing_service = session.query(Service).filter(Service.service_type == ServiceEnum[service_type], Service.provider_id == provider_id).first()
            if existing_service:
                return jsonify({'error': f'Service already exists for this provider: {service_type}.'}), 400
            
            # Determine category based on service type
            if service_type in [ServiceEnum.plumbing.value, ServiceEnum.electrician.value, ServiceEnum.handyman.value]:
                category_name = CategoryEnum.home_repairs.value
            elif service_type == ServiceEnum.cleaning.value:
                category_name = CategoryEnum.cleaning.value
            elif service_type in [ServiceEnum.gardening.value, ServiceEnum.welding.value]:
                category_name = CategoryEnum.gardening.value
            else:
                return jsonify({'error': 'No category found for this service.'}), 400
            
            category = session.query(Category).filter(Category.name == category_name).first()
            if not category:
                return jsonify({'error': 'Category not found.'}), 400

            new_service = Service(
                service_type=ServiceEnum[service_type],
                description=description,
                price=price,
                provider_id=provider_id,
                category_id=category.id
            )

            session.add(new_service)
            created_services.append(new_service)

        session.commit()
        for service in created_services:
            session.refresh(service)

        return jsonify([{
            'id': service.id,
            'service_type': service.service_type.value,
            'description': service.description,
            'price': service.price,
            'provider_id': service.provider_id,
            'category_id': service.category_id
        } for service in created_services]), 201

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
        service_type = service_data.get('service_type')  # Changed from 'name' to 'service_type'
        description = service_data.get('description')
        price = service_data.get('price')
        provider_id = request.user.get('id')

        if not all([service_type, price, description]):
            return jsonify({'error': 'Incomplete data. All fields are required.'}), 400

        existing_service = session.query(Service).filter(Service.id == service_id).first()

        if not existing_service:
            return jsonify({'error': 'Service not found.'}), 404

        if existing_service.provider_id != provider_id:
            return jsonify({'error': 'You do not have permission to update this service.'}), 403

        duplicate_service = session.query(Service).filter(
            Service.service_type == ServiceEnum[service_type], 
            Service.provider_id == provider_id
        ).first()

        if duplicate_service and duplicate_service.id != service_id:
            return jsonify({'error': 'Service already exists for this provider.'}), 400

        existing_service.service_type = ServiceEnum[service_type]  
        existing_service.description = description
        existing_service.price = price
        
        # Determine category based on service type
        if service_type in [ServiceEnum.plumbing.value, ServiceEnum.electrician.value, ServiceEnum.handyman.value]:
            category_name = CategoryEnum.home_repairs.value
        elif service_type == ServiceEnum.cleaning.value:
            category_name = CategoryEnum.cleaning.value
        elif service_type in [ServiceEnum.gardening.value, ServiceEnum.welding.value]:
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
            'service_type': existing_service.service_type.value,  
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
            'service_type': service.service_type.value,  
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

# Get service by service type
@services_routes.route('/services/<string:service_type>', methods=['GET'])
def get_service_by_type(service_type):
    session = SessionLocal()
    try:
        if service_type not in [service.value for service in ServiceEnum]:
            return jsonify({'error': 'Invalid service type.'}), 400

        service = session.query(Service).filter(Service.service_type == ServiceEnum[service_type]).first()

        if not service:
            return jsonify({'error': 'Service not found.'}), 404

        return jsonify({
            'id': service.id,
            'service_type': service.service_type.value,  
            'description': service.description,
            'price': service.price,
            'provider_id': service.provider_id,
            'category_id': service.category_id
        }), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get providers by service type
@services_routes.route('/services/<string:service_type>/providers', methods=['GET'])
def get_providers_for_service(service_type):
    session = SessionLocal()
    try:
        if service_type not in [service.value for service in ServiceEnum]:
            return jsonify({'error': 'Invalid service type.'}), 400

        services = session.query(Service).filter(Service.service_type == ServiceEnum[service_type]).all()
        if not services:
            return jsonify({'error': 'No services found for this type.'}), 404

        provider_ids = [service.provider_id for service in services]
        providers = session.query(User).filter(User.id.in_(provider_ids)).all()
        
        providers_list = [{
            'id': provider.id,
            'name': provider.username,  
            'contact': provider.phone, 
        } for provider in providers]

        return jsonify(providers_list), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()
