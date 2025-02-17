import os
import configparser

def to_absolute_path(filename: str) -> str:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(current_dir, filename)

class AppConfig:
    def __init__(self, test = False):
        config = configparser.ConfigParser()
        config_file_path = "config.ini" if os.path.exists("config.ini") else "config.ini.sample"
        config.read(config_file_path)
        host = config["DEFAULT"]["Host"]
        port = int(config["DEFAULT"]["Port"])
        request_body_limit = int(config["DEFAULT"]["RequestBodyLimit"])
        api_key = config["DEFAULT"]["ApiKey"]
        in_memory = True if test else config["DEFAULT"]["InMemory"] == "true"
        debug = config["DEFAULT"]["Debug"] == "true"
        galaxy_database = config["DEFAULT"]["GalaxyDatabase"]

        self.server = ServerConfig(host, port, request_body_limit)
        self.auth = AuthConfig(api_key)
        self.database = DatabaseConfig(to_absolute_path(config["DEFAULT"]["DatabasePath"]), in_memory, debug)
        self.galaxy_database = galaxy_database

class DatabaseConfig: 
    def __init__(self, path, in_memory=False, debug=False):
        self.path = path
        self.in_memory = in_memory
        self.debug = debug

class AuthConfig: 
    def __init__(self, api_key):
        self.bearer_token = api_key

class ServerConfig: 
    def __init__(self, host, port, request_body_limit):
        self.host = host
        self.port = port
        self.request_body_limit = request_body_limit

def get_env_var(key: str):
    value = os.environ.get(key)
    if value is None:
        raise ValueError(f"{key} is not configured")
    return value

