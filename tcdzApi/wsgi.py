from run import create_app
from config import ProductionConfig

# Create an app instance using the correct configuration
app = create_app(ProductionConfig)
