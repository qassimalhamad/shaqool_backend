import os 
from flask import Blueprint, request, jsonify
from config.database import SessionLocal, ServiceCategoryModel  # Ensure you import the correct model

categories_routes = Blueprint('categories_routes', __name__)

# Get all categories
@categories_routes.route('/categories', methods=['GET'])
def get_categories():
    session = SessionLocal()
    try:
        categories = session.query(ServiceCategoryModel).all()  # Use ServiceCategoryModel here
        return jsonify([
            {
                'id': category.id,
                'name': category.name,
            } for category in categories
        ]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get a category by name
@categories_routes.route('/categories/<string:category_name>', methods=['GET'])
def get_category(category_name):
    session = SessionLocal()
    try:
        category = session.query(ServiceCategoryModel).filter(ServiceCategoryModel.name == category_name).first()
        if category:
            return jsonify({
                'id': category.id,
                'name': category.name,
            }), 200
        return jsonify({'error': 'Category not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

# Get a category by id
@categories_routes.route('/categories/<int:category_id>', methods=['GET'])
def get_category_by_id(category_id):
    session = SessionLocal()
    try:
        category = session.query(ServiceCategoryModel).filter(ServiceCategoryModel.id == category_id).first()
        if category:
            return jsonify({
                'id': category.id,
                'name': category.name,
            }), 200
        return jsonify({'error': 'Category not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()