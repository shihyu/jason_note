import time
from concurrent import futures

from nltk.corpus import stopwords

from nltk_service_pb2 import *
from nltk_service_pb2_grpc import *


class NltkService(KeywordServiceServicer):
    def __init__(self):
        self.stopwords = stopwords.words("english")
        self.trans_table = str.maketrans(
            "", "", '[]()-,|/\\"?:;&%$#@!%^.'
        )  # Remove these symbols from keywords

    def keywords(self, words):
        # We are removing all the stopwords and removing all other characters
        return [
            word.translate(self.trans_table)
            for word in words
            if word not in self.stopwords
        ]

    def GetKeywords(self, request, context):
        # Text we got from the client
        text = request.text.lower()
        print(text)
        text = text.replace("\n", "").replace("\r", "")
        words = text.split(" ")

        keywords = self.keywords(words)

        response = Response()
        response.keywords.extend(keywords)

        return response


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_KeywordServiceServicer_to_server(NltkService(), server)
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print("Listening on port {}..".format(port))
    try:
        while True:
            time.sleep(10000)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == "__main__":
    serve(6000)
