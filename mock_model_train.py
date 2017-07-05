import os
from model_manager import ModelManager, PSQLConn
import json
from time import sleep
#model_params
CONFIG_FILE="/Users/ewayman/workspace/model_manager/config.json"
SCHEMA="temp"
MODEL_NICKNAME = 'mock_model'
# pm=ParamManager(CONFIG_FILE)
# p = pm.param_dict

conn_factory = PSQLConn(db=os.getenv('DATABASE_NAME'),
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
                host=os.getenv("DATABASE_HOST"),
                port=os.getenv("DATABASE_PORT")
)
model_manager = ModelManager(
            model_id=None,
            config_file=CONFIG_FILE,
            db_connection=conn_factory, 
            schema=SCHEMA,
            model_nickname=MODEL_NICKNAME
)

p = model_manager.param_dict
TRAINING_PARAMS = p['training_params']

@model_manager.log_model_training
def train(**training_params):
    print(training_params)
    sleep(2)
    return

if __name__ == "__main__":
    model_manager.compile()
    train(**TRAINING_PARAMS)