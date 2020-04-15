import subprocess as sp
from datetime import datetime

def QueryWinds(year,month,day,hour,n_hrs,airport,source="Op40"):
    url="https://rucsoundings.noaa.gov/get_soundings.cgi?data_source={source}&latest=latest&start_year={year}&start_month_name={month}&start_mday={day}&start_hour={hour}&start_min=0&n_hrs={n_hrs}&fcst_len=shortest&airport={airport}&text=Ascii%20text%20%28GSD%20format%29&hydrometeors=false&start=latest".format(**vars())
    query = sp.Popen(["curl",url],stdout=sp.PIPE,stderr=sp.PIPE)
    return query.stdout.read()
def FindLine(iterator,condition):
    return next( (value for value in iterator if condition(value)),None )
class WindLayer:
    def __init__(self,data):
        self.surface = data[0]==b"9"
        self.pressure,self.elev,self.temp,self.dewpt,self.wind_dir,self.wind_spd = [ float(value) for value in data[1:7] ]
class WindData:
    def __init__(self,data):
        data = data.split(b'\n')[1:]
        it = iter(data);
        line = next(it).split()
        self.source = line[0].decode()
        datestr = '-'.join(map(lambda s:s.decode(),line[1:]))
        self.date = datetime.strptime(datestr,"%H-%d-%b-%Y")
        line = FindLine(it,lambda line:line.split()[0]==b"1").split()
        self.lat,self.lon,self.elev = [ float(value) for value in line[3:6] ]
        FindLine(it,lambda line:line.split()[0]==b"3")
        self.layers = [ WindLayer(line.split()) for line in it ]
        self.surface = self.layers[0]
        if self.elev == 99999.0: self.elev = self.surface.elev
        for layer in list(self.layers):
            if layer.pressure == 10000.0: self.layers.remove(layer)
            layer.height = layer.elev - self.elev
class FlightWinds:
    def __init__(self,year,month,day,hour,n_hrs,airport,source="Op40"):
        data = QueryWinds(year,month,day,hour,n_hrs,airport,source)
        timesteps = data.split(b'\n\n')[:-1]
        self.wind_data = [ WindData(timestep) for timestep in timesteps ]
        self.start = self.wind_data[0]
        self.lat = self.start.lat
        self.lon = self.start.lon
        self.elev = self.start.elev
        self.date = self.start.date
        self.source = self.start.source
if __name__ == "__main__":
    flight_winds= FlightWinds(2020,4,15,16,2,"44.42%2C-89.23")
