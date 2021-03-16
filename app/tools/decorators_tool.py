import json
from functools import wraps

from flask import g
from flask import jsonify


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False, None
    return True, json_object
