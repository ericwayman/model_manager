import os
from model_manager import ModelManager, ConnectionFactory
from time import sleep
from sklearn.feature_extraction.text import TfidfVectorizer
#model_params
CONFIG_FILE="/Users/ewayman/workspace/model_manager/config.json"
SCHEMA="temp"
MODEL_NICKNAME = 'mock_save_model'


conn_factory = ConnectionFactory(db=os.getenv('DATABASE_NAME'),
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
MODEL_PARAMS = p['model_params']

def initialize_tfidf(min_doc_freq,max_doc_freq,stop_words):
    tfidf = TfidfVectorizer(
        analyzer = u'word',
        lowercase='true',
        stop_words = stop_words,
        strip_accents = 'ascii',
        use_idf = True,
        min_df = min_doc_freq,
        max_df = max_doc_freq
    )
    return tfidf

if __name__ == "__main__":
    model_manager.compile()
    tfidf = initialize_tfidf(**MODEL_PARAMS)
    model_manager.save_serialized_model_to_db(object_to_save=tfidf,
                                            object_params=MODEL_PARAMS,
                                            object_name='mock_tfidf_vectorizer'
                                        )