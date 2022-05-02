# function that help and set the extent of the canvas, derived from the haversine formula
# input width and height should be in KM
### Make sure the project is in the correct crs => difference between 10 km and 10°
#### This example takes the radius of the Earth for Belgium
import math
#Distance calculation of the given points to Null island (a point with lon lat values of 0), converted to KM
def distance(lon, lat):
    lon, lat , lon1, lat1 = map(math.radians, [lon, lat, 0,0])
    dlon = lon -lon1
    dlat = lat - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat) * math.cos(lat1) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    km = 6367 * c
    return km

# calculates the distance in degrees between the given point and Null island for either the longitude distance or the latitude distance , with position being a string 
def newposition(distance, position):
    if (position =="lat"):
        c= distance/6367
        a = (math.sin(c/2))**2
        var = 2*(math.asin(math.sqrt(a)))
    if (position == "lon"):
        c= distance/6367
        a = (math.sin(c/2))**2
        var = 2*(math.asin(math.sqrt(a)))
    return math.degrees(var)

# calculates the new position of a rectangle in degrees for a point with lon lat values given and width,height being the distances given. 
def new_distance( lon, lat, width = 0, height = 0):
    new_lon = newposition(distance(lon , 0) +width, "lon")
    new_lat = newposition(distance(0, lat) + height, "lat")
    return (new_lon -lon, new_lat -lat)
