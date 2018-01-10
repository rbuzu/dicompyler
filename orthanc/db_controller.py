import requests

class OrthancDB:

    def __init__(self, host, port):
        self.addr = host + port
        self.host = host
        self.port = port

    def retreive_patients(self):
        URL = self.addr + '/patients'
        return requests.get(URL)


def create_db_connection(host, port):
    return OrthancDB(host, port)
