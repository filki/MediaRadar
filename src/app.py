from flask import Flask
from dotenv import load_dotenv
import os
import routes  # This is the correct way to import

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Register routes
    app.register_blueprint(routes.bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)