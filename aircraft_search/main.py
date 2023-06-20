import json
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
from PIL import Image

# try:
#     from components import browser, fun_facts, OCR
# except:
#     from .components import browser, fun_facts, OCR

try:
    from components import browser, fun_facts
except:
    from .components import browser, fun_facts


class aircraft_searcher():
    def __init__(self, logging=False, show_image=False, json_response=True):
        global log
        log = logging
        self.show_image = show_image
        self.json_response = json_response

        self.aircraft_data = {"success": True,
                              "aircraft_image_link": "", "data": []}
        self.aircraft_data_index = -1

    def aircraft_query_using_reg_no(self, reg_no):
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
            "https://api.planespotters.net/pub/photos/reg/{}".format(self.reg_no))
        if req[0] < 300:
            data = json.loads(req[1])
            if not len(data["photos"]) == 0:
                _aircraft_image_src = data["photos"][0]["thumbnail_large"]["src"]
                self.aircraft_data["aircraft_image_link"] = _aircraft_image_src
                req = browser.get_url(
                    _aircraft_image_src, return_content_response=True)
                if req[0] < 300:
                    with open("_most_recent_aircraft_image.png", "wb") as file:
                        file.write(req[1])
                    _print(
                        "Aircraft's image saved at ./_most_recent_aircraft_image.png")
                    img = Image.open("_most_recent_aircraft_image.png")
                    if self.show_image:
                        img.show()
                else:
                    _image_error = True
            else:
                _image_error = True
        if _image_error:
            _print("Aircraft's image not available")

        _print("\n=======================================\nQuerying Source 1...")
        # Source1: flightaware.com
        req = browser.get_url(
            "https://flightaware.com/resources/registration/{}".format(self.reg_no))

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

        _print("\n=======================================\nQuerying Source 2...")
        # Source 2: flightera.net
        req = browser.get_url(
            "https://www.flightera.net/en/planes/{}".format(self.reg_no))
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

    def aircraft_query_using_flight_no(self, flight_no):
        self.flight_number = flight_no.upper().strip().replace(" ", "").replace("-", "")

        status_code, html_text = browser.get_url(
            "https://www.flightera.net/en/flight/{}".format(self.flight_number))
        print("\n\n\n", self.flight_number)

        if status_code > 300:
            _print(status_code,
                   "Flight Number Information not available. Please enter a valid fight numnber.")
        else:
            soup = BeautifulSoup(html_text, "lxml")
            info = soup.find(
                "main", class_="flex-auto px-2 max-w-4xl mt-4 mx-auto")
            flight_number_info = info.find(
                "dt", class_="text-xl text-center leading-5 font-bold text-gray-800 dark:text-white")
            _print(flight_number_info.text.strip())

            flight_status = info.find(
                "dd", class_="text-center text-sm leading-5 text-gray-900 dark:text-white mt-6")
            _print(flight_status.text.strip())
            _print("---")

            origin_and_destination = info.findAll(
                "span", class_="text-lg font-medium")
            origin_name = origin_and_destination[0].text.strip()
            destination_name = origin_and_destination[1].text.strip()

            origin_airport_code_info = info.find(
                "dd", class_="text-left text-xs leading-5 text-gray-500 dark:text-white")
            code_string = remove_delimiters(
                origin_airport_code_info.text.strip())
            origin_airport_code = code_string[0:3] + "/" + code_string[-4:]

            destination_airport_code_info = info.find(
                "dd", class_="text-right text-xs leading-5 text-gray-500 dark:text-white")
            code_string = remove_delimiters(
                destination_airport_code_info.text.strip())
            destination_airport_code = code_string[0:3] + \
                "/" + code_string[-4:]

            flight_info = info.find(
                "div", class_="col-span-1 text-xs text-center text-gray-600 dark:text-white mt-6")
            flight_duration_info = flight_info.findAll(
                "span", class_="whitespace-nowrap")
            flight_duration = flight_duration_info[0].text.strip()
            flight_distance = flight_duration_info[1].text.strip()

            terminal_and_gate_origin = info.find(
                "dd", class_="text-left text-sm leading-5 text-gray-800 dark:text-white").text
            terminal_and_gate_destination = info.find(
                "dd", class_="text-right text-sm leading-5 text-gray-500 dark:text-white").text

            departure_info = info.find(
                "dt", class_="text-left text-md text-base leading-5 text-gray-800 dark:text-gray-100")
            departure = departure_info.find(
                "span", class_="whitespace-nowrap").text

            arrival_info = info.find(
                "dt", class_="text-right text-md text-base leading-5 text-gray-800 dark:text-gray-100")
            arrival = arrival_info.find(
                "span", class_="whitespace-nowrap").text

            _headings = info.findAll(
                "dt", class_="text-left text-sm leading-5 font-bold text-gray-500 dark:text-gray-300")
            plane_info_headings = []
            for i in _headings:
                plane_info_headings.append(i.text.strip())

            _headings = info.findAll(
                "dt", class_="text-right text-sm leading-5 font-bold text-gray-500 dark:text-gray-300")
            for k in _headings:
                plane_info_headings.append(k.text.strip())

            model_and_seat_config_info = info.findAll(
                "dd", class_="text-left text-sm leading-5 text-gray-500 dark:text-white")
            plane_info_items = []
            for i in model_and_seat_config_info:
                if i != None:
                    plane_info_items.append(i.text.strip())
                else:
                    plane_info_items.append("NA")

            icao_identifier = info.find(
                "dd", class_="text-right text-sm leading-5 text-gray-900 dark:text-white")
            if icao_identifier != None:
                plane_info_items.append(icao_identifier.text.strip())
            else:
                plane_info_items.append("NA")

            first_flight = info.findAll(
                "dd", class_="text-right text-sm leading-5 text-gray-500 dark:text-white")
            if len(first_flight) >= 2:
                plane_info_items.append(first_flight[1].text.strip())
            else:
                plane_info_items.append("NA")

            plane_info_items[0] = " ".join(plane_info_items[0].split())
            plane_info_items[3] = plane_info_items[3][0:8]

            plane_info_dict = dict(zip(plane_info_headings, plane_info_items))

            # col1, col2, col3 = st.columns(3)
            if 1:
                _print('<h2 style="text-align: left">'
                       + origin_name + "</h2>")
                _print('<h3 style="text-align: left">'
                       + origin_airport_code + "</h3>")
                _print('<h5 style="text-align: left">'
                       + terminal_and_gate_origin + "</h5>")
                _print('<h2 style="text-align: left">'
                       + departure + "</h2>")

            if 1:
                _print('<h5 style="text-align: center">Duration:  '
                       + flight_duration + "</h5>")
                _print('<h5 style="text-align: center">Distance:  '
                       + flight_distance + "</h5>")

            if 1:
                _print('<h2 style="text-align: right">'
                       + "To: " + destination_name + "</h2>")
                _print('<h3 style="text-align: right">'
                       + destination_airport_code + "</h3>")
                _print('<h5 style="text-align: right">'
                       + terminal_and_gate_destination + "</h5>")
                _print('<h2 style="text-align: right">'
                       + arrival + "</h2>")

            _print("---")
            frequency_info = info.find(
                "div", class_="col-span-1 text-left").find("dd")
            frequency = frequency_info.find("span").text
            _print('<h5 style="text-align: left">'
                   + "Frequency: " + frequency + "</h5>")
            days_running = frequency_info.text.strip()[len(frequency):].strip()
            _print('<h5 style="text-align: left">'
                   + days_running + "</h5>")

            _print("---")

            _print('< h2 > Aircraft Information: < /h2 >')

            # Gets registration of aircraft
            _ = []
            for c in plane_info_items[0]:
                if c == " ":
                    break
                _.append(c)
            reg_no = "".join(_)

            return reg_no


def remove_delimiters(word):
    _ = []
    for i in word:
        if i != "\n" and i != "\t":
            _.append(i)
    return "".join(_)


def _print(*args):
    try:
        if log is True:
            for i in args:
                print(i, end=" ")
            print()
    except NameError:
        pass


if __name__ == "__main__":
    _print("Aircraft Search\n")

    # flight_no = input("Enter flight number:").upper().strip()

    flight_no = "A i-4 41"

    searcher = aircraft_searcher(
        logging=True, show_image=False, json_response=False)

    print(searcher.aircraft_query_using_flight_no(flight_no))

    # searcher.aircraft_details_query(aircraft_code, logging=True)

# if __name__ == "__main__":
#     _print("Aircraft Search\n")

#     # aircraft_code = input("Enter aircraft registration number:").upper().strip()
#     aircraft_code = "N145DQ"

#     searcher = aircraft_searcher(
#         logging=True, show_image=False, json_response=False)

#     print(searcher.aircraft_query_using_reg_no(aircraft_code))

#     # searcher.aircraft_query_using_reg_no(aircraft_code, logging=True)
