import random
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from passlib.hash import pbkdf2_sha256   # pbkdf2_sh256 => hàm băm mật khẩu

from db import db
from blocklist import BLOCKLIST
from models import UserModel
from schemas import UserSchema, UserregisterSchema
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity

from tasks import send_simple_message_py, send_simple_message


blp = Blueprint("Users", __name__, description="Operations on user")




@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserregisterSchema)
    def post(self, user_data):
        if UserModel.query.filter(
            or_(
                UserModel.username == user_data["username"],
                UserModel.email == user_data["email"]
            )).first():
            abort(409, message="A user with that email or username already exists.")
        user = UserModel(
            username = user_data["username"],
            email = user_data["email"],
            password = pbkdf2_sha256.hash(user_data["password"])
        )
        try:
            db.session.add(user)
            db.session.commit()
            send_simple_message_py(
                to=user_data["email"],
                subject="OTP Flask API",
                body=f"Your OTP iS !98147")
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the user.")

        return {"message": " User Create Successfull"},201




@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter(
            UserModel.username == user_data['username'] 
            ).first()
        if user and pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)  # Tạo Token, xác nhận fresh = true để chạy refresh_token lại
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}
        abort(401, message="Invalid creadentials.")

#refresh
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()['jti']
        BLOCKLIST.add(jti)
        return {"access_token": new_token}


@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully Logged out."}
        
@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while Deleted the user.")
        return {"message":"User deleted."}, 200