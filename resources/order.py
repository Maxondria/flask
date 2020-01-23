from collections import Counter

from flask import request
from flask_restful import Resource
from models.item import ItemModel
from models.order import ItemsInOrder, OrderModel
from schemas.order import OrderShema

ITEM_NOT_FOUND = 'Ordered item with id <{}> was not found.'
ORDER_ERROR = 'order error'

order_shema = OrderShema()


class Order(Resource):
    @classmethod
    def get(cls):
        return order_shema.dump(OrderModel.find_all(), many=True), 200

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

        # stripe
        try:
            order.set_status('failed')
            order.charge_with_stripe(data['token'])
            order.set_status('completed')  # charge succeeded
            return order_schema.dump(order), 200
        except error.CardError as e:
            return e.json_body, e.http_status
        except error.RateLimitError as e:
            return e.json_body, e.http_status
        except error.InvalidRequestError as e:
            return e.json_body, e.http_status
        except error.AuthenticationError as e:
            return e.json_body, e.http_status
        except error.APIConnectionError as e:
            return e.json_body, e.http_status
        except error.StripeError as e:
            return e.json_body, e.http_status
        except Exception as e:
            return {"message": ORDER_ERROR}, 500
