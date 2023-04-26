from dataclasses import dataclass, asdict
from os import path, environ

base_dir = path.dirname(path.dirname(path.dirname(path.abspath(__file__))))


@dataclass
class Config:
    """
    기본 Configuration
    """
    BASE_DIR = base_dir

    DB_POOL_RECYCLE: int = 900
    DB_ECHO: bool = True # ECHO -> 트루 -> 터미널 실행하면 에코를 함


@dataclass
class LocalConfig(Config):
    PROJ_RELOAD: bool = True
    #DB_URL: str = "mysql+pymysql://travis:ghkd@localhost/notification_api?charset=utf8mb4" # mysql+pymysql://{user}:{password}@{endpoint}:{port}/{db} #local database
    DB_URL: str = "mysql+pymysql://travis:ghkd@svc.sel3.cloudtype.app:31955/notification_api?charset=utf8mb4" # cloudtype 에 배포한 서버와 연결 #cloudtype database

@dataclass
class ProdConfig(Config):
    PROJ_RELOAD: bool = False


def conf(): 
    """
    환경 불러오기
    :return:
    """
    config = dict(prod=ProdConfig(), local=LocalConfig())
    return config.get(environ.get("API_ENV", "local"))  