import os
import sys
import configparser
import json
from datetime import datetime as dt
#from tables import metadata, models, model_results, model_objects
from sqlalchemy import (create_engine,
    MetaData, Integer, DateTime, Table,
    Column, Interval, Text, JSON, Numeric,
    ForeignKey,PickleType)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func,exists
import psycopg2 as pg
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


############ helper functions to define tables
##move these functions to schema.py file

"""consider adding fields for number of versions, last version, last modified, etc.
json of model objects comprising the model
json field of model_params.  Should be nested {"component_1":{**compnent_1 params},"component_2" params}
"""
def model_master_list(metadata,schema):
    models = Table('model_master_list',metadata,
        Column('model_id',Integer,primary_key=True),
        Column('time_created',DateTime),
        Column('initializing_script',Text),
        Column('model_param_dict',JSON),
        schema=schema
    )
    return models

def model_training(metadata,schema):
    model_training = Table('model_training',metadata,
        Column('model_id',Integer,ForeignKey(
            '{}.model_master_list.model_id'.format(schema),
            ondelete='CASCADE'
            )
        ),
        Column('time_stamp',DateTime),
        Column('time_to_run_script',Interval),
        Column('model_script',Text),
        Column('model_nickname',Text),
        Column('model_param_dict',JSON), #can include for consistency, but maybe not be needed if we can find in model_master_list
        Column('training_param_dict',JSON),
        Column('training_metrics',JSON),
        Column('param_config_file',Text),
        schema=schema
    )
    return model_training

def model_results(metadata,schema):
    model_results = Table('model_results',metadata,
        Column('model_id',Integer,ForeignKey(
            '{}.model_master_list.model_id'.format(schema),
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
            '{}.model_master_list.model_id'.format(schema),
            ondelete='CASCADE'
            )
        ),
        Column('object_name',Text),
        Column('object_params',JSON),
        Column('serialized_object',PickleType),
        Column('time_created',DateTime),
        Column('initializing_script',Text),
        schema=schema
    )
    return serialized_objects


#### class definitions
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
                model_nickname=None,
                model_id = None):
        self.db_connection = db_connection
        self.config_file = config_file
        with open(self.config_file) as config:
            self.param_dict = json.load(config)
        self.schema = schema
        self.metadata = MetaData()
        self.model_master_list = model_master_list(self.metadata,schema)
        self.model_training = model_training(self.metadata,schema)
        self.model_results = model_results(self.metadata,schema)
        self.seralized_objects = serialized_objects_table(self.metadata,schema)
        if model_nickname is None:
            self.model_nickname = self.config_file
        else: 
            self.model_nickname = model_nickname
        self.parent_script = sys.argv[0]
        self.model_id = model_id

    #compiling the model stores an entry in model_master_list table
    #crea
    def compile(self):
        """
        Compiling the model manager creates an entry for the model_manager object in the model_master_list
        table if the model_id doesn't exist, otherwise it checks that the id exists.
        We create all metadata tables that they don't already exist.
        """
        #'model_id','time_created''initializing_script','model_param_dict'
        self.create_tables()
        session_maker= sessionmaker(bind = self.db_connection.engine())
        if self.model_id is None:
            session = session_maker()
            max_id = session.query(func.max(self.model_master_list.c.model_id)).scalar() or 0
            model_id = max_id+1
            insert = self.model_master_list.insert().values(
                            model_id = model_id,
                            time_created = dt.now(),
                            initializing_script = self.parent_script,
                            model_param_dict = os.path.basename(self.config_file),
            )
            print(insert)
            session.execute(insert)
            session.commit()
            self.model_id = model_id
        else:
            session = session_maker()
            id_exists=session.query(exists().where(self.model_master_list.c.model_id==self.model_id)).scalar()
            if id_exists == False:
                raise ValueError("model_id: {model_id} does not exist in table: {schema}.model_master_list".format(
                                    model_id = self.model_id,
                                    schema = self.schema
                                    )
                                )
            session.commit()
    def create_tables(self):
        """Initialize all tables if they don't already exist"""
        engine = self.db_connection.engine()
        self.metadata.create_all(engine)

    def log_model_training(self,train_model):
        """Wrapper around function to train a model.  Stores outcome in trainingtable
        train_model is assumed to return a dict of the outcome from the training.  (e.g. keys are indexed by CV folds
        values are sub dicts mapping accuracy and AUC for each fold
        """
        def wrapper(**train_model_args):
            start = dt.now()
            output = train_model(**train_model_args)
            time_to_train = dt.now()-start
            self._add_row_to_model_training_table(time_to_run_script=time_to_train,
                                                training_param_dict=train_model_args,
                                                training_metrics=output
                                                )
            return output
        return wrapper

    def _add_row_to_model_training_table(self,time_to_run_script,training_param_dict,training_metrics):
        #self.create_tables()
        insert = self.model_training.insert().values(
            model_id = self.model_id,
            time_stamp = dt.now(),
            time_to_run_script = time_to_run_script,
            model_script = self.parent_script,
            model_nickname = self.model_nickname,
            param_config_file = os.path.basename(self.config_file),
            model_param_dict = self.param_dict,
            training_param_dict = training_param_dict,
            training_metrics = training_metrics
        )
        with self.db_connection.engine().connect() as conn:
            result = conn.execute(insert)
        return result

    def log_results(self):
        """"""
        pass


