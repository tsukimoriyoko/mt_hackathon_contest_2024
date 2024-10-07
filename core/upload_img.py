import requests

file_path = "D:\\repos\\desktop-pet\\img\\chat.png"

with open(file_path, 'rb') as file:
    file_content = file.read()

url = 'https://data.test.meituan.com/pc/v1/screenshot/upload'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'multipart/form-data'
}
data = {
    'name': 'img_1',
    'file': file_content,
    'type': 'png',
    'userId': 'ailong1',
    'agentId': 'ailong',
}

response = requests.post(url, data=data, headers=headers)

if response.status_code == 200:
    print('File uploaded successfully', response.text, response.content)
else:
    print(f'Failed to upload file. Status code: {response.status_code}')

# curl --location 'https://data.test.meituan.com/pc/v1/screenshot/upload' \
# --header 'Accept: application/json' \
# --header 'Content-Type: multipart/form-data' \
# --form 'file=@"D:\\repos\\desktop-pet\\img\\chat.png"' \
# --form 'type="png"' \
# --form 'userId=ailong1' \
# --form 'agentId=ailong'