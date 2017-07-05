#table definitions for the model_manager

from sqlalchemy import (MetaData,
Table, Column, Integer, DateTime, Interval, Text, JSON,
ForeignKey,Numeric,PicklType


SCHEMA = 'temp'
metadata = MetaData()

models = Table('models',metadata,
    Column('model_id',Integer,primary_key=True),
    Column('time_stamp',DateTime),
    Column('time_to_run_script',Interval),
    Column('model_script',Text),
    Column('model_nick_name',Text),
    Column('model_param_dict',JSON),
Column('param_config_file',Text),
    schema=SCHEMA
)

model_results = Table('model_results',metadata,
    Column('model_id',Integer,ForeignKey(
        '{}.models.model_id'.format(SCHEMA),
        ondelete='CASCADE'
        )
    ),
    Column('data_point_id',Integer),
    Column('actual',Numeric),
    Column('prediction',Numeric),
    schema=SCHEMA
)

serialized_objects = Table('serialized_objects',metadata,
    Column('model_id',ForeignKey(
        '{}.models.model_id'.format(SCHEMA),
        ondelete='CASCADE'
        )
    ),
    Column('object_name',Text),
    Column('object_params',JSON),
    Column('serialized_object',PickleType),
    schema=SCHEMA
)