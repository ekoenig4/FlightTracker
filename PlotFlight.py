from FlightPath import FlightPath
from ParseWeather import FlightWinds
from ArgParser import parser
import numpy as np
import folium
import folium.plugins as plugins
from scimath import units
from scipy.spatial import ConvexHull
import itertools

parser.add_argument("-r","--relative",help="Display layer height (AGL) instead of elevation (MSL)",action="store_true")
unitmap = { key:value for key,value in vars(units.length).items() if type(value) == units.unit.unit }
parser.add_argument("-u","--unit",help="Units to display layer height in",choices=list(unitmap.keys()),default="feet")
def store_html(arg):
    if arg.endswith(".html"): return arg
    return arg+".html"
parser.add_argument("-o","--output",help="Specify output filename for flight track (html)",type=store_html,default="flight_path.html")

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
def length_label(meters):
    convert = unitmap[parser.args.unit]
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
        if parser.args.relative:label ="AGL: "+length_label(layer.avg_height)
        else: label ="MSL: "+length_label(layer.avg_elev)
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
    print("Writing track to: %s"%parser.args.output)
    m.save(parser.args.output)
if __name__ == "__main__":
    winds= FlightWinds(2019,10,15,7,2,"35.1850,-106.5974",tzone="US/Mountain")
    flight=FlightPath(winds)
    PlotPath(flight)
