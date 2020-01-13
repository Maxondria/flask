from flask_restful import Resource
from flask import request
from models.store import StoreModel
from flask_jwt_extended import jwt_required
from schemas.store import StoreSchema

STORE_NOT_EXISTS = 'A store with name {} does not exist'
STORE_ALREADY_EXISTS = 'A store with name {} exists already'
ERROR_INSERTING = 'An error occured while inserting a store.'
STORE_DELETED = 'Store deleted'

store_schema = StoreSchema()
store_list_schema = StoreSchema(many=True)


class Store(Resource):
    @classmethod
    @jwt_required
    def get(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            return store_schema.dump(store), 200
        return {'message': STORE_NOT_EXISTS.format(name)}, 404

    @classmethod
    @jwt_required
    def post(cls, name: str):
        if StoreModel.find_by_name(name):
            return {'message': STORE_ALREADY_EXISTS.format(name)}, 400

        store = StoreModel(name=name)

        try:
            store.save_to_db()
        except:
            return {'message': ERROR_INSERTING}, 500

        return store_schema.dump(store), 201

    @classmethod
    @jwt_required
    def delete(cls, name: str):
        store = StoreModel.find_by_name(name)
        if store:
            store.delete_from_db()
            return {'message': STORE_DELETED}
        return {'message': STORE_NOT_EXISTS.format(name)}


class StoreList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        return {'stores': store_list_schema.dump(StoreModel.find_all())}
