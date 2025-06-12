from configparser import ConfigParser
from client import Client

import logging
import structlog

def get_config(path: str = "config.ini") -> ConfigParser:
    configparser = ConfigParser()
    configparser.read(path)
    return configparser

def get_debug():
    config = get_config()
    if config.getboolean("settings", "debug", fallback=None):
        structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG))
    else:
        structlog.configure(wrapper_class=structlog.make_filtering_bound_logger(logging.WARNING))

def get_clients():
    config = get_config()
    clients = config.get("settings", "clients").split()
    for client in clients:
        name = "client/" + client
        token = config.get(name, "token")
        ua = config.get(name, "ua")
        sex = config.get(name, "sex", fallback=None)
        wish_sex = config.get(name, "wish-sex", fallback=None)
        age = list(map(lambda x: int(x), config.get(name, "age", fallback=None).split(",")))
        wish_age = [
            list(map(lambda x: int(x), age.split(","))) 
            for age in config.get(name, "wish-age", fallback=None).split("-")
        ]
        role = config.getboolean(name, "role", fallback=None)
        adult = config.getboolean(name, "adult", fallback=None)
        wish_role = config.get(name, "wish-role", fallback=None)
        yield Client(
            token=token, 
            ua=ua,
            sex=sex,
            wish_sex=wish_sex,
            age=age,
            wish_age=wish_age,
            wish_role=wish_role,
            role=role,
            adult=adult,
        )