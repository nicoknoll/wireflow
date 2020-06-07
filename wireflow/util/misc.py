import uuid
import re
from importlib import import_module


ID_ALPHABET = list("23456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz")


def int_to_string(number):
    output = ''
    alpha_len = len(ID_ALPHABET)
    while number:
        number, digit = divmod(number, alpha_len)
        output += ID_ALPHABET[digit]
    return output[::-1]


def generate_id(prefix=None):
    generated = int_to_string(uuid.uuid4().int)[:16]
    return f'{prefix}_{generated}' if prefix else generated


def format_class_name(class_name):
    return ' '.join(re.sub(
        '([A-Z][a-z]+)', r' \1',
        re.sub('([A-Z]+)', r' \1', class_name)
    ).split())


def flatten(l):
    return [item for sublist in l for item in sublist]


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
                          ) from err
