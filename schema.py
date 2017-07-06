#table definitions for the model_manager

from sqlalchemy import (MetaData,
Table, Column, Integer, DateTime, Interval, Text, JSON,
ForeignKey,Numeric,PicklType


SCHEMA = 'temp'
metadata = MetaData()
#model master list
model_master_list = Table('model_master_list',metadata,
        Column('model_id',Integer,primary_key=True),
        Column('time_created',DateTime),
        Column('initializing_script',Text),
        Column('model_param_dict',JSON),
        schema=SCHEMA
    )

model_training = Table('model_training',metadata,
    Column('model_id',Integer,ForeignKey(
        '{}.model_master_list.model_id'.format(SCHEMA),
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
schema=SCHEMA
)

model_results = Table('model_results',metadata,
    Column('model_id',Integer,ForeignKey(
        '{}.model_master_list.model_id'.format(SCHEMA),
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
        '{}.model_master_list.model_id'.format(SCHEMA),
        ondelete='CASCADE'
        )
    ),
    Column('object_name',Text),
    Column('object_params',JSON),
    Column('serialized_object',PickleType),
    Column('time_created',DateTime),
    Column('initializing_script',Text),
    schema=SCHEMA
)
