import logging as _logging

logger = _logging.getLogger("objects")


class _Message:
    pass


class EditableMessage(_Message):
    pass


class ReadOnlyMessage(_Message):
    def __setattr__(self, key, value):
        logger.warning("Tried to modify a ReadOnlyMessage.")
        return
