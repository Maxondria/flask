from ma import ma
from models.order import OrderModel


class OrderShema(ma.ModelSchema):
    class Meta:
        model = OrderModel
        dump_only = ('id', 'status')
