import os
import time
import json
from .SimilaritySearch import SimilaritySearch
from dotenv import load_dotenv
from functools import lru_cache
from langchain_groq import ChatGroq

load_dotenv()

@lru_cache(maxsize=1)
class LLMContentRanking():
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=os.getenv("GROQ_CLOUD"), 
            model_name="llama-3.1-70b-versatile")
        print("Initialized Similarity Search(Mongo) ========================================\n")
        
    def stage1(self, customer_verdict):

        promp_ph1 =f"""CUSTOMER Feedback:\n{customer_verdict}\nINSTRUCTION:\nReturn a JSON object with a single key products containing an array of recommended products based on customer data. Omit any additional text or keys. The output should be a valid JSON string in the exact format below:\n{{"products":["product 1", "product 2", ... , "product n"]}}\nRESPONSE(NO PREAMBLE):"""

        response = self.llm.invoke(promp_ph1)
        try:
            json_data = json.loads(response.content)
            return json_data
        except:
            print("invalid json",response.content)
            return {"products": []}

    def stage3(self,str, customer_verdict):
        prompt = f"""INSTRUCTION:
        Filter the predicted demand list: {str} to return the most relevant product that matches the customer's demand {customer_verdict}. If no relevant product exists, return an empty list. Exclude any unrelated products. The output should be a valid JSON string in the exact format below, without any additional text or keys:
        {{"products":["product 1", "product 2", ... , "product n"]}}
        RESPONSE(NO PREAMBLE):
        """

    #     print("\n\n\n",prompt,"\n\n\n")

        response = self.llm.invoke(prompt)
        try:
    #         print(response.content)
            json_data =json.loads(response.content)
            return json_data
        except:
            print("invalid json ", response.content)
            return {"products": []}
        
        
    def LLamaRec(self, customer_verdict):
        print("Customer -> ", customer_verdict)
        # STAGE 1
        stage1_data = self.stage1(customer_verdict)
        print("Stage 1 -> ", stage1_data)
    #     TODO: Implement err handling
    #     if(len(stage1_data) == 0):
    #         return

        # STAGE 2
        stage2_data = SimilaritySearch().stage2(stage1_data["products"])

    #     Unique products  
        unique_elements = set()
        filtered_list = []
        for i in stage2_data:
            for j in i:
                filtered_data = (
                    ("id", j["document"]["_id"]["$oid"]),
                    ("name", j["document"]["name"]),
                    ("image", j["document"]["image"]),
                )
                if filtered_data not in unique_elements:
                    unique_elements.add(filtered_data)
                    filtered_list.append(dict(filtered_data))
                
        # Unique products names
        filtered_prod_name = ""
        for i in filtered_list:
            filtered_prod_name = filtered_prod_name + "`" + i['name'] + "`,"
        
        filtered_prod_name = filtered_prod_name[:len(filtered_prod_name)-2]
        
        print("Stage 2(Vector search) filtered - > ", filtered_prod_name)
        # STAGE 3
        final_products_name = self.stage3(filtered_prod_name, customer_verdict)
        final_products_list = []
        
        for i in filtered_list:
            if  i['name'] in final_products_name['products']:
                final_products_list.append(i)
        
        
        print("Stage(Ranking) 3 -> ", final_products_list)
        
        if len(final_products_list ) < 1:
            return filtered_list
        
        return final_products_list