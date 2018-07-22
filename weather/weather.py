import json
import requests
import sys
import geocoder
import getopt


class Weatherman:
    def __init__(self, units_in):
        self.units = units_in
        self.searchMode = False
        self.connectionTries = 3

    def validateInput(self):
        opts, remainder = getopt.getopt(sys.argv[1:], "u:s:h",
                                        ["units=", "search=", "help"])
        for opt, arg in opts:
            if opt in ('-u', '--units'):
                self.units = arg
            elif opt in ('-s', '--search'):
                self.searchMode = True
                self.searchQuery = arg
            elif opt in ('-h', '--help'):
                print("To be filled in later")
                exit(0)

    def readData(self):
        if not self.searchMode:
            g = geocoder.ip('me')
            latlon = g.latlng
        else:
            latlon = self.getSearchQuery()

        self.latitude = latlon[0]
        self.longitude = latlon[1]
        queryLocation = "https://www.metaweather.com/api/location/search/?lattlong=" + \
                        str(self.latitude) + "," + str(self.longitude)
        locationData = requests.get(queryLocation).text
        jsonLocationData = json.loads(locationData)
        id = jsonLocationData[0]['woeid']
        cityName = jsonLocationData[0]['title']
        print("You are in:", cityName)
        queryData = "https://www.metaweather.com/api/location/" + str(id) + "/"
        data = requests.get(queryData).text

        jsonData = json.loads(data)

        self.currentTemp = jsonData['consolidated_weather'][0]['the_temp']
       	 
        if self.units == 'F':
            self.outputTemp = self.convertToFarenheit(self.currentTemp)
        else:
          self.outputTemp = self.currentTemp
        self.outputTemp = round(self.outputTemp, 2)

    def printOutput(self):
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
