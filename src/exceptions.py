class UserNotFoundError(Exception):
    def __init__(self, account_id: int) -> None:
        message = f"Произошла ошибка при получении пользователя с account_id={account_id} из БД."
        super().__init__(message)


class ChannelNotFoundError(Exception):
    def __init__(self, channel_id: int) -> None:
        message = f"Произошла ошибка при получении канала с channel_id={channel_id} из БД."
        super().__init__(message)


class ObjectAlreadyExistsError(Exception):
    def __init__(self, new_data: dict) -> None:
        message = f"Произошла ошибка при создании объекта {new_data} в БД, объект с таким id уже существует."
        super().__init__(message)


class UserNotAdminInChannelError(Exception):
    def __init__(self, account_id: int, channel_id: int) -> None:
        message = f"Пользователь с account_id={account_id} не является администратором канала с channel_id={channel_id}"
        super().__init__(message)
