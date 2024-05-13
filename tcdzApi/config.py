
class BaseConfig:
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = 'cockroachdb://rohith:1GzkPwMOIO4z9j9d4Zwn3g@plains-emu-5603.g8z.gcp-us-east1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full';
    #REDIS_HOST = "localhost"
    #REDIS_PASSWORD = "61a62a841f54d08ec165faf2ad20544e9f6fb8d37d10bf429b6e9f6e2807e0c4"
    #REDIS_PORT = 6379

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'cockroachdb://rohith:1GzkPwMOIO4z9j9d4Zwn3g@plains-emu-5603.g8z.gcp-us-east1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full';

class TestingConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'cockroachdb://rohith:1GzkPwMOIO4z9j9d4Zwn3g@plains-emu-5603.g8z.gcp-us-east1.cockroachlabs.cloud:26257/defaultdb?sslmode=verify-full';

class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = 'cockroachdb://rohith:1GzkPwMOIO4z9j9d4Zwn3g@plains-emu-5603.g8z.gcp-us-east1.cockroachlabs.cloud:26257/defaultdb?sslmode=require&sslrootcert=util/root.crt';


PresentConfig = BaseConfig
