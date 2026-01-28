from shared.serializers import BaseSerializer


class UserSerializer(BaseSerializer):
    def serialize_instance(self, instance) -> dict:
        return {
            'id': instance.pk,
            'username': instance.username,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
        }


class TokenSerializer(BaseSerializer):
    def serialize_instance(self, instance) -> dict:
        return {
            'key': str(instance.key),
            'created_at': instance.created_at.isoformat(),
            'user': UserSerializer(instance.user).serialize(),
        }
