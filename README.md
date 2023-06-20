# Aircraft Search

Aircraft details provider that queries multiple sources to find and display information about a given aircraft using any one of the following inputs:

- Flight number (present on the boarding pass)
- Aircraft registration number
- Aircraft image (will be [OCR](https://en.wikipedia.org/wiki/Optical_character_recognition)d and then queried)

## Features

The script returns the following information:

- Details about the aircraft such as Manufacturer, Engines, First flight etc.
- Image of the aircraft obtained from the [planespotters.net](https://www.planespotters.net/photo/api) API
- Recent past flights of the aircraft

There are four available versions:

- `aircraft_search` python library
- Web API made with [FastAPI](https://github.com/tiangolo/fastapi/)
- HTML Web interface (Currently in progess)
- Web interface made with [Streamlit](https://github.com/streamlit/streamlit)

  Streamlit URL: https://aircraft-search.streamlit.app

## Requirements

Python 3.7+

- [FastAPI](https://github.com/tiangolo/fastapi/)
- [Streamlit](https://github.com/streamlit/streamlit)

## Installation

```
git clone https://github.com/04ac/Aircraft-Search.git
cd Aircraft-Search
pip install -r requirements.txt
```

## Usage

#### - Base scraper module

```
import aircraft_search

aircraft_reg_no = "N145DQ"  # example aircraft registration number

searcher = aircraft_search.aircraft_searcher(logging=True, json_response=False)

aircraft_data = searcher.aircraft_details_query(aircraft_reg_no)

print(aircraft_data)
```

Please view [`example_module.py`](example_module.py) for more examples.

#### - API + HTML Web interface

```
uvicorn api:app
```

Visit http://127.0.0.1:8000 in a browser to view the web interface

Available endpoint(s):

- `/query?regno=<input aircraft reg number here>` Request type: GET/POST

#### - Streamlit Web Interface

```
streamlit run streamlit_web_interface.py
```

## Todo

- [x] Enable searching for an aircraft using Flight Number
- [ ] API: Enable sending image object as a POST request to `/queryByImage` so that users can search using aircraft / flight ticket's image
- [ ] API: Switch to `APIRouter`
- [ ] Web interface: Make a web app using the API as backend with features:
  - [ ] Query multiple reg numbers / flight numbers in parallel with JS
  - [x] Show aviation related fun facts while the backend API fetches the results
- Pool all possible requests and parallelly run them with `grequests` and then parse them
- [ ] OCR: Switch to a faster OCR engine
- [ ] OCR: Flight ticket Flight Number -> Query
- [ ] Package aircraft_search as pip package
- [ ] Make a GUI using [ttkbootstrap](https://ttkbootstrap.readthedocs.io/en/latest/)
- [ ] Add logo image with badges to README.md
- [ ] Find and give credit to owners of test images
- [ ] Add argument passing functionality

## License

This project is licensed under the terms of the [MIT License](LICENSE).

> Parent repository: [04ac/Aircraft-Search](https://github.com/04ac/Aircraft-Search)
