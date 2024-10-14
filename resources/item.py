from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError

from db import db
from models import ItemModel
from schemas import ItemSchema, ItemUpdateSchema




blp = Blueprint("items", __name__, description="Operations on items")


@blp.route("/item/<int:item_id>")
class Item(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)  
    def get(self, item_id):
        return ItemModel.query.get_or_404(item_id)

    @jwt_required(fresh=True)
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        items_delete = ItemModel.query.get_or_404(item_id) 
        try:
            db.session.delete(items_delete)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(404, message=f"Check your items input: {e}")
        
        return {"message": "Items has deleted"}, 200


    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self,item_data, item_id):
        items = ItemModel.query.get_or_404(item_id)
        try:
            if items:
                items.name = item_data["name"]
                items.price = item_data["price"]
            else:
                items = ItemModel(id=item_id, **item_data)
        except SQLAlchemyError:
            abort(500, message=f"Check you input infomations")
        
        db.session.add(items)
        db.session.commit()

        return items

@blp.route("/item")
class ItemList(MethodView):
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        items = ItemModel(**item_data)
        try:
            db.session.add(items)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item")
        return items