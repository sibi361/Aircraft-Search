import aircraft_search

aircraft_reg_no = "N145DQ"  # example aircraft registration number

# Logging is disabled by default and hence the default response is JSON
# JSON response can be suppressed by setting json_response to False
searcher = aircraft_search.aircraft_searcher(logging=True, json_response=False)

# show_image enables showing the aircraft image in the default image viewer
# searcher = searcher.aircraft_search_class(logging=True, show_image=True, json_response=False)

# This is where the script actually queries the sources and presents the data
aircraft_data = searcher.aircraft_details_query(aircraft_reg_no)

print(aircraft_data)
