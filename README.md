# MemeBot

***MemeBot - бот для постинга вложений из сообщений в ваш канал***

### Инструкция по работе с ботом

- В корневой папке создайте файл *.env* по примеру *.env.example* и заполните его своими данными
- Запустите программу
- Добавьте бота к себе в канал
- Отправьте любое сообщение с вложением боту, он опубликует это в вашем канале

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
alembic revision -m "first migration" --autogenerate
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
