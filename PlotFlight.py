from FlightPath import FlightPath
from ParseWeather import FlightWinds
import numpy as np
import folium
import folium.plugins as plugins
from scimath import units
from scipy.spatial import ConvexHull
import itertools

colors = [
    'lightblue',
    'red',
    'blue',
    'gray',
    'darkred',
    'orange',
    'green',
    'black',
    'darkgreen',
    'darkblue',
    'purple',
    'cadetblue',
    'lightgreen',
]
coliter = iter(colors)
def getColor():
    global coliter
    try:
        return next(coliter)
    except StopIteration:
        coliter = iter(colors)
        return next(coliter)
def length_label(meters,convert=units.length.f):
    value = units.convert(meters,units.length.m,convert)
    return "%i %s"%(value,convert.label)

def FlightArea(m,flight):
    fg = folium.FeatureGroup(name="Flight Area")
    m.add_child(fg)

    points = []
    for layer in flight: points += layer.path
    points.sort()
    points = np.array(list(points for points,_ in itertools.groupby(points)),float)
    hull = ConvexHull(points)
    locations = []
    for i in hull.vertices: locations.append( [points[i,0],points[i,1]] )
    folium.Polygon(
        locations=locations,
        color=getColor(),
        fill=True,
        fill_opacity=0.2
    ).add_to(fg)
def FlightTracks(m,flight):
    fg = folium.FeatureGroup(name="Flight Tracks")
    m.add_child(fg)
    
    for ilayer,layer in enumerate(flight):
        label ="MSL: "+length_label(layer.avg_elev)
        color = getColor()
        print(label)
        lg = plugins.FeatureGroupSubGroup(fg,label)
        m.add_child(lg)
        folium.PolyLine(
            locations=layer.path,
            popup=label,
            color=color
        ).add_to(lg)
        for ipath,loc in enumerate(layer.path):
            if ipath == 0: continue
            folium.CircleMarker(
                location=loc,
                radius=5,
                weight=8./ipath,
                popup=label,
                color=color
            ).add_to(lg)
def PlotPath(flight):
    start = [flight.lat,flight.lon]
    m = folium.Map(location=start)
    folium.Marker(
        location=start,
        popup="Launch Site",
    ).add_to(m)
    FlightArea(m,flight)
    FlightTracks(m,flight)

    folium.LayerControl(collapsed=False).add_to(m)
    
    m.save("flight_path.html")
if __name__ == "__main__":
    winds= FlightWinds(2020,4,15,12,2,"35.1850,-106.5974")
    flight=FlightPath(winds)
    PlotPath(flight)
