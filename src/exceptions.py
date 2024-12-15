class BaseProjectException(Exception):
    pass


class UserNotFoundError(BaseProjectException):
    def __init__(self, account_id: int) -> None:
        self.account_id = account_id
        super().__init__(f"Пользователь с account_id={self.account_id} не найдет в БД.")


class ChannelNotFoundError(BaseProjectException):
    def __init__(self, channel_id: int) -> None:
        self.channel_id = channel_id
        super().__init__(f"Канал с channel_id={self.channel_id} не найден в БД.")


class ObjectAlreadyExistsError(BaseProjectException):
    def __init__(self, instance) -> None:
        self.instance = instance
        super().__init__(f"Ошибка при создании объекта {self.instance}. Объект с таким id уже существует в БД.")


class UserIsNotAdminInChannel(BaseProjectException):
    def __init__(self, account_id: int, channel_id: int) -> None:
        self.account = account_id
        self.channel = channel_id
        super().__init__(
            f"Аккаунт account_id={self.account_id} не является администратором канала channel_id={self.channel_id}",
        )


class BotKickedFromTheChannel(BaseProjectException):
    def __init__(self, channel_id: int) -> None:
        self.channel_id = channel_id
        super().__init__(f"Бот был удален из канала channel_id={channel_id}")
