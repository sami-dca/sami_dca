# About databases

## A few guidelines

- Each file should start with an underscore, so to not be imported directly
- Therefore, the database object should be imported in the `__init__.py` file
- Databases should not manipulate Sami objects directly,
  instead, use DBOs (DataBase Objects), and implement, in the Sami object,
  a `from_dbo` class method
- In the same vein, methods that should take DBOs, and to get these,
  Sami objects should implement a `to_dbo` method
