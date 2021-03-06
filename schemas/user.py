from ma import ma
from marshmallow import pre_dump
# also: pre_load, post_load, post_dump
from models.user import UserModel


class UserSchema(ma.ModelSchema):
    class Meta:
        model = UserModel
        load_only = ('password',)
        dump_only = ('id', 'confirmation')

    @pre_dump
    def filter_confirmations(self, user: UserModel, **kwargs):
        user.confirmation = [user.most_recent_confirmation]
        return user
