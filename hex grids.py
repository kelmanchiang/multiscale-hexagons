# coding: utf-8
""" Python functions to create tessellating, multi size regular hexagons

This script simplifies the creation of tessellating hexagon shapefiles, for use
in other softwares, such as Tableau or QGIS.

Multi-sized tessellating hexagons allow for multi-scale analysis at varying
aggregation levels, to observe spatial distribtion of data

Hexagons created are in meters, most suitable for small, city-scale areas.

If the desired extent of the hexagons crosses multiple UTM zones (e.g. large 
country scale), the hexagon sizes may suffer from projection issues.

#user input here

#take in top & bottom lat long coordinates representing the extent of hexagons to create
#no need to worry about left or right, checker below will sort out
coord1 = (-27.365941, 153.140228)
coord2 = (-27.541362, 152.955269)

#input sizes in meters as needed
sizes = [20, 50, 100, 200]

output_filename = 'Brisbane'

#import libraries
import utm
from math import sqrt
import osgeo.osr as osr
import osgeo.ogr as ogr


#convert coords into UTM first
#start xy is the lowest left, will incrementally go to top right
def calc_polygons_new(bx, by, tx, ty, radius):
    """
    This function calculates the coordinates of all the hexagon vertices, given an
    pair of top and bottom coordinates. List is formatted for ogr shapefile creation

    Args:
        bx (float) : the bottom x coordinate of the desired extent
        by (float) : the bottom y coordinate of the desired extent
        tx (float) : the top x coordinate of the desired extent
        ty (float) : the top y coordinate of the desired extent
        radius (int) : the length of one side of the hexagon, equivalent to the
                        from the centre to its edge vertice
    
    Returns:
        list of coordinates of the hexagons' vertices
    """
    
    #calculate the height of a hex
    height = sqrt(radius**2 - (radius/2)**2) * 2
    
    #calculate the midpoint of height length to pointed edge
    mid_len = sqrt(radius**2 - (height/2)**2)
    
    #offsets for moving along and up rows
    xoffset = radius * 1.5
    yoffset = height / 2

    #lists to store coordinates, one for regular row, one row for shifted hexagons
    shifted_xs = []
    straight_xs = []
    shifted_ys = []
    straight_ys = []
    
    #push out the start & end point by distance of radius to ensure proper overlapping
    startx = bx - mid_len
    starty = by - (height/2)
    endx = tx + mid_len
    endy = ty + (height/2)
    
    #while loop to iterate till x limit
    while startx < endx:
        #calculate each hexagon's x coordinate
        xs = [startx, startx+radius, startx+mid_len+radius, startx+radius, startx, startx-mid_len, startx]
        #append to lists
        straight_xs.append(xs)
        #append to second list, with offset
        shifted_xs.append([xoffset + x for x in xs])
        #update x
        startx += xoffset*2
    
    #while loop to iterate till y limit
    while starty < endy:
        #calculate each hexagon's y coordinate
        ys = [starty, starty, starty+(height/2), starty+height, starty+height, starty+(height/2), starty]
        #append to lists
        straight_ys.append(ys)
        #append to second list, with offset
        shifted_ys.append([yoffset + y for y in ys])
        #update x
        starty += yoffset*2
    
    #initialise empty list
    polys = []
    
    #iterate thru full list of coords
    for row in range(0, len(straight_ys) ):
        for col in range(0, len(straight_xs)):
            poly1=[]
            for i in range(0,7):
                #append each y,x coordinate
                poly1.append(tuple( (straight_ys[row][i],straight_xs[col][i]) ))      
            polys.append(poly1)
    
    #repeat for shifted coordinates
    for row in range(0, len(shifted_ys) ):
        for col in range(0, len(shifted_xs)):
            poly1=[]
            for i in range(0,7):
                poly1.append(tuple( (shifted_ys[row][i],shifted_xs[col][i]) ))      
            polys.append(poly1)
    
    #done, list of coordinates ready for shapefile creation
    return polys



def get_epsg(latlong):
    """
    This function obtains the EPSG code of the latitude and longitude provided.
    The EPSG code allows for hexagon creation to be in UTM coordinate system
    and meter units.

    Args:
        latlong (tuple): pair of coordinates, in latitude and logitude format
                            (e.g. WGS84 coordinates)
    
    Returns:
        integer representing the EPSG code for the UTM projection system
    """
    lat = latlong[0]
    lng = latlong[1]
    #get index 2 representing the UTM band that the coordinate falls into
    utm_band = utm.from_latlon(lat, lng)[2]
    # if else to differentiate north/south hemisphere
    if lat>= 0:
        return int('326' + str(utm_band) )
    else:
        return int('327' + str(utm_band) )
    

def shapefile_creator(filename, polygon_coords, sizes, epsg):
    """
    This function creates the shapefile, using inputs from the above 2 functions
    & user inputs.

    Args:
        filename (str) : name of output file
        polygon_coords (list) : formatted list containing the coordinates
                                 of hexagon vertices created by 
                                 calc_polygons_new function
        sizes (list) : list of the desired hexagon sizes to be generated
        epsg (int) : EPSG code indicating the desired projection

    Returns:
        Shapefile of tessellating hexagons, of desired filename.
        Shapefile contains 2 fields, id & hexagon radius size

    """

    #get drivers from ogr
    driver = ogr.GetDriverByName("ESRI Shapefile")
    ds = driver.CreateDataSource(filename + '.shp')
    
    #set spatial reference system
    srid = osr.SpatialReference()
    srid.ImportFromEPSG(epsg)
    
    #create layer & fields
    lyr = ds.CreateLayer(filename, srid, ogr.wkbPolygon)
    
    #create id field
    lyr.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    
    #create size field
    lyr.CreateField(ogr.FieldDefn('size', ogr.OFTInteger))
    
    #create index counter
    index = 0
    
    #iterate through list of hexagon coordinates
    for z in polygon_coords:
        
        #iterate through polygons
        for i in range(0, len(z)):
            grid_ring = ogr.Geometry(ogr.wkbLinearRing)

            #add coordinates of the polygon
            for g in z[i]:
                grid_ring.AddPoint(g[0],g[1])

            #create polygon object, add coordinates
            grid_poly = ogr.Geometry(ogr.wkbPolygon)
            grid_poly.AddGeometry(grid_ring)

            #initialise feature
            feature = ogr.Feature(lyr.GetLayerDefn())
            feature.SetGeometry(grid_poly)
            feature.SetFID(i)

            #update ID field
            feature.SetField('id', i)
            feature.SetField('size', sizes[index])

            #create feature in layer
            lyr.CreateFeature(feature)

            #clear object
            feature = None

        #update counter
        index += 1
    
    #housekeeping    
    ds = None
    lyr = None

    #done
    return

#checker to get the min max lat long
TR = (max(coord1[0], coord2[0]) , max(coord1[1], coord2[1]))
BL = (min(coord1[0], coord2[0]) , min(coord1[1], coord2[1]))

#convert to utm cooords
TR_utm = utm.from_latlon(TR[0], TR[1])[0:2]
BL_utm = utm.from_latlon(BL[0], BL[1])[0:2]

grids = []
for s in sizes:
    grids.append(calc_polygons_new( BL_utm[1], BL_utm[0] ,TR_utm[1], TR_utm[0], s) )
    print('done for ' + str(s))
    
shapefile_creator(output_filename, grids, sizes, get_epsg(TR))