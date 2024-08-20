import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, asc
from tidb_vector.sqlalchemy import VectorType
from functools import lru_cache


load_dotenv()

Base = declarative_base()

class Ads(Base):
    __tablename__ = "AdsTable"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(125))
    image = Column(String(96))
    link = Column(String(487))
    main_category = Column(String(32))
    sub_category = Column(String(32))
    discount_price = Column(String(32))
    actual_price = Column(String(32))
    embedding = Column(VectorType(512,))
    comment="hnsw(distance=cosine)"


@lru_cache(maxsize=1)
class SimilaritySearch():
    def __init__ (self):
        self.TIDB_HOST = os.getenv("TIDB_HOST")
        self.TIDB_PORT = os.getenv("TIDB_PORT")
        self.TIDB_USER = os.getenv("TIDB_USER")
        self.TIDB_PASSWORD = os.getenv("TIDB_PASSWORD")
        self.TIDB_DB_NAME = os.getenv("TIDB_DB_NAME")
        self.CA_PATH = os.getenv("CA_PATH")

        self.engine = self.get_db_engine()
        self.Session = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def get_db_engine(self):
        connect_args={}
        if self.CA_PATH:
            connect_args = {
                "ssl_verify_cert": True,
                "ssl_verify_identity": True,
                "ssl_ca": self.CA_PATH,
            }
        return create_engine(
            URL.create(
                drivername="mysql+pymysql",
                username=self.TIDB_USER,
                password=self.TIDB_PASSWORD,
                host=self.TIDB_HOST,
                port=self.TIDB_PORT,
                database=self.TIDB_DB_NAME
            ),
            connect_args = connect_args,
        )

    def similaritySearch(self, embeddings):
        try:
            with self.Session() as session:
                results = session.query(
                    Ads,
                    Ads.embedding.cosine_distance(embeddings).label("distance"),
                ).order_by(
                    asc("distance")
                ).limit(9).all()
        except Exception as e:
            print("Conn lost")

        similarItems = []
        # print("-----------------------------------------------")
        for obj, d in results:
            # print(f"{d} -> {obj.name}")
            similarItems.append(obj)
        # print("-----------------------------------------------")


        return similarItems