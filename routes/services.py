from flask import Blueprint, request, jsonify
from config.database import Service, SessionLocal, ServiceCategoryModel
from sqlalchemy.orm import Session

services_routes = Blueprint('services_routes', __name__)

# Create a new service
@services_routes.route('/services', methods=['POST'])
def create_service():
    session = SessionLocal()
    try:
        new_service_data = request.get_json()
        title = new_service_data.get('title')
        description = new_service_data.get('description')
        category_id = new_service_data.get('category_id')

        if not all([title, category_id]):
            return jsonify({'error': 'Incomplete data. Title and category_id are required.'}), 400

        owner_id = request.user.get('id')  

        category = session.query(ServiceCategoryModel).filter(ServiceCategoryModel.id == category_id).first()
        if not category:
            return jsonify({'error': 'Category not found.'}), 404

        if not owner_id:  
            return jsonify({'error': 'Owner not found.'}), 404

        new_service = Service(
            title=title,
            description=description,
            category_id=category_id,
            owner_id=owner_id  
        )

        session.add(new_service)
        session.commit()
        session.refresh(new_service)

        return jsonify({
            'id': new_service.id,
            'title': new_service.title,
            'description': new_service.description,
            'category_id': new_service.category_id,
            'owner_id': new_service.owner_id,
            'created_at': new_service.created_at.isoformat()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Update a service
@services_routes.route('/services/<int:service_id>', methods=['PUT'])
def update_service(service_id):
    session = SessionLocal()
    try:
        current_user_id = request.user.get('id')
        updated_service_data = request.get_json()
        title = updated_service_data.get('title')
        description = updated_service_data.get('description')
        category_id = updated_service_data.get('category_id')

        service = session.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'error': 'Service not found.'}), 404

        if service.owner_id != current_user_id:
            return jsonify({'error': 'You are not authorized to update this service.'}), 403

        if category_id:
            category = session.query(ServiceCategoryModel).filter(ServiceCategoryModel.id == category_id).first()
            if not category:
                return jsonify({'error': 'Category not found.'}), 404

        if title is not None:
            service.title = title
        if description is not None:
            service.description = description
        if category_id is not None:
            service.category_id = category_id

        session.commit()
        session.refresh(service)

        return jsonify({
            'id': service.id,
            'title': service.title,
            'description': service.description,
            'category_id': service.category_id,
            'owner_id': service.owner_id,
            'created_at': service.created_at.isoformat()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Delete a service
@services_routes.route('/services/<int:service_id>', methods=['DELETE'])
def delete_service(service_id):
    session = SessionLocal()
    try:
        current_user_id = request.user.get('id')

        service = session.query(Service).filter(Service.id == service_id).first()
        if not service:
            return jsonify({'error': 'Service not found.'}), 404

        if service.owner_id != current_user_id:
            return jsonify({'error': 'You are not authorized to delete this service.'}), 403

        session.delete(service)
        session.commit()

        return jsonify({'message': 'Service deleted successfully.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get all services
@services_routes.route('/services', methods=['GET'])
def get_services():
    session = SessionLocal()
    try:
        services = session.query(Service).all()
        return jsonify([
            {
                'id': service.id,
                'title': service.title,
                'description': service.description,
                'category_id': service.category_id,
                'owner_id': service.owner_id,
                'created_at': service.created_at.isoformat()
            } for service in services
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get a service by id
@services_routes.route('/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    session = SessionLocal()
    try:
        service = session.query(Service).filter(Service.id == service_id).first()
        if service:
            return jsonify({
                'id': service.id,
                'title': service.title,
                'description': service.description,
                'category_id': service.category_id,
                'owner_id': service.owner_id,
                'created_at': service.created_at.isoformat()
            }), 200
        return jsonify({'error': 'Service not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get services by category
@services_routes.route('/services/category/<string:category_name>', methods=['GET'])
def get_services_by_category(category_name):
    session = SessionLocal()
    try:
        category = session.query(ServiceCategoryModel).filter(ServiceCategoryModel.name == category_name).first()
        if not category:
            return jsonify({'error': 'Category not found.'}), 404

        services = session.query(Service).filter(Service.category_id == category.id).all()
        return jsonify([
            {
                'id': service.id,
                'title': service.title,
                'description': service.description,
                'category_id': service.category_id,
                'owner_id': service.owner_id,
                'created_at': service.created_at.isoformat()
            } for service in services
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@services_routes.route('/services/owner/<int:owner_id>', methods=['GET'])
def get_services_by_owner(owner_id):
    session = SessionLocal()
    try:
        services = session.query(Service).filter(Service.owner_id == owner_id).all()
        return jsonify([
            {
                'id': service.id,
                'title': service.title,
                'description': service.description,
                'category_id': service.category_id,
                'owner_id': service.owner_id,
                'created_at': service.created_at.isoformat()
            } for service in services
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()
