from flask import Flask, render_template
from flask_cors import CORS

import os

from src.config import Config
from src.api import api
from src.extensions import db, api, migrate, jwt, scheduler
from src.views import auth_blueprint
from src.commands import init_db, populate_db, insert_db

from src.models import User

from src.logging_config import get_logger

logger = get_logger('app')

BLUEPRINTS = [auth_blueprint]
COMMANDS = [init_db, populate_db, insert_db]

def create_app(config=Config):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config)

    logger.info(f"Creating app with config: {config.__name__}")

    @app.route('/')
    def index():
        return render_template('index.html')
    
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    register_error_handlers(app)
    register_scheduler(app)

    return app

def register_extensions(app):

    # Flask-SQLAlchemy
    db.init_app(app)

    # Flask-Migrate
    migrate.init_app(app, db)

    # Flask-restX
    api.init_app(app)

    # Flask-JWT-Extended
    jwt.init_app(app)

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        try:
            return user.uuid
        except AttributeError:
            return user
        
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        user_uuid = jwt_data.get("sub")
        # print(f"JWT Data: {jwt_data}")
        if user_uuid:
            user = User.query.filter_by(uuid=user_uuid).first()
            return user
        return None
    
    
def register_blueprints(app):
    for blueprint in BLUEPRINTS:
        app.register_blueprint(blueprint)
    
def register_commands(app):
    for command in COMMANDS:
        app.cli.add_command(command)

def register_scheduler(app):
    """
    Start APScheduler only in the Werkzeug reloader child process
    (or when not in debug mode) to prevent the scheduler running twice.
    """
    from tools.outsidescript import add_transaction_to_db

    is_reloader_child = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'

    if is_reloader_child or not app.debug:
        logger.info("Starting APScheduler...")

        scheduler.add_job(
            func=add_transaction_to_db,
            args=[app],           # passes the app instance to the job
            trigger='interval',
            minutes=1,
            id='add_transaction_job',
            replace_existing=True,
            max_instances=1       # prevents overlap if job takes >1 min
        )

        scheduler.start()
        logger.info("APScheduler started. Job 'add_transaction_job' registered (every 1 min)")
    else:
        logger.info("Skipping scheduler start (Werkzeug parent process)")

# Custom error handler for 404
def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        # You can return a JSON response or render a custom HTML template
        return render_template('404.html'), 404