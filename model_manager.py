import os
import configparser
import json
from datetime import datetime as dt
#from tables import metadata, models, model_results, model_objects
from sqlalchemy import create_engine, MetaData, Integer, DateTime, Table, Column, Interval, Text, JSON, Numeric, ForeignKey,PickleType
import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


############ helper functions to define tables



def models_table(metadata,schema):
    models = Table('models',metadata,
        Column('model_id',Integer,primary_key=True),
        Column('time_stamp',DateTime),
        Column('time_to_run_script',Interval),
        Column('model_script',Text),
        Column('model_nickname',Text),
        Column('model_param_dict',JSON),
    Column('param_config_file',Text),
        schema=schema
    )
    return models

def model_results(metadata,schema):
    model_results = Table('model_results',metadata,
        Column('model_id',Integer,ForeignKey(
            '{}.models.model_id'.format(schema),
            ondelete='CASCADE'
            )
        ),
        Column('data_point_id',Integer),
        Column('actual',Numeric),
        Column('prediction',Numeric),
        schema=schema
    )
    return model_results

def serialized_objects_table(metadata,schema):
    serialized_objects = Table('serialized_objects',metadata,
        Column('model_id',ForeignKey(
            '{}.models.model_id'.format(schema),
            ondelete='CASCADE'
            )
        ),
        Column('object_name',Text),
        Column('object_params',JSON),
        Column('serialized_object',PickleType),
        schema=schema
    )
    return serialized_objects


#### class definitions

class ParamManager(object):

    def __init__(self,config_file):
        self._config_file = config_file
        config = configparser.ConfigParser()
        config.read(self._config_file)
        self.param_dict = {s:dict(config.items(s)) for s in config.sections()}
        self.config = config

    def get_json(self):
        return json.dumps(self.param_dict)

class PSQLConn(object):
    """Stores the connection to psql."""
    def __init__(self, db, user, password, host,port=5432):
        self.db = db
        self.user = user
        self.password = password
        self.host = host
        self.port = port

    def connect(self):
        connection = pg.connect(
                host=self.host,
                database=self.db,
                user=self.user,
                password=self.password,
                port = self.port)
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return connection
    
    def engine(self):
        engine = create_engine("postgresql://{user}:{password}@{host}:{port}/{db}".format(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            db=self.db
            ))
        return engine

class ModelManager(object):

    def __init__(self,
                config_file,
                db_connection, 
                schema,
                model_nickname=None):
        self.db_connection = db_connection
        #should this be hidden?
        self.param_manager = ParamManager(config_file)
        self.config_file = config_file
        self.schema = schema
        self.metadata = MetaData()
        self.models = models_table(self.metadata,schema)
        self.model_results = model_results(self.metadata,schema)
        self.seralized_objects = serialized_objects_table(self.metadata,schema)
        if model_nickname is None:
            self.model_nickname = os.path.basename(__file__)
        else: 
            self.model_nickname = model_nickname

    def create_tables(self):
        """Initialize all tables if they don't already exist"""
        engine = self.db_connection.engine()
        self.metadata.create_all(engine)

    def log_model_training(self,train_model):
        """Wrapper around function to train a model.  Stores model in models table"""
        def wrapper(*train_model_args):
            start = dt.now()
            output = train_model(*train_model_args)
            time_to_train = dt.now()-start
            self._add_row_to_models_table(time_to_run_script=time_to_train)
            return output
        return wrapper

    def get_param_dict(self):
        return self.param_manager.param_dict

    def _add_row_to_models_table(self,time_to_run_script):
        self.create_tables()
        insert = self.models.insert().values(
            time_stamp = dt.now(),
            time_to_run_script = time_to_run_script,
            model_script = os.path.basename(__file__),
            model_nickname = self.model_nickname,
            param_config_file = self.param_manager._config_file,
            model_param_dict = self.param_manager.get_json()
        )
        with self.db_connection.engine().connect() as conn:
            result = conn.execute(insert)
        return result

    def log_results(self):
        """"""
        pass


