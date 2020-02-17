
import json
import requests


class TravelTimes():
    def __init__(self):
        self.coordinates = {}
        pass

    def add_address(self, address):
        coordinates = self.get_coordinates(address)
        if coordinates:
            self.coordinates[address] = coordinates
            return True
        else:
            return False

    def get_coordinates(self, address):
        res = requests.get('http://api.digitransit.fi/geocoding/v1/search?text=' + address)
        location_json = json.loads(res.text)
        coordinates = location_json['features'][0]['geometry']['coordinates']

        return {
            'latitude': coordinates[1], 
            'longitude': coordinates[0]
            }

    def get_travel_times(self, address):
        base_query = """
        {
        plan(
            from: {lat: %f, lon: %f}
            to: {lat: %f, lon: %f}
            numItineraries: 3
        ) {
            itineraries {
                legs {
                    mode
                    duration
                }
            }
        }
        }
        """
        coordinates = self.get_coordinates(address)
        
        queries = [(coordinates['latitude'],
                    coordinates['longitude'], 
                    self.coordinates[place]['latitude'],
                    self.coordinates[place]['longitude'],
                    place)
                for place in self.coordinates]
        
        travel_times = {}
        for query in queries:
            travel_times[query[4]] = []
            res = requests.post('https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql',
                                json={'query': base_query % query[:4]}
                            )
            routing_json = json.loads(res.text)
            itineraries = routing_json['data']['plan']['itineraries']
            
            for i in itineraries:
                time = int(sum([x['duration'] for x in i['legs']])/60)
                modes = ', '.join([x['mode'] for x in i['legs'] if x['mode'] != 'WALK'])
                travel_times[query[4]].append((modes, str(time) + ' min'), )
          
        return travel_times


if __name__ == "__main__":
    t = TravelTimes()
    a = t.add_address('Otakaari 1, Espoo')
    a = t.add_address('Keskuskatu 7, Helsinki')
    times = t.get_travel_times('Helsinki, Viikki')
    print(times)
