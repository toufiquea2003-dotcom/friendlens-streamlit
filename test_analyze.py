import requests

# Upload first
url_upload = 'http://127.0.0.1:8000/api/upload'
files = {'file': open('test.csv', 'rb')}
response_upload = requests.post(url_upload, files=files, auth=('FriendLens1', '12345678'))
print('Upload Status:', response_upload.status_code)

# Test analyze endpoint with different tasks
tasks = [
    'give me a summary of the data',
    'recommend friends for Alice',
    'create a visualization',
    'count the users'
]

for task in tasks:
    url_analyze = 'http://127.0.0.1:8000/api/analyze'
    response = requests.post(url_analyze, data={'task': task}, auth=('FriendLens1', '12345678'))
    print(f'\nTask: "{task}"')
    print('Status:', response.status_code)
    if response.status_code == 200:
        result = response.json()
        print('Result:', result['result'])
    else:
        print('Error:', response.text)
