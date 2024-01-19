import cloudscraper

def get_url(link, return_content_response=False):
    scraper = cloudscraper.create_scraper()
    _request = scraper.get(link)
    if return_content_response:
        return (_request.status_code, _request.content)
    return (_request.status_code, _request.text)
