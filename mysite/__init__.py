from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from routes import init_routes

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRETKEY")
app.config['SQLALCHEMY_POOL_RECYCLE'] = 270

sqldb = SQLAlchemy()
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_size' : 100, 'pool_recycle' : 280}
sqldb.init_app(app)

init_routes(app)