import csv

CONFIG_FILE = "./config.csv"

CONFIG_OPTION_SERVER_IP = "server_ip"
CONFIG_OPTION_SERVER_PORT = "server_port"
CONFIG_OPTION_NAME = "name"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        reader = csv.reader(file, delimiter=";")
        ret = dict()
        for key, *value in reader:
            if len(value) == 1:
                value = value[0]
            else:
                value = tuple(value)
            ret[key] = value
        return ret
