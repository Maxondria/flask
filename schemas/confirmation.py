from ma import ma
from models.user import UserModel
from models.confirmation import ConfirmationModel


class ConfirmationSchema(ma.ModelSchema):
    class Meta:
        model = ConfirmationModel
        dump_only = ('id', 'expired_at', 'confirmed')
        load_only = ('user',)
        include_fk = True
