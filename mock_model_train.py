import os
from model_manager import ModelManager, PSQLConn
import configparser
from time import sleep
#model_params
CONFIG_FILE="/Users/ewayman/workspace/model_manager/config"
SCHEMA="temp"
MODEL_NICKNAME = 'mock_model'
# pm=ParamManager(CONFIG_FILE)
# p = pm.param_dict

conn_factory = PSQLConn(db='ewayman',
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
                host=os.getenv("DATABASE_HOST"),
                port=os.getenv("DATABASE_PORT")
)
model_manager = ModelManager(
            config_file=CONFIG_FILE,
            db_connection=conn_factory, 
            schema=SCHEMA,
            model_nickname=MODEL_NICKNAME
)

@model_manager.log_model_training
def train():
    sleep(2)
    return

if __name__ == "__main__":
    train()
    # model_manager.create_tables()
    # print(model_manager.param_manager.get_json())