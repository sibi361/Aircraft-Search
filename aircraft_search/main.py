import re
import cv2
import json
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import PIL
import easyocr

try:
    from components import browser, fun_facts, OCR
except:
    from .components import browser, fun_facts, OCR


class aircraft_searcher():
    def __init__(self, logging=False, show_image=False, json_response=True):
        global log
        log = logging
        self.show_image = show_image
        self.json_response = json_response

        self.aircraft_data = {"success": True,
                              "aircraft_image_link": "", "data": []}
        self.aircraft_data_index = -1

    def aircraft_details_query(self, reg_no):
        self.reg_no = reg_no

        if self.reg_no == "":
            del self.aircraft_data["data"]
            self.aircraft_data["success"] = False
            self.aircraft_data["message"] = "Aircraft registration number must not be blank"
            return self.aircraft_data
        self.reg_no = self.reg_no.upper().strip().replace(" ", "")

        _print("\nAviation fun fact: {}\n".format(fun_facts.get_fun_fact()))

        _print("Details for {}:".format(self.reg_no))

        _image_error = 0
        req = browser.get_url(
            "https://api.planespotters.net/pub/photos/reg/", self.reg_no)
        if req[0] < 300:
            data = json.loads(req[1])
            if not len(data["photos"]) == 0:
                src = data["photos"][0]["thumbnail_large"]["src"]
                self.aircraft_data["aircraft_image_link"] = src
                req = browser.get_url(src, return_content_response=True)
                if req[0] < 300:
                    with open("_most_recent_aircraft_image.png", "wb") as file:
                        file.write(req[1])
                    _print(
                        "Aircraft's image saved at ./_most_recent_aircraft_image.png")
                    img = PIL.Image.open("_most_recent_aircraft_image.png")
                    if self.show_image:
                        img.show()
                else:
                    _image_error = True
            else:
                _image_error = True
        if _image_error:
            _print("Aircraft's image not available")

        _print("\n===========================================================\n\
    Querying flightaware.com...")
        # Source1: flightaware.com
        req = browser.get_url(
            "https://flightaware.com/resources/registration/", self.reg_no)

        if req[0] < 300:
            data_from_source1 = {}
            soup = BeautifulSoup(req[1], "lxml")
            info = soup.find("div", class_="pageContainer")
            data = info.findAll("div", class_="attribute-row")
            for i in data:
                data_from_source1[i.find("div", class_="medium-1 columns title-text").text] = remove_delimiters(
                    i.find("div", class_="medium-3 columns").text.replace("\n", " "))
            if len(data_from_source1.items()) > 1:
                engine = data_from_source1["Engine"]
                data_from_source1["Engine"] = engine[:engine.find(
                    "Thrust")] + " " + engine[engine.find("Thrust") + 8:] + " thrust"
                source1_df = pd.DataFrame(data_from_source1.items()).rename(
                    columns={0: "Parameter", 1: "Value"}).set_index("Parameter")
                source1_json = json.loads(
                    source1_df.to_json())
                _print(source1_df)
                # _print(json.dumps(source1_json, indent=4))
                self.aircraft_data_index += 1
                self.aircraft_data["data"].append(
                    source1_json["Value"])
                self.aircraft_data["data"][self.aircraft_data_index]["source"] = "https://flightaware.com/resources/registration/"
            else:
                _print("Data not available")

            soup.find("div", class_="airportBoardContainer")
            data = info.find("table")
            try:
                aircraft_owners_df = pd.read_html(
                    str(data))[0].set_index("Date")
                _print(aircraft_owners_df)
                aircraft_owners_json = json.loads(
                    aircraft_owners_df.to_json(orient="records"))
                # _print(json.dumps(aircraft_owners_json, indent=4))
                _print("\nAircraft Owners:")
                _print(aircraft_owners_json)

                self.aircraft_data["data"][self.aircraft_data_index]["Aircraft Owners"] = aircraft_owners_json
                # _print(json.dumps(self.aircraft_data, indent=4))
            except ValueError:
                pass
        else:
            _print("Data not available")

        _print("\n===========================================================\n\
    Querying flightera.net...")
        # Source 2: flightera.net
        req = browser.get_url(
            "https://www.flightera.net/en/planes/", self.reg_no)
        if req[0] < 300:
            html = req[1]
            soup = BeautifulSoup(html, "lxml")
            info = soup.find("div", class_="mx-auto flex max-w-7xl")
            f = info.find(
                "div", class_="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8")
            i = info.find(
                "dl", class_="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2 lg:grid-cols-3")
            # there are two tables, we need to merge them
            j = i.findAll("table")
            source2_df = pd.read_html(str(j[0]), index_col=0)[
                0].rename(columns={0: "Parameter", 1: "Value"})
            try:
                details_flightera_df_2 = pd.read_html(str(j[1]), index_col=0)[
                    0].rename(columns={0: "Parameter", 1: "Value"})
                source2_df = pd.concat(
                    [source2_df, details_flightera_df_2])
            except:
                pass
            _print(source2_df)
            source2_json = json.loads(
                source2_df.to_json())
            # _print(json.dumps(source2_json, indent=4))
            self.aircraft_data_index += 1
            self.aircraft_data["data"].append(source2_json["Value"])
            self.aircraft_data["data"][self.aircraft_data_index]["source"] = "https://www.flightera.net/en/planes/"

            tables = pd.read_html(html)
            if len(tables) < 3:
                _print("No past flights found")
            else:
                # Drop last column
                past_flights = tables[2].iloc[:, :-1]

                if "TO" in past_flights.keys().tolist():
                    i = 0
                    # Clean up data in "FROM" column
                    for item in past_flights["FROM"]:
                        l = []
                        for le in item:
                            l.append(le)
                            if le == ")":
                                break
                        past_flights["FROM"][i] = "".join(l)
                        i += 1

                    i = 0
                    # Clean up data in "TO" column
                    for item in past_flights["TO"]:
                        l = []
                        for le in item:
                            l.append(le)
                            if le == ")":
                                break
                        past_flights["TO"][i] = "".join(l)
                        i += 1
                    _print("Past Flights:")
                    _print(past_flights)
                    past_flights_json = json.loads(
                        past_flights.to_json(orient="records"))
                    # most_freq_airports_df.to_json)
                    # _print(json.dumps(past_flights_json, indent=4))
                    self.aircraft_data["data"][self.aircraft_data_index]["Past Flights"] = past_flights_json
                else:
                    _print("No past flights found")

            try:
                info = soup.find("table", {"id": "apt-ranking"})
                most_freq_airports_df = pd.read_html(str(info), index_col=0)[
                    0].iloc[:, :2]
                _print("\nMost Frequented Airports:")
                _print(most_freq_airports_df)
                most_freq_airports_json = json.loads(
                    most_freq_airports_df.to_json(orient="index"))
                # _print(json.dumps(most_freq_airports_json, indent=4))
                self.aircraft_data["data"][self.aircraft_data_index]["Most Frequent Airports"] = most_freq_airports_json
            except ValueError:
                pass
            # _print(json.dumps(self.aircraft_data, indent=4))
        else:
            _print("Data not available")

        if len(self.aircraft_data["data"]) == 0:
            del self.aircraft_data["data"]
            self.aircraft_data["success"] = False
            self.aircraft_data["message"] = "Data not available from any source"

        if self.json_response is True:
            return self.aircraft_data
        return json.loads(json.dumps({"success": True, "message": "No data returned as json_response is set to False"}))


def remove_delimiters(word):
    _ = []
    for i in word:
        if i != "\n" and i != "\t":
            _.append(i)
    return "".join(_)


def _print(to_print):
    try:
        if log is True:
            print(to_print)
    except NameError:
        pass


# kept for debugging
if __name__ == "__main__":
    _print("Aircraft Search\n")

    # aircraft_code = input("Enter aircraft registration number:").upper().strip()
    aircraft_code = "N145DQ"

    searcher = aircraft_searcher(
        logging=True, show_image=False, json_response=False)

    searcher.aircraft_details_query(aircraft_code)

    # searcher.aircraft_details_query(aircraft_code, logging=True)
