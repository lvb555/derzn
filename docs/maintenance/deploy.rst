Тестирование миграций на MySql
==============================

команда ниже позволяет запустить mysql сервер локально, нужен только docker.
::

    docker rm -f derzn && docker run --name derzn -e MYSQL_ROOT_PASSWORD=password \
        -e MYSQL_DATABASE=derzn -p 3306:3306 -d mysql:5.7.27 \
        --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

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
- полуавтоматически (ansible скрипты в репозитории)
- автоматически (Continuous Delivery)

Последний вариант требует реализации Continuous Delivery, конкретнее - найти
бесплатную платформу. В наше время это стало сложно: heroku/circleci/. Возможно
поможет github actions. Открытый вопрос.

База данных используемая для тестового сервера - MySql, потому что только она
есть на reg.ru.

Вручную
-------

Это не сложно, но затратно по времени, скучно и так далее. Но для понимания полезно.

1. Установка файлов

::

    ssh USER:PASSWD@HOST
    cd www/test.derzn.ru/dz
    git pull

2. Настройка

Нужно поправить `dz/settings.py` (на сервере `$HOME/www/test.derzn.ru/dz/dz/settings.py`) и
заполнить файл `$HOME/www/test.derzn.ru/dz/.env` (на сервере) по подобию файла в репозитории
`env.sample`. Реальные данные файлов для примера можно глянуть в
`scripts/ansible/files/`, но они зашифрованы. Подробнее в параграфе про
полуавтоматический режим установки.

4. Миграция БД

Тестовый сервер исключение, потому для него делать дамп базы перед миграциями
не нужно.

::

    source $HOME/www/test.derzn.ru/venv/bin/activate
    ./manage.py migrate


5. Рестарт сервера

::

    touch $HOME/www/test.derzn.ru/.restart-app


Полуавтоматически
-----------------

Чтобы упростить процесс часто пишут скрипты, а индистрия создала "фреймворк" для
этого - `ansible<https://docs.ansible.com/>`_.

Сами скрипты расположены в каталоге `scripts/ansible`.

Короче, чтобы сделать все тоже самое, что и выше, с помощью ansible:

::

    ansible-vault decrypt --vault-password-file .vault files/test.env
    ansible-playbook test.yaml

Один нюанс - нужно записать пароль от ansible-vault в файл .vault или любой
другой, но тогда и в команде выше указать путь до него. Пароль есть у Анатолия.

И еще момент - если вы начали менять файлы ansible, то НИКОГДА не коммитьте
незашифрованными файлы с секретами: ключи к бд и т.п. Для этого шифруйте такие
вещи командой:

::

    ansible-vault encrypt --vault-password-file .vault files/test.env

Бонусом, через ansible написана переустановка дампа в БД:

::

    ansible-vault decrypt --vault-password-file .vault files/test.env
    ansible-playbook loaddump.yaml -e local_dump_file=mydump.json

Операция может быть долгой, потому чистите дамп от лишних данных
(admin.logentry, drevo.browsinghistory).

Так же операция зависнет через некоторое время, потому подождав 5 минут можно
грохнуть процесс - это специфика загрузки дампа на чистую БД, а не ansible.
