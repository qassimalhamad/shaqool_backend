import os
from flask import Flask

# Imports from routes and middleware
from routes.auth import auth_routes
from routes.users import users_routes
from middleware.verifyToken import verify_token

# Initialize the Flask app
app = Flask(__name__)

# Register the global middleware
app.before_request(verify_token)

# Register the blueprints
app.register_blueprint(auth_routes)
app.register_blueprint(users_routes)


# run the server
if __name__ == '__main__':
    app.run()

