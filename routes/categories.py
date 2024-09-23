from flask import Blueprint, request, jsonify
from config.database import Service, ServiceEnum, CategoryEnum, Category, SessionLocal

categories_routes = Blueprint('categories_routes', __name__)

# Get all categories
@categories_routes.route('/categories', methods=['GET'])
def get_categories():
    session = SessionLocal()
    try:
        categories = session.query(Category).all()
        categories_list = []
        for category in categories:
            categories_list.append({
                'id': category.id,
                'name': category.name.value if isinstance(category.name, CategoryEnum) else str(category.name)
            })
        return jsonify(categories_list), 200
    
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    
    finally:
        session.close()

# Get category by name
@categories_routes.route('/categories/<string:category_name>', methods=['GET'])
def get_category_by_name(category_name):
    session = SessionLocal()
    try:
        category = session.query(Category).filter(Category.name == category_name).first()
        if not category:
            return jsonify({'error': 'Category not found.'}), 404
        
        category_data = {
            'id': category.id,
            'name': category.name.value if isinstance(category.name, CategoryEnum) else str(category.name)
        }
        return jsonify(category_data), 200
    
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    
    finally:
        session.close()

# Get services by category
@categories_routes.route('/categories/<string:category_name>/services', methods=['GET'])
def get_services_by_category_name(category_name):
    session = SessionLocal()
    try:
        category = session.query(Category).filter(Category.name == category_name).first()
        if not category:
            return jsonify({'error': 'Category not found.'}), 404
        
        services = session.query(Service).filter(Service.category_id == category.id).all()
        services_list = []
        
        for service in services:
            services_list.append({
                'id': service.id,
                'service_type': service.service_type.value if isinstance(service.service_type, ServiceEnum) else str(service.service_type),
            })
        
        return jsonify(services_list), 200

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    
    finally:
        session.close()
