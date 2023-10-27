from sqlalchemy import create_engine, engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

ssl_args = {
    "ssl_ca": "./lib/DigiCertGlobalRootCA.crt.pem"
}

pool = create_engine(
    engine.url.URL.create(
        drivername="mysql+pymysql",
        username="capstonedesign",
        password="CBNU201907602$",
        host="capstonedesign-db.mysql.database.azure.com",
        port="3306",
        database="barcode"
    ),
    connect_args=ssl_args
)

db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False, 
                                         bind=pool))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():    
    import models
    Base.metadata.create_all(bind=pool)