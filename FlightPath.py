from ParseWeather import FlightWinds
import numpy as np

convt=1.852/111.111 # nautical miles to latitude degree

"""
lat = na * 1.852km/na * 1deg/111.111km
lon = na * 1.852km/na * 1deg/(111.111*cos(lat)km)
"""

class FlightLayer(list):
    def __init__(self,start_wind):
        self.start = start_wind
        self.surface = self.start.surface
        self.append(start_wind)
    def __eq__(self,wind,tolerance=20): return abs(self.start.elev - wind.elev) < tolerance
    def add(self,wind): self.append(wind)
    def __str__(self): return str([ str(step) for step in self])
    def process(self,lat,lon):
        self.avg_elev = sum(step.elev for step in self)/len(self)
        self.avg_height = sum(step.height for step in self)/len(self)
        self.lat = lat
        self.lon = lon
        
        for step in self:
            lat += convt * step.wind_spd * np.cos( np.deg2rad(step.wind_dir) )
            lon += convt * step.wind_spd * np.sin( np.deg2rad(step.wind_dir) )/np.cos(lat)
            step.lat = lat
            step.lon = lon
        self.path = [[self.lat,self.lon]] + [[step.lat,step.lon] for step in self]
class FlightPath(list):
    def __init__(self,winds,ceiling=3600,npaths=12):
        self.winds = winds
        self.ceiling = ceiling

        self.date = self.winds.date
        self.start = self.winds.start
        self.lat = self.start.lat
        self.lon = -self.start.lon
        self.elev = self.start.elev

        surface = FlightLayer(self.start.surface)
        for wind in self.winds[1:]: surface.add(wind.surface)
        surface.process(self.lat,self.lon)
        self.append(surface)
        for wind in self.start[1:]:
            if wind.elev >= ceiling: break
            if len(self) >= npaths: break
            flight = FlightLayer(wind)
            for step in self.winds[1:]:
                layer = next( (layer for layer in step[1:] if layer == flight),None )
                if layer == None: layer = flight[-1]
                flight.add(layer)
            flight.process(self.lat,self.lon)
            self.append(flight)
if __name__ == "__main__":
    winds= FlightWinds(2020,4,15,12,2,"44.42%2C-89.23")
    flight=FlightPath(winds)
