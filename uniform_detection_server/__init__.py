from flask import Flask
from flask_cors import CORS
from ultralytics import YOLO
import tempfile

from uniform_detection_server.routes import auth , predict

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py')
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    app.config.model = YOLO("models\\best.pt")
    app.config.tempfolder = tempfile.mkdtemp()
    
    CORS(app)
    


    app.register_blueprint(auth.bp)
    app.register_blueprint(predict.bp)

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app