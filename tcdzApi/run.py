from flask import Flask, redirect, render_template
from app import api_bp
from model import db #, redis_cache
from config import DevelopmentConfig, TestingConfig, BaseConfig, PresentConfig
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

t = 0
def create_app(config_filename):
    app.config.from_object(config_filename)
    global t
    if t == 0:
        app.register_blueprint(api_bp, url_prefix='/cric/ml/services')
        t = 1
    if config_filename != TestingConfig:
        db.init_app(app)
        #redis_cache.init_app(app)
    return app

@app.route('/')
@app.route('/cric/ml/services/')
def availableApps():

    return render_template('availableApp.html')


if __name__ == "__main__":
    PresentConfig = BaseConfig
    app = create_app(PresentConfig)
    app.run(debug=True,port=9000)
