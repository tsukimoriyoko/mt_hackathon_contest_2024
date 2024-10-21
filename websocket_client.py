from websocket import create_connection
import json
if __name__ == "__main__":
   userId = 'zhangjun102_4'
   url = "wss://data.test.meituan.com/channel/chat/{}".format(userId)
#    url = "ws://localhost:8080/channel/chat/{}".format(userId)
   print("url: " + url)
   ws = create_connection(url)
   # result = ws.recv()
   # print("Received '%s'" % result)
   ws_input = {'userId': userId, 'agentId': 'ailong',  'content': '你好', 'userName': '123', "type": "heartbeat"}
   s = json.dumps(ws_input, ensure_ascii=False)
   ws.send(s)
   print("Receiving...")
   result = ws.recv()
   print("Received '%s'" % result)
   while True:
         text_input = input("用户输入: ")
         ws_input['content'] = text_input
         s = json.dumps(ws_input, ensure_ascii=False)
         ws.send(s)
         print("Receiving...")
         result = ws.recv()
         print("Received '%s'" % result)
   ws.close()
