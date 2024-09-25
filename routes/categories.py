from flask import Blueprint, request, jsonify
from config.database import Category, CategoryEnum, SessionLocal

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
                'name': category.name.value,
                'description': category.description
            })
        return jsonify(categories_list), 200
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()

# Get a single category by name
@categories_routes.route('/categories/<string:category_name>', methods=['GET'])
def get_category(category_name):
    session = SessionLocal()
    try:
        category = session.query(Category).filter(Category.name == CategoryEnum[category_name]).first()
        if category:
            return jsonify({
                'id': category.id,
                'name': category.name.value,
                'description': category.description
            }), 200
        return jsonify({'error': 'Category not found'}), 404
    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500
    finally:
        session.close()
