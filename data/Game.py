from flask_restful import reqparse, abort, Api, Resource
import random
import requests
from flask import jsonify



class Location(Resource):
    def get(self):
        cities = [
            {'lat': 40.1772, 'lng': 44.5035},
            {'lat': 40.7858, 'lng': 43.8417},
            {'lat': 40.8077, 'lng': 44.4948},
            {'lat': 43.2389, 'lng': 76.8897},
            {'lat': 51.1605, 'lng': 71.4277},
            {'lat': 42.3417, 'lng': 69.5901},
            {'lat': 43.6480, 'lng': 51.1722},
            {'lat': 49.8019, 'lng': 73.1021},
            {'lat': 41.2995, 'lng': 69.2401},
            {'lat': 39.6270, 'lng': 66.9750},
            {'lat': 39.7680, 'lng': 64.4556},
            {'lat': 40.9983, 'lng': 71.6726},
            {'lat': 41.0082, 'lng': 28.9784},
            {'lat': 39.9334, 'lng': 32.8597},
            {'lat': 36.8841, 'lng': 30.7056},
            {'lat': 38.4192, 'lng': 27.1287},
            {'lat': 41.0027, 'lng': 39.7168},
            {'lat': 55.7558, 'lng': 37.6173},
            {'lat': 59.9311, 'lng': 30.3609},
            {'lat': 56.8389, 'lng': 60.6057},
            {'lat': 55.0084, 'lng': 82.9357},
            {'lat': 45.0355, 'lng': 38.9747},
            {'lat': 55.7887, 'lng': 49.1221},
            {'lat': 43.1155, 'lng': 131.8855},
            {'lat': 56.3269, 'lng': 44.0059},
            {'lat': 54.7104, 'lng': 20.4522}]
        city = random.choice(cities)
        city['lat'] += random.uniform(-0.05, 0.05)
        city['lng'] += random.uniform(-0.05, 0.05)
        return jsonify({'lat': city['lat'], 'lng': city['lng']})