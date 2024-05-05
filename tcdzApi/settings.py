# Flask settings
FLASK_SERVER_NAME = 'localhost:9000'
FLASK_DEBUG = True  # Do not use debug mode in production

# Flask-Restplus settings
RESTPLUS_SWAGGER_UI_DOC_EXPANSION = 'list'
RESTPLUS_VALIDATE = True
RESTPLUS_MASK_SWAGGER = False
RESTPLUS_ERROR_404_HELP = False

# SQLAlchemy settings
# SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False


## MINE
SQLALCHEMY_DATABASE_URI = 'cockroachdb://rohith:1GzkPwMOIO4z9j9d4Zwn3g@plains-emu-5603.g8z.gcp-us-east1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full';
    
