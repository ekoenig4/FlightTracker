#!/usr/bin/env python3
from ArgParser import parser
from ParseWeather import FlightWinds
from FlightPath import FlightPath
from PlotFlight import PlotPath
from datetime import datetime
from pytz import timezone,common_timezones

parser.add_argument("-b","--batch",help="Do not generate plot",action="store_true")
parser.add_argument("-v","--verbose-query",help="Display wind query output",action="store_true")
usa_timezones = [ tz for tz in common_timezones if "US/" in tz ]
parser.add_argument("-z","--time-zone",help="Change time zone",choices=usa_timezones,default="US/Central")
parser.add_argument("-t","--time",help="Time to query winds, ( YEAR-MONTH-DAY-HOUR )",type=lambda a:datetime.strptime(a,"%Y-%m-%d-%H"),default=datetime.now())
parser.add_argument("-d","--duration",help="Time in hours of flight",type=int,default=2)
parser.add_argument("-a","--airport",help="Airport or Latitude/Longitude of launch site",default="44.42,-89.23")
sources=["Op40","Bak40","Bak13","FIM","GFS","NAM"]
parser.add_argument("-s","--source",help="Source Model to query winds",choices=sources,default="Op40")

args = parser.parse_args()

date = timezone(args.time_zone).localize(args.time)

winds = FlightWinds(date,args.duration,args.airport,args.source,args.time_zone)

if args.verbose_query: print(winds)

flight = FlightPath(winds)

if not args.batch:
    PlotPath(flight)
