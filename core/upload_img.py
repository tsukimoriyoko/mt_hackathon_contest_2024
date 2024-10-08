import requests

def uploadImage(filePath):
    with open(filePath, 'rb') as file:
        url = 'https://data.test.meituan.com/pc/v1/screenshot/upload'
        headers = {
            'Accept': 'application/json'
        }
        files = { 'file': file }
        data = {
            # 'file': ('chat.png', open(file_path, 'rb'), 'image/png'),
            'type': 'png',
            'userId': 'ailong1',
            'agentId': 'ailong',
        }

        response = requests.post(url, data=data, files=files, headers=headers)

        if response.status_code == 200:
            print('File uploaded successfully', response.text)
        else:
            print(f'Failed to upload file. Status code: {response.status_code}')

file_path = "D:\\repos\\desktop-pet\\img\\chat.png"

with open(file_path, 'rb') as file:
    # file_content = file.read()

    url = 'https://data.test.meituan.com/pc/v1/screenshot/upload'
    headers = {
        'Accept': 'application/json'
    }
    files = { 'file': file }
    data = {
        # 'file': ('chat.png', open(file_path, 'rb'), 'image/png'),
        'type': 'png',
        'userId': 'ailong1',
        'agentId': 'ailong',
    }

    response = requests.post(url, data=data, files=files, headers=headers)

    if response.status_code == 200:
        print('File uploaded successfully', response.text)
    else:
        print(f'Failed to upload file. Status code: {response.status_code}')

# curl --location 'https://data.test.meituan.com/pc/v1/screenshot/upload' --header 'Accept: application/json' --header 'Content-Type: multipart/form-data' --form 'file=@"D:\\repos\\desktop-pet\\img\\chat.png"' --form 'type="png"' --form 'agentId="ailong"' --form 'userId="1"'