def filter_kwargs_additive(*valid_kwargs: str):
    """
    Decorator used to filter the keyword arguments passed to a function,
    by keeping only those specified.
    """

    def decorator(func):
        def wrapper(**passed_kwargs):
            # Filter the passed kwargs, leaving only those that were specified
            final_kwargs = {}
            for k, v in passed_kwargs.items():
                if k in valid_kwargs:
                    final_kwargs.update({k: v})
            # Call the function with the filtered kwargs
            return func(**final_kwargs)

        return wrapper

    return decorator


def filter_kwargs_subtractive(*invalid_kwargs: str):
    """
    Decorator used to filter the keyword arguments passed to a function,
    by filtering out those specified.
    """

    def decorator(func):
        def wrapper(**passed_kwargs):
            # Filter the passed kwargs, popping the invalid ones
            for k in invalid_kwargs:
                try:
                    passed_kwargs.pop(k)
                except KeyError:
                    pass
            # Call the function with the filtered kwargs
            return func(**passed_kwargs)

        return wrapper

    return decorator
