import os
from flask import Flask, jsonify
from flask_smorest import Api
from flask_migrate import Migrate
from dotenv import load_dotenv

from db import db
from blocklist import BLOCKLIST
import models

from resources.store import blp as StoreBlueprint
from resources.item import blp as ItemBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint
from flask_jwt_extended import JWTManager
def create_app(db_url=None):
    app= Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")  # Link database
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Vô hiệu hóa 1 cái gì đó .... Trong SQLAlchemy
    db.init_app(app)  # Cấp quyền kết nối db Flask và SQLAlchemy

    migrate = Migrate(app, db)

    api = Api(app)
    # JWT
    app.config["JWT_SECRET_KEY"] = "4585307749053280932928903605462913905"
    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token has been revoked.",
                    "error":"token_revoked"
                }
            ), 401
        )

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description":"The token is not fresh",
                    "error": "fresh_token_required",
                }
            )
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # Look in the database and see whether the user is an admin
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}
 

    @jwt.expired_token_loader   # Khi Token hết thời gian sự dụng
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify({
                "message": "The token has expired",
                "error": "token_expired"
            }), 401,
        )

    @jwt.invalid_token_loader  # Khi Token không đúng
    def invalid_token_callback(error):
        return (
            jsonify(
                {
                    "message": "Signature verification failed.", "error": "invalid_token"
                },
                401,
            )
        )

    @jwt.unauthorized_loader    # Khi Token không có ( chưa login)
    def unauthorized_loader(error):
        return (
            jsonify(
                {
                    "description": "Request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401
        )

    # @app.before_first_request  #3.0.3 resapi ko còn hàm này
    # def create_table():
    #     db.create_all()

    with app.app_context():  # chỉ chạy 1 lần 
        db.create_all()
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    app.register_blueprint(TagBlueprint)
    app.register_blueprint(UserBlueprint)

    return app


