#table definitions for the model_manager

from sqlalchemy import (MetaData,
Table, Column, Integer, DateTime, Interval, Text, JSON,
ForeignKey,Numeric,PicklType


SCHEMA = 'temp'
metadata = MetaData()
#model master list
#how does this relate to model_architecture_list
#decisions to make
#does it make sense to have a table just listing model architectures,
#or do we want a table listing model_architectures, model_architecture params

#somewhere we need a list of model_architecture, model_architecture_params,
#(version number: how many times has a given model_architecture,model_params pair been used)
#is this necessary or are the model_architecture_list, model_training table sufficient
#model_training table can contain more meta data-
#specific on training time, metrics on the validation set, loss function used, etc
#the model_master_list should just be a long table with an entry to join to the training tables
model_master_list = Table('model_master_list',metadata,
        Column('model_id',Integer,primary_key=True),
        #A model is uniquely defined by it's architecture file, model_architecture_params,
        #training params and training data set
        #this could be more complicated than a simple triple for the training set 
        #if a model is created by loading a parent model and training on a new set of data.
        #creating a model should be reproducible by following its ancestory chain.
        Column('model_architecture_id',Integer),
        Column('model_architecture_param_dict',JSON),
        Column('training_param_dict',JSON),
        Column('training_log_id',Integer), #foreign key to join to a unique entry in model_training table #for training meta data
        Column('time_created',DateTime),
        Column('model_architecture_script',Text),
        Column('parent_model_id',Integer),#if trained from loading a previous parent model. otherwise null.
        #??Column('child_model_ids') list?
        schema=SCHEMA
    )

#contains a record of all model architectures.
model_architecture_list = Table('model_architecture_list',metadata,
        Column('model_architecture_id',Integer,primary_key=True),
        Column('time_upload',DateTime),
        Column('model_architecture_file',Text),
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
