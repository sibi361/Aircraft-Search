import random


def get_fun_fact():
    # Fun Facts adapted from https://www.flightcentre.com.au/
    fun_facts = ["KLM Royal Dutch Airlines is the world's oldest airline, established in 1919.",
                 "In 1987 American Airlines saved $40,000 by removing one olive from each salad served in first class.",
                 "An aircraft takes off or lands every 37 seconds at Chicago O’Hare International Airport.",
                 "The wing-span of the Airbus A380 is longer than the aircraft itself. Wingspan is 80m, the length is 72.7m",
                 "Singapore Airlines spends approximately $700 million on food every year and $16 million on wine.",
                 "Travelling by air can shed up to 1.5 litres of water from the body during an average 3-hour flight.",
                 "German airline Lufthansa is the world's largest purchaser of caviar, buying over 10 tons per year.",
                 "The Boeing 747 wing-span (195 ft) is longer than the Wright Brothers' entire first flight (120 ft).",
                 "The winglets on an Airbus A330-200 are the same height as the world's tallest man (2.4m).",
                 "The Boeing 747 family has flown more than 5.6 billion people - equivalent to 80% of the world's population.",
                 "The average Boeing 747 has a whopping 240-280 kilometres of electrical wiring",
                 "In the USA, over two million passengers board over 30,000 flights each day."]

    return random.choice(fun_facts)


if __name__ == "__main__":
    print("Aviation fun fact:\n{}".format(get_fun_fact()))
