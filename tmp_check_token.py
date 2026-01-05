import urllib.request
url='http://127.0.0.1:8000/token/eAPzeiykelkJacgethKyijR-TkBkjjL-5WuhNhqIbLw'
try:
    r=urllib.request.urlopen(url, timeout=5)
    print(r.status)
    print(r.read().decode())
except Exception as e:
    print('ERROR', e)
