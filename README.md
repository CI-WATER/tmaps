# tmaps
Time Machine Automated Python Scripts for producing interactive viewers of transient data through video tiles


##Prerequisites:
The code was developed in Ubuntu but should be compatible with any Linux/Unix system
- Python2.7
- Ruby
- xmlsimple	 (ruby gem) -- normally installed with Ruby by default
- ParaView4.0.1
- netCDF4-python (Python package)
- GDAL 		 (Python package)
- owslib	 (Python package)
- PIL		 (Python package)


###Install Ruby on Ubuntu / should install xmlsimple with it
```
$ apt-get install ruby

```

###Install ParaView4.0.1 on Ubuntu
```
$ apt-get install paraview

```

###Install netCDF4-python on Ubuntu:
```
$ apt-get install python-dev zlib1g-dev libhdf5-serial-dev libnetcdf-dev 
$ pip install numpy
$ pip install netCDF4
```

###Install GDAL on Ubuntu:
```
$ apt-get install python-gdal
```

###Install PIL and OWSLib on Ubuntu:
```
$ pip install PIL
$ pip install owslib
```

##Example of Use:
There are two example files that can be used with an accompanying set of output ADHydro files. They are the "tmaps_adhydro.py" and the tmaps_adhydro_wo_map.py". One will produce a product with a basemap from the USGS and the other will produce just a mesh solution on a black background. Before running, the files will need to be modified by adjusting the following input parameters in a text editor before running them in a Python interpreter.

- output_dir = './dir_to_ADHydro_Output/'
- user_parameter = 'meshSurfacewaterDepth'
- user_contour = 'blueyellowred'
- user_opacity = 0.65
- start_frame = 55
- end_frame = 65


