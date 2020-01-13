from flask_restful import Resource
from flask import request
from models.item import ItemModel
from schemas.item import ItemSchema
from flask_jwt_extended import (
    jwt_required,
    jwt_optional,
    get_jwt_claims,
    fresh_jwt_required,
    get_jwt_identity)

ITEM_NOT_FOUND = 'An item with name {} does not exist'
ITEM_ALREADY_EXISTS = 'An item with name {} already exists'
ERROR_INSERTING = 'An error occured while saving an item'
MUST_BE_ADMIN = 'Admin privillages required'
ITEM_DELETED = 'Item deleted'
MUST_LOGIN = 'More data available if you login'


item_schema = ItemSchema()
item_list_schema = ItemSchema(many=True)


class Item(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item_schema.dump(item), 200
        return {'message': ITEM_NOT_FOUND.format(name)}, 404

    @classmethod
    @fresh_jwt_required
    def post(cls, name: str):
        if ItemModel.find_by_name(name):
            return {'message': ITEM_ALREADY_EXISTS.format(name)}, 400

        item_json = request.get_json()
        item_json['name'] = name

        item = item_schema.load(item_json)

        try:
            item.save_to_db()
        except Exception as e:
            return {'message': ERROR_INSERTING}, 500

        return item_schema.dump(item), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        # Check if user is admin
        claims = get_jwt_claims()

        if not claims['is_admin']:
            return {'message': MUST_BE_ADMIN}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': ITEM_DELETED}
        return {'message': ITEM_NOT_FOUND.format(name)}

    @classmethod
    @jwt_required
    def put(cls, name: str):
        item_json = request.get_json()
        item = ItemModel.find_by_name(name)

        if item is None:
            item_json['name'] = name
            item = item_schema.load(item_json)
        else:
            item.price = item_json['price']
            item.store_id = item_json['store_id']
        item.save_to_db()
        return item_schema.dump(item), 200


class ItemList(Resource):
    @classmethod
    @jwt_optional
    def get(cls):
        user_id = get_jwt_identity()
        items = item_list_schema.dump(ItemModel.find_all())

        if user_id:
            return {'items': items}, 200
        return {'items': [item['name'] for item in items],
                'message': MUST_LOGIN}, 200
