from flask_restful import Resource, reqparse
from models.item import ItemModel
from flask_jwt_extended import (
    jwt_required,
    jwt_optional,
    get_jwt_claims,
    fresh_jwt_required,
    get_jwt_identity)


class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
                        type=float,
                        required=True,
                        help='Price is required!!'
                        )
    parser.add_argument('store_id',
                        type=int,
                        required=True,
                        help='Store ID is required!!'
                        )

    @jwt_required
    def get(self, name: str):
        item = ItemModel.find_by_name(name)
        if item:
            return item.json(), 200
        return {'message': f'An item with name {name} does not exist'}, 404

    @fresh_jwt_required
    def post(self, name: str):
        if ItemModel.find_by_name(name):
            return {'message': f'An item with name {name} exists already'}, 400

        data = Item.parser.parse_args()

        item = ItemModel(name, **data)

        try:
            item.save_to_db()
        except:
            return {'message': 'An error occured while inserting an item.'}, 500

        return item.json(), 201

    @jwt_required
    def delete(self, name: str):
        # Check if user is admin
        claims = get_jwt_claims()

        if not claims['is_admin']:
            return {'message': 'Admin privillages required'}, 401

        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'Item deleted'}
        return {'message': 'Item not found'}

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
                'message': 'More data available if you login'}, 200
