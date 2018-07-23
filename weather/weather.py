import json
import requests
import geocoder
import argparse


class Weatherman:
    def __init__(self, units_in):
        self.units = units_in
        self.searchQuery = False
        self.connectionTries = 5

    def validateInput(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         description='Deciding what to wear is a daily struggle and '
                                                     'Weatherman helps you out with that.'
                                                     '\nWeatherman detects your location and tells you '
                                                     'what to wear based on the weather.')
        parser.add_argument('-s', '--search',
                            metavar='"<city name>"',
                            help='Weatherman searches for the city you entered '
                                 'and tells residents of that city what to wear')
        parser.add_argument('-u', '--units',
                            choices=['C', 'F'],
                            help='Gives you output in Celsius or Fahrenheit depending on the option you provided '
                                 '(default is Celsius)')
        args = parser.parse_args()
        if args.units:
            self.units = args.units
        if args.search:
            self.searchQuery = args.search

    def readData(self):
        if not self.searchQuery:
            # get latitude and longitude from IP Address
            g = geocoder.ip('me')
            latlon = g.latlng
        else:
            # get latitude and longitude from search query
            latlon = self.getSearchQuery()
        self.latitude = latlon[0]
        self.longitude = latlon[1]
        # parse json data from API
        queryLocation = "https://www.metaweather.com/api/location/search/?lattlong=" + \
                        str(self.latitude) + "," + str(self.longitude)
        locationData = requests.get(queryLocation).text
        jsonLocationData = json.loads(locationData)
        id = jsonLocationData[0]['woeid']
        cityName = jsonLocationData[0]['title']
        print("You are in:", cityName)
        queryID = "https://www.metaweather.com/api/location/" + str(id) + "/"
        idData = requests.get(queryID).text
        jsonIDData = json.loads(idData)
        self.currentTemp = jsonIDData['consolidated_weather'][0]['the_temp']

        if self.units == 'F':
            self.outputTemp = self.convertToFarenheit(self.currentTemp)
        else:
            self.outputTemp = self.currentTemp
        # round to 2 decimal places
        self.outputTemp = round(self.outputTemp, 2)

    def printOutput(self):
        # output what clothes to wear based on weather
        if self.currentTemp > 30:
            print("Bring a cap! Temperature is:", self.outputTemp, self.units)
        elif self.currentTemp > 20:
            print("Wear T-Shirt and Shorts. Temperature is:", self.outputTemp, self.units)
        elif self.currentTemp > 10:
            print("Wear a light jacket. Temperature is:", self.outputTemp, self.units)
        elif self.currentTemp > 0:
            print("Wear a thick jacket. Temperature is:", self.outputTemp, self.units)
        elif self.currentTemp > -10:
            print("Wear multiple layers. Temperature is:", self.outputTemp, self.units)
        elif self.currentTemp > -20:
            print("Wear a parka. Temperature is:", self.outputTemp, self.units)
        else:
            print("You shouldn't be outside. Temperature is:", self.outputTemp, self.units)

    # helper functions
    def convertToFarenheit(self, currentTemp):
        self.convertedTemp = currentTemp * 9 / 5 + 32
        return round(self.convertedTemp, 2)

    def getSearchQuery(self):
        try:
            # try to search 3 times
            for attempt in range(self.connectionTries):
                latlon = geocoder.google(self.searchQuery).southwest
                if latlon:
                    return latlon
            raise TypeError
        except TypeError:
            print("Invalid search query")
            exit(1)


# default is Celsius mode
myWeatherman = Weatherman('C')

myWeatherman.validateInput()
myWeatherman.readData()
myWeatherman.printOutput()
