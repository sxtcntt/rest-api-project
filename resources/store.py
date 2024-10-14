from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models import StoreModel

from schemas import StoreSchema

from db import db

blp = Blueprint("stores", __name__, description="Operations on Store")


@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        return StoreModel.query.get_or_404(store_id)

    @jwt_required(fresh=True)
    def delete(self, store_id):
        store_delete = StoreModel.query.get_or_404(store_id) 
        try:
            db.session.delete(store_delete)
            db.session.commit()
            return {"message": "Store has deleted"}, 200
        except SQLAlchemyError as e:
            abort(404, message=f"Error: {e}")

@blp.route("/store")
class StoreList(MethodView):
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        try:
            return StoreModel.query.all()
        except SQLAlchemyError as e:
            abort(404, message=f"Error: {e}")

    @jwt_required(fresh=True)
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(400, message="A Store that name already exists ")
        except SQLAlchemyError as e:
            abort(500, message="An error occurred create the stores")
        return store
