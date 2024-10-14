from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema


blp = Blueprint("tags", __name__, description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @blp.response(200, TagSchema(many=True)) # Trả về
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()


    def put(self):
        pass

    @blp.arguments(TagSchema)  # xử lý và kiểm tra tính hợp lệ của dữ liệu yêu cầu.
    @blp.response(201, TagSchema)  # định nghĩa mã trạng thái và cấu trúc dữ liệu trả về.
    def post(self, tag_data, store_id):
        if(TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data["name"]).first()):
            abort(400, message="A tag with that name already exists in that store")

        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=f"Check you data input, try again, Please!\n {e}")
        return tag

@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsToItem(MethodView):
    
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return tag

    @blp.response(200, TagSchema)
    def delete(self, item_id, tag_id):
        # Chuaw kiem tra item và tag có trong table ko 
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag.")

        return {"message": "Item removed from tag"}
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):

    @blp.response(200, TagSchema)   # Tra ve
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.response(202, 
                    description="Deletes a tag if no item is tagged with it.", 
                    example={"messge": "tag deleted"})
    @blp.alt_response(404, description="Tag not found")
    @blp.alt_response(400, 
                        description="Retured if the tag is assigned to one or more items. In this case, the tag not deleted")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)

        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted"}
        abort(400, message="Could not delete tag. Make sure tag is not associated with any items. them try again!")


