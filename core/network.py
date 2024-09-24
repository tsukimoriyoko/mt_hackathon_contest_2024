from PyQt5 import QtCore, QtNetwork
from websocket import create_connection
import re

class Net:
    def __init__(self):
        print("")

    def doRequest(self):
        url = "https://data.test.meituan.com"
        query = QtCore.QUrlQuery()
        query.addQueryItem("param1", "value1")
        query.addQueryItem("param2", "value2")
        url.setQuery(query)
        req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.handleResponse)
        self.nam.get(req)

    def handleResponse(self, reply):
        er = reply.error()
        if er == QtNetwork.QNetworkReply.NoError:
            bytes_string = reply.readAll()
            print(str(bytes_string, 'utf-8'))
        else:
            print("Error occurred: ", er)
            print(reply.errorString())
