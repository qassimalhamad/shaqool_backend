from sqlalchemy import _or

from flask import Blueprint, request, jsonify

from config.database import SessionLocal , User

users = Blueprint('users_routes', __name__)
session = SessionLocal()