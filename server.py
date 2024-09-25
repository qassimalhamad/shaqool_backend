from flask import Flask
from flask_cors import CORS

# Imports from routes and middleware
from routes.auth import auth_routes
from routes.users import users_routes
from routes.categories import categories_routes
from routes.services import services_routes
from routes.provider_service import service_provider_routes
from routes.booking import booking_routes
from middleware.verifyToken import verify_token

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Register the global middleware
app.before_request(verify_token)

# Register the blueprints
app.register_blueprint(auth_routes)
app.register_blueprint(users_routes)
app.register_blueprint(categories_routes)
app.register_blueprint(services_routes)
app.register_blueprint(service_provider_routes)
app.register_blueprint(booking_routes)

# run the server
if __name__ == '__main__':
    app.run()

