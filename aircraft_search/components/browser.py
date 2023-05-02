import requests


def get_url(site_link, regno=None, return_content_response=False):

    if regno == None:
        _request = requests.get(site_link)
    else:
        _request = requests.get(site_link + regno)
    if return_content_response:
        return (_request.status_code, _request.content)
    return (_request.status_code, _request.text)
