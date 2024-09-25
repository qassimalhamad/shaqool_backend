from flask import Blueprint, request, jsonify
from config.database import Service, SessionLocal, CategoryEnum, ServiceEnum, Category, ProviderService, User

services_routes = Blueprint('services_routes', __name__)

# Get all services
@services_routes.route('/services', methods=['GET'])
def get_services():
    session = SessionLocal()
    try:
        services = session.query(Service).all()
        services_list = []
        for service in services:
            services_list.append({
                'id': service.id,
                'name': service.name.value,
                'description': service.description,
                'category_id': service.category_id
            })
        return jsonify(services_list), 200
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get all services in a category
@services_routes.route('/categories/<string:category_name>/services', methods=['GET'])
def get_services_by_category(category_name):
    session = SessionLocal()
    try:
        category = session.query(Category).filter(Category.name == CategoryEnum[category_name]).first()
        if not category:
            return jsonify({'error': 'Category not found'}), 404

        services = session.query(Service).filter(Service.category_id == category.id).all()
        services_list = []
        for service in services:
            services_list.append({
                'id': service.id,
                'name': service.name.value,
                'description': service.description
            })
        return jsonify(services_list), 200
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get a service by name
@services_routes.route('/services/<string:service_name>', methods=['GET'])
def get_service_by_name(service_name):
    session = SessionLocal()
    try:
        service = session.query(Service).filter(Service.name == ServiceEnum[service_name]).first()
        if service:
            return jsonify({
                'id': service.id,
                'name': service.name.value,
                'description': service.description,
                'category_id': service.category_id
            }), 200
        return jsonify({'error': 'Service not found'}), 404
    
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get providers by service
@services_routes.route('/services/<string:service_name>/providers', methods=['GET'])
def get_providers_by_service(service_name):
    session = SessionLocal()
    try:
        service = session.query(Service).filter(Service.name == ServiceEnum[service_name]).first()
        if not service:
            return jsonify({'error': 'Service not found'}), 404

        providers = session.query(ProviderService).filter(ProviderService.service_id == service.id).all()
        providers_list = []
        for provider in providers:
            providers_list.append({
                'provider_id': provider.provider_id,
                'service_id': provider.service_id,
                'price': provider.price,
                'description': provider.description,
                'username': session.query(User).filter(User.id == provider.provider_id).first().username
            })
        return jsonify(providers_list), 200
    
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()
