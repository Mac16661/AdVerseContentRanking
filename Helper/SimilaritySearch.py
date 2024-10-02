import os
import json
from pymongo import MongoClient
from bson import json_util
from dotenv import load_dotenv
from functools import lru_cache
from .TextToEmbeddings import TextToEmbeddings
load_dotenv()

@lru_cache(maxsize=1)
class SimilaritySearch():
    def __init__(self):
        mongodb = os.getenv("MONGODB_URI")
        client = MongoClient(mongodb)
        db = client['testDB']
        self.ad_collection = db['ads']
        print("Initialized Similarity Search(Mongo) ========================================\n")

    def query_db(self, vector):
        try:
            results = self.ad_collection.aggregate([
                {
                    "$search": {
                        "index": "AdSearch",  
                        "knnBeta": {
                            "vector": vector,
                            "path": "embedding",
                            "k": 3
                        }
                    }
                },
                {
                    "$match": {"available_balance": {"$gt": 0.01}}  
                },
                {
                    "$project": {
                        "score": {"$meta": "searchScore"},
                        "document": "$$ROOT"
                    }
                }
            ])
                
            return list(results)
        except Exception as e:
            print(f"Err during vector search: {str(e)}")
        
        return []
    
    def stage2(self, product_list):
        retrieved_items = []
        for i in product_list:
            # Convert it to embeddings
            product_embedding = TextToEmbeddings().getEmbedding(i)

            # perform db query
            result = self.query_db(product_embedding[0])
            
            # return id, image and name
            retrieved_items.append(result)

        # BSON to json VERY IMP
        return json.loads(json_util.dumps(retrieved_items))