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
end_frame = 30




if __name__=="__main__":    

    runtmaps = render_adhydro.Adhydro_Render(output_dir, user_parameter,user_contour,user_opacity, start_frame, end_frame)
    runtmaps.output_info()

    

    
    