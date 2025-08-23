from flask import Flask, jsonify
from flask_smorest import Api
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv(override=True)

def create_app():
    app = Flask(__name__)

    # Flask Configuration
    app.config["API_TITLE"] = "WearCast API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"

    # CORS Configuration
    CORS(app,
         supports_credentials=True,
         resources={
             r"/*": {
                "origins": ['http://127.0.0.1:5500', "http://localhost:5000",
                             "http://127.0.0.1:5000"],
                 "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
                 "allow_headers": ["Content-Type", "Authorization"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": False,

             }
         })

    api = Api(app)

    # Server Health Check
    @app.route('/health')
    def health_check():
        return jsonify({'status': 'healthy'})

    # Register Blueprints
    from src.routes.chat import blp as chat_blp
    api.register_blueprint(chat_blp)

    from src.routes.auth import blp as auth_blp
    api.register_blueprint(auth_blp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5000, debug=True, host='0.0.0.0')
