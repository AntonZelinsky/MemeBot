# MemeBot

***MemeBot - бот для репостинга сообщений в вашу группу***

### Инструкция по работе с ботом

- В корневой папке создайте файл *.env* по примеру *.env.example* и заполните его
- Добавьте бота к себе в группу
- Отправьте любое сообщение с вложением боту, он опубликует это в вашем канале

### Особенности

<details>
 <summary>
 Особенности
 </summary>

* В данный момент бот работает только с одной группой

</details>

### Переменные окружения

<details>
 <summary>
 Переменные окружения
 </summary>

```
DESCRIPTION=      # Описание к публикуемым сообщениям
BOT_TOKEN=        # Токен вашего telegram бота
DATABASE_URL=     # Путь подключения к БД
```

</details>

### Запуск проекта

<details>
 <summary>
 Подготовка и запуск бота
 </summary>

- Установите poetry

```shell
pip install poetry
```

- Находясь в папке проекта, установите зависимости

```shell
poetry install
```

- Активируйте виртуальное окружение с помощью poetry

```shell
poetry shell
```

- Создайте миграции

```shell
alembic revision --message="Initial" --autogenerate
```

- Установите миграции

```shell
alembic upgrade head
```

- Запустите бота

```shell
python.exe run.py
```

</details>


Special for https://t.me/Memazes
