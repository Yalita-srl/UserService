from calendar import timegm
from datetime import datetime

from graphql_jwt.settings import jwt_settings

def jwt_payload(user, context=None):
    """
    Custom payload handler to include user ID, email, and role.
    This avoids issues with fields that don't exist on the custom user model.
    """
    jwt_datetime = datetime.utcnow() + jwt_settings.JWT_EXPIRATION_DELTA
    jwt_expires = timegm(jwt_datetime.utctimetuple())

    payload = {
        'user_id': str(user.pk),
        'email': user.email,
        'role': user.role,
        'exp': jwt_expires,
        'orig_iat': timegm(datetime.utcnow().utctimetuple()),
    }

    if jwt_settings.JWT_AUDIENCE is not None:
        payload['aud'] = jwt_settings.JWT_AUDIENCE

    if jwt_settings.JWT_ISSUER is not None:
        payload['iss'] = jwt_settings.JWT_ISSUER

    return payload
