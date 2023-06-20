import requests


def get_url(link, return_content_response=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    _request = requests.get(link, headers=headers)
    if return_content_response:
        return (_request.status_code, _request.content)
    return (_request.status_code, _request.text)
