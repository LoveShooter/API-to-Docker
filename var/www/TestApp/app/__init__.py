from flask import Flask

UPLOAD_DIRECTORY = "/var/www/upload"

app = Flask(__name__)

app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY

from app import prog