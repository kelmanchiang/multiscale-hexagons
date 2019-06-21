# multiscale-hexagons
Python script to create multi-sized, regular, tessellating hexagon shapefiles.

This script simplifies the creation of tessellating hexagon shapefiles, for use in other softwares, such as Tableau, QGIS or other software that uses ESRI shapefile formats.

Multi-sized tessellating hexagons allow for visualisation and analysis of data at varying aggregation levels, such as to observe spatial distribtion of data. A prime example would be visualising point-level data, where mutliple observations would require aggregation to reveal insights.

![alt text](https://github.com/kelmanchiang/multiscale-hexagons/blob/master/screenshot.png "")

# Caveats
The hexagons created are in units of meters and are most suitable for small, city-scale areas.

If the desired extent of the hexagons crosses multiple UTM zones (e.g. large country scale), the hexagon sizes may suffer from projection issues.
