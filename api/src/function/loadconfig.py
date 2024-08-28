from concurrent.futures import ThreadPoolExecutor
from dotenv import dotenv_values
import os

# load config
config = dotenv_values("config/.env")

UPLOAD_FOLDER = os.path.join('files', 'UploadFile')

isDev = config['DEV'].lower() == "true"

executor = ThreadPoolExecutor(max_workers=1)