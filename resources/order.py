from collections import Counter

from flask import request
from flask_restful import Resource
from models.item import ItemModel
from models.order import ItemsInOrder, OrderModel

ITEM_NOT_FOUND = 'Ordered item with id <{}> was not found.'


class Order(Resource):
    @classmethod
    def post(cls):
        """
        - Expect a token
        - list of item IDs from the request body

        #eg: {'token':'zxc', 'item_ids': [1, 2, 3, 3, 5, 5]}

        - Construct an order, connect to Stripe, make a charge
        """
        data = request.get_json()
        items = []

        item_id_quantities = Counter(data['item_ids'])

        # item_id_quantities.most_common(), returns list items_ids with no of occurences
        # = [(1,1), (2, 1), (3, 2), (5,2)]

        for _id, count in item_id_quantities.most_common():
            item = ItemModel.find_by_id(_id)
            if not item:
                return {'message': ITEM_NOT_FOUND.format(_id)}, 404
            items.append(ItemsInOrder(item_id=_id, quantity=count))

        order = OrderModel(items=items, status='pending')
        order.save_to_db()
