class TextHandler():
    def contentRanking(self, contents):
        """
            Rank contents from the set of similar contents
            Args:   
                content -> list of similar contents
            
            returns:
                list of contents
        """

    def getProcessedText(self, text):
        """
            Preprocess text data
            Args:
                text -> unprocessed texts data
            
            returns:
                pre-process text data
        """
        pass

    def textToEmbeddings(self, text):
        """
            Convert text data into vector embeddings 
            Args:
                text -> text from speech data

            returns:
                vector embeddings
        """
        pass

    def similaritySearch(self, embeddings):
        """
            Search for vector embedding in vector DB
            Args:
                embeddings -> embedding of text data
            
            returns:
                similar content related to embeddings
        """
        pass

    def sendResponse(self, args, sidReqContext, socContext, eventContext):
        """
            Process audio coming from client and make it compatible to be used with speech to text model
            
            Args: 
                args -> audio data
                sid -> socket id(to identify user)
                soc -> socket instance(to avoid out of context issue)
        """

        print(f"processing chunk from user -> {sidReqContext} ")

        """
            Steps->
                get text prediction 
                get text embeddings
                perform similarity search
                rank contents
                return ads as response 
        """

        # Simulating delay
        for i in range(200):
            eventContext.sleep(3)
            # Using context of socket
            socContext.emit("adsOut", {'message': i, 'id': args}, room=sidReqContext)