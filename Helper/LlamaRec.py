import os
import time
from groq import Groq
from dotenv import load_dotenv
from functools import lru_cache
from langchain_groq import ChatGroq

load_dotenv()

# @lru_cache(maxsize=1)
# class LLMContentRanking():
#     # Singleton class
#     def __init__ (self):
#         self.client = Groq(api_key=os.getenv("GROQ_CLOUD"))

#     def contentRanking(self, contents, text_req, eventContext):
#         """
#             Rank contents from the set of similar contents
#             Args:   
#                 content -> list of similar contents
            
#             returns:
#                 list of contents
#         """
#         system_query = ""
#         for idx,i in enumerate(contents):
#             system_query = system_query + f"{idx}. {i} "

#         system_query = system_query + f"{len(contents)}. None of the above"

#         # This will be passed on to the llm
#         user_query = f"recommend only all the relevant products in this context: {text_req}.VERY IMP: `Specify the options number Only`. example output formate: [options] or [options,options]."


#         chat_completion = self.client.chat.completions.create(
#             messages=[
#                 {
#                     "role": "system",
#                     "content": system_query
#                 },
#                 {
#                     "role": "user",
#                     "content": user_query,
#                 },
#             ],
#             model="llama3-8b-8192",
#         )

#         eventContext.sleep(2) # rate limiting the api call
#         return chat_completion.choices[0].message.content
        

@lru_cache(maxsize=1)
class LLMContentRanking():
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=os.getenv("GROQ_CLOUD"), 
            model_name="llama-3.1-70b-versatile"
    )
        
    # STAGE 1 [User intrests based on context]
    def firstStage(self, customer_data):
        customer_data = "I like softdrinks"

        promp_ph1 = """
            CUSTOMER Feedback:
            It is cold inside
            INSTRUCTION:
            Return a JSON object with a single key products containing an array of recommended products based on customer data. Omit any additional text or keys. The output should be a valid JSON string in the exact format below:
            {"products":["product 1", "product 2", ... , "product n"]}
            RESPONSE(NO PREAMBLE):
            """

        response = self.llm.invoke(promp_ph1)

        print(response.content)
        # TODO: Should convert string to JSON and return
        return response.content
    
    # Similarity Search[Searching relevant items from DB]
    def secondStage(self, predicted_products):
        # TODO: Interact with VECTOR DB to fetch all similar the ads
        pass 

    # Ranking Retrieved Ads
    def thirdStage(self, retrieved_item):
        prompt_ph2 = """
            INSTRUCTION:
            Filter the predicted demand list: `Heater`, `Thermal Socks`, `Hot Chocolate`, `Electric Blanket` to return the most relevant product that matches the customer's demand `It is really cold inside`. If no relevant product exists, return an empty list. Exclude any unrelated products. The output should be a valid JSON string in the exact format below, without any additional text or keys:
            {"products":["product 1", "product 2", ... , "product n"]}
            RESPONSE(NO PREAMBLE):"""

        # print(promp_ph1)

        response = self.llm.invoke(prompt_ph2)
        print(response.content)
        # TODO: Should convert string to JSON and return
        return response.content