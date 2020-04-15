import subprocess as sp
from datetime import datetime
import pytz

def QueryWinds(utc,n_hrs,airport,source="Op40"):
    year,month,day,hour = utc.strftime("%Y %m %d %H").split()
    url="https://rucsoundings.noaa.gov/get_soundings.cgi?data_source={source}&latest=latest&start_year={year}&start_month_name={month}&start_mday={day}&start_hour={hour}&start_min=0&n_hrs={n_hrs}&fcst_len=shortest&airport={airport}&text=Ascii%20text%20%28GSD%20format%29&hydrometeors=false&start=latest".format(**vars())
    query = sp.Popen(["curl",url],stdout=sp.PIPE,stderr=sp.PIPE)
    return query.stdout.read()
def FindLine(iterator,condition):
    return next( (value for value in iterator if condition(value)),None )
class WindLayer:
    def __init__(self,data):
        self.surface = data[0]==b"9"
        self.pressure,self.elev,self.temp,self.dewpt,self.wind_dir,self.wind_spd = [ float(value) for value in data[1:7] ]
    def __str__(self):
        return "{pressure} {elev} {temp} {dewpt} {wind_dir} {wind_spd}".format(**vars(self))
class WindData(list):
    def __init__(self,data):
        self.data = data.decode()
        data = data.split(b'\n')[1:]
        it = iter(data);
        line = next(it).split()
        self.source = line[0].decode()
        datestr = '-'.join(map(lambda s:s.decode(),line[1:]))
        self.utc = datetime.strptime(datestr,"%H-%d-%b-%Y")
        line = FindLine(it,lambda line:line.split()[0]==b"1").split()
        self.lat,self.lon,self.elev = [ float(value) for value in line[3:6] ]
        FindLine(it,lambda line:line.split()[0]==b"3")
        self += [ WindLayer(line.split()) for line in it ]
        self.surface = self[0]
        if self.elev == 99999.0: self.elev = self.surface.elev
        for layer in self:
            if layer.wind_spd == 99999.0: self.remove(layer)
            layer.height = layer.elev - self.elev
    def __str__(self,raw=False):
        if raw: return self.data

        string = ["{source} {lat} {lon} {elev}".format(**vars(self))]
        string += [ "%i: %s"%(i,str(layer)) for i,layer in enumerate(self) ]
        return "\n".join(string)
class FlightWinds(list):
    def __init__(self,year,month,day,hour,n_hrs,airport,source="Op40",tzone="US/Central"):
        if any( char.isdigit() for char in airport ):
            self.lat,self.lon = [ abs(float(value)) for value in airport.split(",") ]
        self.date = pytz.timezone(tzone).localize(datetime.strptime("{hour}-{day}-{month}-{year}".format(**vars()),"%H-%d-%m-%Y"))
        self.utc = self.date.astimezone(pytz.utc)
        data = QueryWinds(self.utc,n_hrs,airport,source)
        timesteps = data.split(b'\n\n')[:-1]
        self += [ WindData(timestep) for timestep in timesteps ]
        self.start = self[0]
        if not hasattr(self,"lat"):
            self.lat = self.start.lat
            self.lon = self.start.lon
        else:
            for data in self:
                data.lat = self.lat
                data.lon = self.lon
        self.elev = self.start.elev
        self.source = self.start.source
    def __str__(self,raw=False):
        if raw: return '\n\n'.join( str(data) for data in self )
        string = [ self.date.strftime("%Y-%b-%d %H:00:00") ]
        string += [ str(data) for data in self ]
        return "\n\n".join(string)
if __name__ == "__main__":
    flight_winds= FlightWinds(2020,4,15,12,2,"44.42,-89.23")
    print(flight_winds)
