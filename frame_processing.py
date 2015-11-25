#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
********************************************************************************
* Name: Frame Processing
* Author: Noah Taylor
* Created On: May 20, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
The methods in this Frame Processing script are for processing extracted imagery from a model
There is an example given that uses these methods in the tmaps_adhydro.py that uses these
methods with the multiprocess module in order to take advantage of multiple cores to 
generate faster processing times.
'''

import os

from PIL import Image, ImageChops
import PIL
import numpy as np
from osgeo import ogr
from osgeo import osr
from owslib.wms import WebMapService

project_proj = '+proj=sinu +datum=WGS84 +lon_0=-109 +x_0=20000000 +y_0=10000000'

#------------------------------------------------------------------------------
#functions that need to be ran independent for multiprocess module
#------------------------------------------------------------------------------
def getbasemap(project_proj, xmin, xmax, ymin, ymax):
    '''
    Reproject coordinates of the corners of the cropped mesh so that they
    can be relatable to the base map - if a different project is used for
    the the geometry then it can be redefined using the project_proj variable.
    Get the basemap. Here the owslib module will be taken advantage of in
    order to download a high quality basemap for the unstructured gird to
    have geographical context
    '''
    source = osr.SpatialReference()
    source.ImportFromProj4(project_proj)
    
    target = osr.SpatialReference()
    target.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    
    transform = osr.CoordinateTransformation(source, target)
    
    pointone = "POINT ("+str(xmin)+" "+str(ymax)+")"
    pointtwo = "POINT ("+str(xmax)+" "+str(ymin)+")"
    
    
    point = ogr.CreateGeometryFromWkt(pointone)
    point.Transform(transform)
    
    outpoint = point.GetPoint()

    
    point2 = ogr.CreateGeometryFromWkt(pointtwo)
    point2.Transform(transform)
    
    outpoint2 = point2.GetPoint()

    print('Bounding coordinates have been reprojected')
    
    ##This is the WMS server that is being used
    wms = WebMapService('http://raster.nationalmap.gov/arcgis/services/Orthoimagery/USGS_EROS_Ortho_NAIP/ImageServer/WMSServer?request=GetCapabilities&service=WMS')
    
    ##Calculate buffers to impose on the base map - tring 35% on y and 65% on each side
    
    #Highest resolution that the WMS server allows for download
    resx = 5000
    resy = 3816
    
    #The buffer ration of the national map
    bufx = 0.75
    bufy = 0.6
    
    mapxmin = outpoint[0] - (outpoint2[0]-outpoint[0])*bufx
    mapxmax = outpoint2[0] + (outpoint2[0]-outpoint[0])*bufx
    
    mapymin = outpoint2[1] - (outpoint[1]-outpoint2[1])*bufy
    mapymax = outpoint[1] + (outpoint[1]-outpoint2[1])*bufy

    mapbounds = open("mapbounds.txt", "w")
    mapbounds.write(str(mapxmin)+','+str(mapxmax)+','+str(mapymin)+','+str(mapymin))
    mapbounds.close()   
    
    overlayx = ((outpoint2[0]-outpoint[0])*bufx)/(mapxmax-mapxmin)*resx
    overlayy = ((outpoint[1]-outpoint2[1])*bufy)/(mapymax-mapymin)*resy
    overlayx = int(overlayx)
    overlayy = int(overlayy)
    
    fgnewsizex = ((outpoint2[0]-outpoint[0]))/(mapxmax-mapxmin)*resx
    fgnewsizex = int(fgnewsizex)
    fgnewsizey = ((outpoint[1]-outpoint2[1]))/(mapymax-mapymin)*resy
    fgnewsizey = int(fgnewsizey)
    
    fgnewsizexy = (fgnewsizex,fgnewsizey)

    
    ##Here the WMS Request parameters are defined including the bounding box.
    img = wms.getmap(   layers=['0'],
                         styles=[],
                         srs='EPSG:4326',
                         bbox=(mapxmin, mapymin, mapxmax, mapymax),
                         size=(resx, resy),
                         format='image/jpeg',
                         transparent=True
                         )
    out = open('./nationalmap.jpg', 'wb')
    out.write(img.read())
    out.close()
    return fgnewsizexy, overlayx, overlayy, mapxmin, mapxmax, mapymin, mapymax

def trim(im):
    '''
    Trims a uniform background around the mesh to be close to the corners so we
    can infer the xmax,xmin, ymax, ymin from the geometry of the mesh as the
    image boundaries. It is also located outside of a class so that it can be
    used in the multiprocess package to take advantage of multi-core processing.
    '''
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


def runtrim(args):
    '''
    This portion will go through and convert an image to RGBA so that the Alpha 
    channel can be used to mask the back ground as transparent according to the 
    background color. This is so that all we see is the mesh on the basemap
    '''    
    
    fname = args[0]
    opacity = args[1]
    print args
    im = Image.open(fname)
    im = trim(im)
    im = im.convert("RGBA")
    pixdata = im.load()
    for y in xrange(im.size[1]):
        for x in xrange(im.size[0]):
            if pixdata[x, y] == (0, 255, 0, 255):
				pixdata[x, y] = (0, 255, 0, 0)
#            if fname == './images/legend.png' and pixdata[x, y] == (pixdata[x,y][0],pixdata[x,y][1],pixdata[x,y][2],0):
#                    pixdata[x, y] = (0,0,0,150)
            elif fname == './images/legend.png':
                pass
            elif pixdata[x, y][3] == 255:
				pixdata[x, y] = (pixdata[x,y][0],pixdata[x,y][1],pixdata[x,y][2],opacity)
            else:
                pass
    im.save(fname)


  
def underlaymap(args):
    '''
    Run through each mesh image and overlay it onto a copied downloaded basemap. The arguments
    needed to run include the filename, fgnewsizexy, overlayx, overlayy, tmcname, and path. 
    fgnewsizexy, overlayx, and overlayy are returned from the getbasemap method.
    '''
    print args[0]
    
    #hname is the frame directory and name that will be overlain
    hname = args[0]
    
    #fgnewsizexy is the 
    fgnewsizexy = args[1]
    
    
    overlayx = args [2]
    overlayy = args[3]
    tmcname = args[4]
    path = args[5]
    tmcimgdir = "./tmc-1.2.1-linux/ct/"+tmcname+ ".tmc/0100-original-images/"

    background = Image.open('./nationalmap.jpg')
    overlay = Image.open(path + hname)
    overlay = overlay.resize((fgnewsizexy), PIL.Image.ANTIALIAS)
    background.paste(overlay, (overlayx,overlayy), overlay)
    background.save(tmcimgdir + hname)

def runtrim_nomap(args):
    '''
    This portion will go through and convert an image to RGBA so that the Alpha 
    channel can be used to mask the back ground as transparent according to the 
    background color. This is so that all we see is the mesh on the basemap
    '''    
    
    fname = args[0]
    opacity = args[1]

    im = Image.open(fname)
    im = trim(im)
    im = im.convert("RGBA")
    pixdata = im.load()
    for y in xrange(im.size[1]):
        for x in xrange(im.size[0]):
            if pixdata[x, y] == (0, 255, 0, 255):
				pixdata[x, y] = (0, 0, 0, 255)
            if fname == './images/legend.png' and pixdata[x, y] == (0,0,0,255):
                    pixdata[x, y] = (0,0,0,0)
            elif fname == './images/legend.png' and pixdata[x, y] == (255,255,128,255):
                pixdata[x, y] = (0,0,0,0)
            elif fname == './images/legend.png':
                pass
            elif pixdata[x, y][3] == 255:
				pixdata[x, y] = (pixdata[x,y][0],pixdata[x,y][1],pixdata[x,y][2],opacity)
            else:
                pass
    im.save(fname)

def reproject_to_wgs84(project_proj, xmin, xmax, ymin, ymax):
    '''
    Reproject coordinates of the corners of the cropped mesh so that they
    can be relatable to the base map - if a different project is used for
    the the geometry then it can be redefined using the project_proj variable.
    '''
    source = osr.SpatialReference()
    source.ImportFromProj4(project_proj)
    
    target = osr.SpatialReference()
    target.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    
    transform = osr.CoordinateTransformation(source, target)
    
    pointone = "POINT ("+str(xmin)+" "+str(ymax)+")"
    pointtwo = "POINT ("+str(xmax)+" "+str(ymin)+")"
    
    
    point = ogr.CreateGeometryFromWkt(pointone)
    point.Transform(transform)
    
    outpoint = point.GetPoint()

    
    point2 = ogr.CreateGeometryFromWkt(pointtwo)
    point2.Transform(transform)
    
    outpoint2 = point2.GetPoint()

    print('Bounding coordinates have been reprojected')
    

    mapxmin = outpoint[0]
    mapxmax = outpoint2[0]
    
    mapymin = outpoint2[1]
    mapymax = outpoint[1]

    mapbounds = open("mapbounds.txt", "w")
    mapbounds.write(str(mapxmin)+','+str(mapxmax)+','+str(mapymin)+','+str(mapymin))
    mapbounds.close()       
    
    return mapxmin, mapxmax, mapymin, mapymax
    
