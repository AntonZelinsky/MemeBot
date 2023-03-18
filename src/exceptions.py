class UserNotFound(Exception):
    def __init__(self, account_id: int) -> None:
        message = f"Пользователь с account_id={account_id} не найдет в БД."
        super().__init__(message)


class ChannelNotFound(Exception):
    def __init__(self, channel_id: int) -> None:
        message = f"Канал с channel_id={channel_id} не найден в БД."
        super().__init__(message)


class ObjectAlreadyExists(Exception):
    def __init__(self, instance) -> None:
        message = f"Произошла ошибка при создании объекта {instance}. Объект с таким id уже существует в БД."
        super().__init__(message)


class UserNotAdminInChannel(Exception):
    def __init__(self, account_id: int, channel_id: int) -> None:
        message = f"Пользователь account_id={account_id} не является администратором канала channel_id={channel_id}"
        super().__init__(message)
