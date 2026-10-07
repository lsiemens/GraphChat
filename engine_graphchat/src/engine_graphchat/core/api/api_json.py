import typing
import json

from engine_graphchat.core import exceptions


ACCEPTED_TYPES = [str, int, float, list]


def validate_field(value, target_type):
    if typing.get_origin(target_type) is None:
        if target_type not in ACCEPTED_TYPES:
            raise exceptions.ContentError(f"Validation failed: the target type {target_type} is not whitelisted")
        return isinstance(value, target_type)

    origin = typing.get_origin(target_type)
    args = typing.get_args(target_type)

    if origin in ACCEPTED_TYPES:
        if len(args) != 1:
            raise exceptions.ContentError("Validation failed: composite objects must have exactly one type")

        if not isinstance(value, origin):
            return False

        return all(validate_field(element, args[0]) for element in value)

    raise exceptions.ContentError(f"Validation failed: the target type {target_type} is not supported")


def load_JSON_as_type(text, target):
    hints = typing.get_type_hints(target)

    try:
        data = json.loads(text)
    except (json.JSONDecodeError, TypeError) as e:
        raise exceptions.ServiceError("Failed decode json") from e

    if not isinstance(data, dict):
        raise exceptions.ContentError("Incompatible structure: JSON must load as a dictionary")

    if set(data) != set(hints):
        raise exceptions.ContentError("Incompatible structure: JSON fields do not match the target fields")

    new_obj = target()

    for field, field_type in hints.items():
        value = data[field]

        if not validate_field(value, field_type):
            raise exceptions.ContentError(f"Incompatible structure: {field} does not match the target field type")

        setattr(new_obj, field, value)

    return new_obj


def dump_JSON_as_type(obj, target):
    hints = typing.get_type_hints(target)

    data = {key: getattr(obj, key) for key in hints.keys()}
    return json.dumps(data)
