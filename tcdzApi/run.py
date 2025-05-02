from flask import Flask, redirect, render_template, url_for
from app import api_bp
import os
from model import db #, redis_cache
from config import DevelopmentConfig, TestingConfig, BaseConfig, PresentConfig, ProductionConfig
from flask_cors import CORS


# app = Flask(__name__)
# CORS(app, resources={r"/*": {"origins": "*"}})

def create_app(config_filename):

    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})

    print("calling correct create_app")
    app.config.from_object(config_filename)
    print("printing existing blueprints: ",app.blueprints)
    app.register_blueprint(api_bp, url_prefix='/cric/ml/services')
    db.init_app(app)

    @app.route('/')
    @app.route('/cric/ml/services/')
    def homepage():
        return render_template('index.html')

    return app


# ONLY FOR PRODUCTION, COMMENT IN DEV ENV
# app = create_app(ProductionConfig)


# In local development, use DevelopmentConfig
if __name__ == "__main__":
    app = create_app(DevelopmentConfig)
    port = int(os.environ.get("PORT", 9000))
    app.run(debug=True, port=port)
