from functools import wraps
from typing import Optional, Any, TypeVar, Callable

from .structures import Structure, StructureType
from .utils import is_int, is_float


AnyStructure = TypeVar('AnyStructure', bound=StructureType)


def cast(data: dict, structure: AnyStructure) -> Optional[AnyStructure]:
    """
    Takes data as a dictionary, and tries to cast it to a structure dataclass
    for easier processing down the line.
    It therefore validates the structure of the data, but not the content.
    Returns the value / structure if valid, None otherwise.
    """

    def valid_field(_var: str, _expected_type) -> Optional[Any]:

        def handle_built_in(value, expected_type):
            """
            Handles built-in types such as `str`, `int`, `dict`, etc.
            """
            if expected_type is int:
                if is_int(value):
                    return int(value)
                else:
                    return
            elif expected_type is float:
                if is_float(value):
                    return float(value)
                else:
                    return
            else:
                return expected_type(value)

        def handle_custom_lists(value, expected_type):
            """
            Handles custom typed lists.
            For these, we expect only one member of the structure's list:
            the type the list's elements are supposed to have.
            """
            if actual_type is not list:
                return

            if len(expected_type) != 1:
                raise ValueError(f'Invalid list definition '
                                 f'in structure {structure!r}')
            inner_type = expected_type[0]

            elements = []
            for element in value:
                if isinstance(inner_type, type):
                    elements.append(handle_built_in(element, inner_type))
                elif isinstance(inner_type, Structure):
                    elements.append(handle_sub_structures(element, inner_type))

            if any([e is None for e in elements]):
                return

            return elements

        def handle_sub_structures(value, expected_type):
            return cast(value, expected_type)

        _value = data[_var]
        actual_type = type(_value)

        if isinstance(_expected_type, type):
            return handle_built_in(_value, _expected_type)

        elif isinstance(_expected_type, list):
            return handle_custom_lists(_value, _expected_type)

        elif isinstance(_expected_type, Structure):
            return handle_sub_structures(_value, _expected_type)

        else:
            raise NotImplementedError(
                f"Couldn't validate var {_var!r} with type "
                f"{_expected_type} (of type {type(_expected_type)})"
            )

    # Annotations will be our reference
    ano = structure.__annotations__

    if data.keys() != ano.keys():
        # Dictionaries have different keys
        return

    validated_struct = {
        v: valid_field(v, t)
        for v, t in ano.items()
    }

    if any([value is None for value in validated_struct.values()]):
        # One or more values are invalid
        return

    return structure(**validated_struct)


def validate_export_structure(struct: AnyStructure) -> Callable:
    """
    Decorator used to validate the output of an export method.
    The decorated export method must return a Structure.
    The function will validate the export structure, and return a dictionary.
    If the returned structure is invalid, a `ValueError` exception is raised.
    """

    def decorator(func) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> dict:
            returned_struct = func(*args, **kwargs)
            out_dict = returned_struct.to_data()
            _valid_struct = cast(out_dict, struct)
            if _valid_struct is None:
                msg = "Invalid export structure."
                raise ValueError(msg)
            return out_dict
        return wrapper

    return decorator
