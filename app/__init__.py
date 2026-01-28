from flask import Flask
from app.extensions import mongo


def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    # Initialize extensions
    mongo.init_app(app)
    
    # Register blueprints
    from app.webhook import webhook_bp
    app.register_blueprint(webhook_bp)
    
    # Root route for dashboard
    from flask import render_template
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    return app
