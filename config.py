import os


IS_PROD = os.getenv('IS_PROD') is not None

PORT = int(os.getenv('PORT', '8080'))

