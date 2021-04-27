import csv
import requests
import json

class GeoCoding:

    def __init__(self):
        self.countries = {}
        self.locations = []
        self.loc_latlng = []

    def read_locations(self):

        with open('country.csv', mode='r') as csv_file :
            csv_reader = csv.reader(csv_file)
            i = 0
            for row in csv_reader:
                if i == 0:
                    i += 1
                    continue

                self.countries[row[0]] = row[1]

        with open('city.csv', mode='r') as csv_file :
            csv_reader = csv.reader(csv_file)
            i = 0
            for row in csv_reader :
                if i == 0 :
                    i += 1
                    continue

                if row[2] != '' :
                    loc = row[1] + ',' + row[2] + ',' + self.countries[row[3]]
                else :
                    loc = row[1] + ',' + self.countries[row[3]]
                self.locations.append(loc)

    def read_countries(self):
        with open('country.csv', mode='r') as csv_file :
            csv_reader = csv.reader(csv_file)
            i = 0
            for row in csv_reader:
                if i == 0:
                    i += 1
                    continue

                self.locations.append(row[1])
            pass

    def api_calls(self):

        for i in range(len(self.locations)):
            arr = []
            arr.append(self.locations[i])
            print(self.locations[i])

            resp = requests.get('http://www.mapquestapi.com/geocoding/v1/address?key=Yuas4vIjIpGr9hzAmY9HvvQBnPPOWbXP&location='+self.locations[i])
            if resp.status_code == 200:
                content_str = resp.content.decode('utf8')
                content = json.loads(content_str)
                latlong = content['results'][0]['locations'][0]['latLng']
                arr.append(latlong['lat'])
                arr.append(latlong['lng'])
            else:
                arr.append('')
                arr.append('')

            print(arr)
            self.loc_latlng.append(arr)

    def write_latlng_file(self):

        with open('country_lat_lng.csv', mode='w') as csv_file :
            for i in range(len(self.loc_latlng)):
                writer = csv.writer(csv_file)
                writer.writerow(self.loc_latlng[i])

if __name__=="__main__":
    g = GeoCoding()
    # g.read_locations()
    g.read_countries()
    g.api_calls()
    g.write_latlng_file()