Тестирование миграций на MySql
==============================

команда ниже позволяет запустить mysql сервер локально, нужен только docker.
::

    docker rm -f derzn && docker run --name derzn -e MYSQL_ROOT_PASSWORD=password -e MYSQL_DATABASE=derzn -p 3306:3306 -d mysql:5.7.27 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

Переменная окружения `DB_URL` должна быть `mysql://root:password@127.0.0.1:3306/derzn`.

Так же нужно поправить настройки django. Данную правку нельзя коммитить!

::

    DATABASES = {"default": env.dj_db_url("DB_URL")}
    DATABASES["default"]["OPTIONS"] = {"ssl_mode": "DISABLED"}


Когда проверка выполнена и отработана, можно перейти к установке.

Установка
=========

Это может быть выполнено разными путями:

- вручную ftp
- полуавтоматически ssh
- автоматически (Continuous Delivery)

Последний вариант требует реализации Continuous Delivery, конкретнее - найти бесплатную платформу.
В наше время это стало сложно: heroku/circleci/. Возможно поможет сервис Buddy.

Вручную
-------

1. Создать чистый архив с кодом проекта с ветки develop:

::

    git checkout develop
    git pull
    git archive --format=zip -o archive.zip delelop

2. Закинуть архив на сервер

::

    scp archive.zip USER:PASSWD@HOST:/www/test.derzn.ru/dz

3. Установка файлов, миграция БД и рестарт сервера

::

    ssh USER:PASSWD@HOST './scripts/remote_install archive.zip www/test.derzn.ru'
