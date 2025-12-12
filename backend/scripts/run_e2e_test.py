import requests
import os

BACKEND = os.getenv('BACKEND_URL','http://127.0.0.1:8000')
PDF_PATH = os.path.join(os.path.dirname(__file__),'tmp','test_chunk.pdf')

print('Backend URL:', BACKEND)

# Step 1: upload/process full pipeline
with open(PDF_PATH,'rb') as f:
    files = {'file': ('test_chunk.pdf', f, 'application/pdf')}
    print('Uploading PDF to /process-pdf-full ...')
    resp = requests.post(f'{BACKEND}/process-pdf-full', files=files, params={'chunk_size':512,'overlap':50})
    print('Status code:', resp.status_code)
    try:
        print('Response JSON:', resp.json())
    except Exception:
        print('Response text:', resp.text)

# Step 2: ask a question
query = 'What is this document about?'
print('\nAsking question:', query)
resp2 = requests.post(f'{BACKEND}/answer', json={'query': query, 'top_k': 5})
print('Status code:', resp2.status_code)
try:
    print('Response JSON:', resp2.json())
except Exception:
    print('Response text:', resp2.text)
