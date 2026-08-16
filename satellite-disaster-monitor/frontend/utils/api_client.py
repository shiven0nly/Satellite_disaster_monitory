import requests

def check_backend_health(url='http://127.0.0.1:8000/health'):
    try:
        res = requests.get(url)
        return res.json()
    except Exception as e:
        return {'status': 'error', 'detail': str(e)}
