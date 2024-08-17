class TextHandler():
    

    def getProcessedText(self, text):
        """
            Preprocess text data
            Args:
                text -> unprocessed texts data
            
            returns:
                pre-process text data
        """
        pass

    

    

    def sendResponse(self, args, sidReqContext, socContext, eventContext):
        """
            Process text coming from client and make it compatible to be used with next function in the chain
            
            Args: 
                args -> text data and user id
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

       
        socContext.emit("adsOut", {'message': args.text, 'id': args.id}, room=sidReqContext)