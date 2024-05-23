from flask import Flask, redirect, render_template, url_for
from app import api_bp
from model import db #, redis_cache
from config import DevelopmentConfig, TestingConfig, BaseConfig, PresentConfig, ProductionConfig
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def create_app(config_filename):
    print("calling correct create_app")
    app.config.from_object(config_filename)
    app.register_blueprint(api_bp, url_prefix='/cric/ml/services')
    db.init_app(app)
    return app


# ONLY FOR PRODUCTION, COMMENT IN DEV ENV
app = create_app(ProductionConfig)


@app.route('/')
@app.route('/ui')
def homepage():
    return render_template('index.html')

@app.route('/dashboard/home/')
def dashboardHome():
    return render_template('dashboardHome.html')

@app.route('/dashboard/')
def dashboard():
    return redirect(url_for('dashboardHome'))

@app.route('/dashboard/players/')
def dashboardPlayers():
    return render_template('players.html')

@app.route('/dashboard/matches/')
def dashboardMatches():
    return render_template('matches.html')


if __name__ == "__main__":
    PresentConfig = DevelopmentConfig
    app = create_app(PresentConfig)
    app.run(debug=True,port=9000)
