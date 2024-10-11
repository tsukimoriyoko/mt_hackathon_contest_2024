import requests
from PIL import Image
import time
import os
from core.conf import settings

def uploadImage(filePath):
    with Image.open(filePath) as img:
        # Save it with the specified quality and output path
        img.save(f"{filePath}.jpg", "JPEG", quality=60)
        # TODO 异步
        time.sleep(1)
        with open(f"{filePath}.jpg", 'rb') as file:
            url = 'https://data.test.meituan.com/pc/v1/screenshot/upload'
            headers = {
                'Accept': 'application/json'
            }
            files = { 'file': file }
            data = {
                'type': 'png',
                'userId': 'ailong1',
                'agentId': 'ailong',
            }

            response = requests.post(url, data=data, files=files, headers=headers)

            if response.status_code == 200:
                print('File uploaded successfully', response.text)
            else:
                print(f'Failed to upload file. Status code: {response.status_code}')

directory = settings.SETUP_DIR / "output"
for filename in os.listdir(directory):
    file_path = os.path.join(directory, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            os.rmdir(file_path)
    except Exception as e:
        print(f"Failed to delete {file_path}. Reason: {e}")