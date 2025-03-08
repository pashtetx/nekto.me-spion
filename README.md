# Spion anonymous chat by nekto.me

<div align="center">
    <i>Шпион для анонимного чата nekto.me, на базе вебсокетов</i>
</div>

---
Шпион написан на [Python 3.11](https://www.python.org/downloads/release/python-3110/) и использует [асинхронность](https://docs.python.org/3/library/asyncio.html) что позволяет запускать 2 клиентов одновременно. Он использует библиотеку [websockets](https://websockets.readthedocs.io/en/stable/index.html), которая дает возможность асинхронного подключения к вебсокетам.

### Запуск

Чтобы запустить бота вам нужно установить на свое устройство. Чтобы установить на windows перейдите по ссылке: [Python 3.11 (Windows).](https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe)

Чтобы установить на линукс:
- Arch linux: ```yay -S python311```
- Ubuntu: ```sudo apt install python3.11```

Следущий шаг это настройка файла **config.ini**:

- Вам нужно достать 2 токены юзеров из nekto.me/chat.
    - Откоройте вкладку инкогнито, перейдите на этот [сайт](https://nekto.me/chat). Откройте консоль и введите: ```JSON.parse(localStorage.getItem("storage_v2"))["user"]["authToken"]```
    - Пообщайтесь 5-10 раз для того чтобы система nekto.me поняла что вы не бот.
    - И обзятельно сохраните User-Agent из браузера которого вы все это сделали.
- После того как у вас есть 2 токена и User-Agent этих токенов то можно приступать к настройке конфига
    - откройте файл config.ini и в секции ```client/client_name```, измените token и ua на User-Agent.
    - и так-же сделать с ```client/client_name2```.

**Остальные настройки:**

| Название    | Значение            | Пример            |
| ----------- | -----------         | ---------         |
| my-sex      | Пол клиента         | M или F           |
| my-age      | Возраст клиента     | 0,17; 18,25       |
| wish-sex    | Пол собеседника     | M или F           |
| wish-age    | Возраст собеседника | 0,17; 0,17 18 21  |
| is-adult    | 18+ чат             | True или False    |
| role        | Ролка               | True или False    |

> Подсказка: M - это парень, F - это девушка

### Мой телеграм канал
У меня есть свой телеграм канал: t.me/progerfromselo 