from websocket import create_connection
import re

if __name__ == "__main__":

    ws = create_connection("wss://data.test.meituan.com/channel/chat/1")
    s = "{'userId': 1, 'agentId': 'ailong', 'type': 'text',  'content': '详细介绍你自己', 'userName': '123'}"
    ws.send(s)
    print("Sent")
    print("Receiving...")
    result = ws.recv()
    pattern = r"WebResponse\(status=(\d+), message=(.*), data=(.*), traceId=(.*)\)"
    match = re.match(pattern, result)
    if match:
        status = match.group(1)
        message = match.group(2)
        data = match.group(3)
        traceId = match.group(4)
        print(f"status: {status}, message: {message}, data: {data}, traceId: {traceId}")

    while True:
        print("Receiving...")
        result = ws.recv()
        print("Received '%s'" % result)
    ws.close()
