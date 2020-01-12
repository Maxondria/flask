from flask_restful import Resource, reqparse
from models.item import ItemModel
from flask_jwt_extended import (
    jwt_required,
    jwt_optional,
    get_jwt_claims,
    fresh_jwt_required,
    get_jwt_identity)

BLANK_ERROR = '{} can not be blank'
ITEM_NOT_FOUND = 'An item with name {} does not exist'
ITEM_ALREADY_EXISTS = 'An item with name {} already exists'
ERROR_INSERTING = 'An error occured while saving an item'
MUST_BE_ADMIN = 'Admin privillages required'
ITEM_DELETED = 'Item deleted'
MUST_LOGIN = 'More data available if you login'


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help=BLANK_ERROR.format('price')
                        )
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help=BLANK_ERROR.format('store_id')
                        )

    @jwt_required
    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {'message': ITEM_NOT_FOUND.format(name)}, 404

    @fresh_jwt_required
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return {'message': ITEM_ALREADY_EXISTS.format(name)}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {'message': ERROR_INSERTING}, 500

        return item.json(), 201

    @jwt_required
    def delete(self, name: str):
        # Check if user is admin
        claims = get_jwt_claims()

        if not claims['is_admin']:
            return {'message': MUST_BE_ADMIN}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': ITEM_DELETED}
        return {'message': ITEM_NOT_FOUND.format(name)}

    @jwt_required
    def put(self, name: str):
        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
            item.store_id = data['store_id']
        item.save_to_db()
        return item.json(), 200


class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]

        if user_id:
            return {'items': items}, 200
        return {'items': [item['name'] for item in items],
                'message': MUST_LOGIN}, 200
