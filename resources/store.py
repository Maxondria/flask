from flask_restful import Resource, reqparse
from models.store import StoreModel
from flask_jwt_extended import jwt_required

STORE_NOT_EXISTS = 'A store with name {} does not exist'
STORE_ALREADY_EXISTS = 'A store with name {} exists already'
ERROR_INSERTING = 'An error occured while inserting a store.'
STORE_DELETED = 'Store deleted'


class Store(Resource):
    @jwt_required
    def get(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json(), 200
        return {'message': STORE_NOT_EXISTS.format(name)}, 404

    @jwt_required
    def post(self, name: str):
        if StoreModel.find_by_name(name):
            return {'message': STORE_ALREADY_EXISTS.format(name)}, 400

        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {'message': ERROR_INSERTING}, 500

        return store.json(), 201

    @jwt_required
    def delete(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {'message': STORE_DELETED}
        return {'message': STORE_NOT_EXISTS.format(name)}


class StoreList(Resource):
    @jwt_required
    def get(self):
        return {'stores': [store.json() for store in StoreModel.find_all()]}
