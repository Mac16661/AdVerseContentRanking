import os
import time
from groq import Groq
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()

@lru_cache(maxsize=1)
class LLMContentRanking():
    # Singleton class
    def __init__ (self):
        self.client = Groq(api_key=os.getenv("GROQ_CLOUD"))

    def contentRanking(self, contents, text_req, eventContext):
        """
            Rank contents from the set of similar contents
            Args:   
                content -> list of similar contents
            
            returns:
                list of contents
        """
        system_query = ""
        for idx,i in enumerate(contents):
            system_query = system_query + f"{idx}. {i} "

        system_query = system_query + f"{len(contents)}. None of the above"

        # This will be passed on to the llm
        user_query = f"recommend only all the relevant products in this context: {text_req}.VERY IMP: `Specify the options number Only`. example output formate: [options] or [options,options]."


        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_query
                },
                {
                    "role": "user",
                    "content": user_query,
                },
            ],
            model="llama3-8b-8192",
        )

        eventContext.sleep(2) # rate limiting the api call
        return chat_completion.choices[0].message.content
        
        