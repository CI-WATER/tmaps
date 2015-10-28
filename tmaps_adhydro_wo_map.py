#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
********************************************************************************
* Name: TMAPS ADHydro
* Author: Noah Taylor
* Created On: May 20, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
This script uses the methods from frame_processing, render_adhydro, and run_tmachine in order to 
process the output of ADHydro and generate a time machine viewer from the specifed results. A user
can specify the inputs to run the script on lines 36-40
'''

import os
import sys
import shutil
import multiprocessing
from datetime import datetime

import render_adhydro
import frame_processing
from PIL import Image
import run_tmachine


time_start = datetime.now()
    
#------------------------------------------------------------------------------
#main process
#------------------------------------------------------------------------------
    
output_dir = '/home/nrtaylor/Research/Files_From_MtMoran/Green_River_ADHydro/'
user_parameter = 'meshSurfacewaterDepth'
user_contour = 'blueyellowred'
user_opacity = 1
start_frame = 0
end_frame = 2




if __name__=="__main__":    

    runtmaps = render_adhydro.Adhydro_Render(output_dir, user_parameter,user_contour,user_opacity, start_frame, end_frame)
    runtmaps.renderpv()
    
    time_elapsed = (datetime.now()-time_start)
    print "The time it took to render and process frames was " + str(time_elapsed)
    
    # This is the proj4 projection that the ADHydro project was developed in. It will need updated if a different
    # projection is used in the ADHydro setup
    project_proj = '+proj=sinu +datum=WGS84 +lon_0=-109 +x_0=20000000 +y_0=10000000'
    xmin = runtmaps.xmin
    xmax = runtmaps.xmax
    ymin = runtmaps.ymin
    ymax = runtmaps.ymax
    
    # fgnewsizexy, overlayx, overlayy, mapxmin, mapxmax, mapymin, mapymax will be returned from the getbasemap method
    reproject_return = frame_processing.reproject_to_wgs84(project_proj, xmin, xmax, ymin, ymax)
    mapxmin = reproject_return[0]
    mapxmax = reproject_return[1]
    mapymin = reproject_return[2]
    mapymax = reproject_return[3]
    
    
    path = "./images/"
    opacity = int(user_opacity*255)
    combinations = [(os.path.join(path,fname), opacity) for fname in os.listdir(path)]
    
    # Uses multiprocessing for faster processing times
    pool = multiprocessing.Pool()                                      
    result = pool.imap(frame_processing.runtrim_nomap, 
                      combinations,
                      chunksize=1)
   
    pool.close()
    pool.join()
    
    # Takes the legend.png that was generated in render_adhydro and resizes and masks it in
    # preparation of placing it on the Time Machine viewer.
    legenddir = "./images/legend.png"
    legendim = Image.open(legenddir)
    reslegend = (235,581)
    newlegend = legendim.resize(reslegend)
    newlegend.save("./legend.png")
    os.remove(legenddir)
    
    # Name of the Time Machine project and the corresponding necessary directories to run Time Machine
    tmcname = "test2"
    parenttmdir ="./tmc-1.2.1-linux/ct/"+tmcname+ ".tmc"
    tmcimgdir = "./tmc-1.2.1-linux/ct/"+tmcname+ ".tmc/0100-original-images/"
    
    # If there are remaining files from a previous run, this will remove and reset the directories to avoid problems
    try :
        shutil.rmtree(parenttmdir)
    except :
        pass

    # This will regenerate the necessary directories for Time Machine to reference
    try :
        if not os.path.exists(parenttmdir):
            os.makedirs(parenttmdir)
        if not os.path.exists(tmcimgdir):
            os.makedirs(tmcimgdir)
    except :
        pass
    
    # Function for copying files from one directory to another
    def copytree(src, dst, symlinks=False, ignore=None):
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)    
    # Tries to use copytree to copy images to the necessary Time Machine directory
    try :
        copytree(path,tmcimgdir)
    except :
        pass

    # The ./images directory will be removed so as not to waste space. The images were already overlain onto a
    # basemap and put in the corresponding Time Machine directory
    try :
        shutil.rmtree(path)
    except :
        pass
    print('Each rendered image has been overlain onto a basemap and placed into the correct Time Machine input folder.')

    cores = 4
    tmc_ct_dir = "./tmc-1.2.1-linux/ct"
    
    run_tmachine.runtm(cores, tmcname, tmc_ct_dir, mapxmin, mapxmax, mapymin, mapymax)
    
    time_elapsed = (datetime.now()-time_start)
    print "The time it took to produce your product was " + str(time_elapsed)
    
    