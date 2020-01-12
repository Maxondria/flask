from flask_restful import Resource, reqparse
from models.store import StoreModel
from flask_jwt_extended import jwt_required


class Store(Resource):
    @jwt_required
    def get(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store.json(), 200
        return {'message': f'A store with name {name} does not exist'}, 404

    @jwt_required
    def post(self, name: str):
        if StoreModel.find_by_name(name):
            return {'message': f'A store with name {name} exists already'}, 400

        store = StoreModel(name)

        try:
            store.save_to_db()
        except:
            return {'message': 'An error occured while inserting a store.'}, 500

        return store.json(), 201

    @jwt_required
    def delete(self, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {'message': 'Store deleted'}
        return {'message': 'Store not found'}


class StoreList(Resource):
    @jwt_required
    def get(self):
        return {'stores': [store.json() for store in StoreModel.find_all()]}
