from db import db


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    items = db.relationship("ItemModel", back_populates="stores", lazy="dynamic")
    tags = db.relationship("TagModel", back_populates="stores", lazy="dynamic")


    # lazy = dunamic sẽ sự dụng một dòng lênh cho tim kiếm thấy vỳ 1 dòng cho items và 1 dòng cho tab.
    # dữ liệu càng nhiều thì lazy=dynamic sẽ càng năng => ko nên sự dụng cho mô hình thực sự vì sẽ làm hiểu suất của chương trình

