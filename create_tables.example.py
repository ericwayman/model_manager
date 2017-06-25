from model_manager import PSQLConn
from tables import metadata
import os

cred = PSQLConn(db='ewayman',
                user=os.getenv("DATABASE_USER"),
                password=os.getenv("DATABASE_PASSWORD"),
                host=os.getenv("DATABASE_HOST"),
                port=os.getenv("DATABASE_PORT")
                )

if __name__ == "__main__":
    engine = cred.engine()
    metadata.create_all(engine)