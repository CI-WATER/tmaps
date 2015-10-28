#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
********************************************************************************
* Name: Render_ADHydro
* Author: Noah Taylor
* Created On: May 20, 2015
* Copyright: (c) Brigham Young University 2015
* License: BSD 2-Clause
********************************************************************************
The rendering script for TMAPS specifically for the ADHydro Output.
The script has a number of visualization options that uses the ParaView rendering
capabilities to extract the individual output frames.For better visualization, 
Contour options are available. The legend is extracted from the chosen contour schema.
'''

import os
import sys
import shutil
import multiprocessing
from datetime import datetime
import jdcal
import time

import netCDF4
try: paraview.simple
except: from paraview.simple import *
paraview.simple._DisableFirstRenderCameraReset()




time_start = datetime.now()

class Adhydro_Render:
    
    def __init__(self, parameter, contour, opacityofmesh, start_frame, end_frame):
        """
        The class parses through the netcdf output of ADHydro through the use of
        the xmf that can be generated using the post processing code for ADHydro.
        It also extracts both the number of time steps and their output value to
        a text file that is later used by the run_tmachine.py so that the user inferace
        has the correct times corresponding to the frames.
        """
        self.input_dir = 'geometry.nc'
        self.parinput_dir = 'display.nc'
        self.parameter = parameter
        self.netcdfgeo = netCDF4.Dataset(self.input_dir)
        self.netcdfpar = netCDF4.Dataset(self.parinput_dir)


        self.ymin = self.netcdfgeo.variables['meshNodeY'][:].min()
        self.ymax = self.netcdfgeo.variables['meshNodeY'][:].max()
        self.ymid = (self.ymax + self.ymin)/2
        self.ydif = self.ymax - self.ymin
        
        self.xmin = self.netcdfgeo.variables['meshNodeX'][:].min()
        self.xmax = self.netcdfgeo.variables['meshNodeX'][:].max()
        self.xmid = (self.xmax + self.xmin)/2
        self.xdif = self.xmax - self.xmin
        
        self.zmin = self.netcdfgeo.variables['meshNodeZSurface'][:].min()
        self.zmax = self.netcdfgeo.variables['meshNodeZSurface'][:].max()
        self.zmid = (self.zmax + self.zmin)/2
        self.zdif = self.zmax - self.zmin
        self.zout = self.xdif + 2*self.ydif
        
        print self.ymin, self.ymax, self.xmin, self.xmax, self.zmin, self.zmax
        
        data_nc = self.netcdfpar
        try:
            jul_date = data_nc.variables['referenceDate'][0]
            ref_date = jdcal.jd2gcal(jul_date,0)
            ref_date_time = datetime(ref_date[0],ref_date[1],ref_date[2],int(ref_date[3]*24))
            ref_time_utc = time.mktime(ref_date_time.timetuple())
        except:
            data_nc.close()
            
        variables = data_nc.variables.keys()
        if 'currentTime' in variables:
            timeout = [(t+ref_time_utc) for t in data_nc.variables['currentTime'][:]]
            datetimeout = [datetime.utcfromtimestamp(dto) for dto in timeout]
            self.datetimeout = datetimeout
        else:
            data_nc.close()
            


        imagepath = './images'
        if not os.path.isdir(imagepath):
            os.makedirs(imagepath)
            
        self.contour = contour
        self.opacity = opacityofmesh
        self.start_frame = start_frame
        self.end_frame = end_frame

        
        if opacityofmesh > 1:
            sys.exit("Please choose an opacity value that is not greater than 1 nor less than 0")
        elif opacityofmesh < 0:
            sys.exit("Please choose an opacity value that is not greater than 1 nor less than 0")
        else:
            pass

        
    def renderpv(self):
        '''
        This method uses the paraview package to loop through the specified 
        parameter and output an image of each time step. The output 
        of this method can be found in the images folder in the relative 
        working directory.        
        '''

        contour = self.contour
        end_frame = self.end_frame
        start_frame = self.start_frame
        
        # Here the code checks to see what parameter the user is wanting to render. It then sets the variable associated
        # to the specified parameter. If it is meshElementZSurface, it will max the contour intervals equal to the min
        # and max z elevations
        parameter = self.parameter       
        print parameter
        try:
            if parameter == 'meshElementZSurface':
                max_max = self.zmax
                min_min = self.zmin          
            elif parameter != 'meshElementZSurface':
                max_max = self.netcdfpar.variables[parameter][:].max()
                min_min = self.netcdfpar.variables[parameter][:].min()
                print max_max, min_min
            
        except Exception:

            sys.exit("Invalid parameter Inputted.")
        
        self.netcdfgeo.close()
        self.netcdfpar.close()        
        
        # Sets the contour min and max according to the parameter's min and max previously derived
        try:
            piecewise = CreatePiecewiseFunction( Points=[min_min, 1.0, 0.5, 0.0, max_max, 1.0, 0.5, 0.0] )
            titletype = parameter
        except Exception:
            sys.exit("Invalid parameter inputted. Please input an existing variable.")        

        # From the inputted contour scheme selected by the user, generate the pvlookup parameter that will be used as the contour reference
        if contour == 'cooltowarm':
            pvlookup = GetLookupTableForArray( parameter, 1, Discretize=1, RGBPoints=[min_min, 0.23, 0.299, 0.754, max_max, 0.706, 0.016, 0.15], UseLogScale=0, VectorComponent=0, NanColor=[0.25, 0.0, 0.0], NumberOfTableValues=256, EnableOpacityMapping=0, ColorSpace='Diverging', IndexedLookup=0, VectorMode='Magnitude', ScalarOpacityFunction=piecewise, HSVWrap=0, ScalarRangeInitialized=1.0, AllowDuplicateScalars=1, Annotations=[], LockScalarRange=0 )           
        elif contour == 'bluetocyan':
            pvlookup = GetLookupTableForArray(parameter, 1, Discretize=1, RGBPoints=[min_min, 0.0, 0.0, 0.0, ((max_max-min_min)/16*1+min_min), 0.0, 0.15294117647058825, 0.36470588235294116, ((max_max-min_min)/16*2+min_min), 0.0, 0.2549019607843137, 0.47058823529411764, ((max_max-min_min)/16*3+min_min), 0.0, 0.34901960784313724, 0.5725490196078431, ((max_max-min_min)/16*4+min_min), 0.0, 0.44313725490196076, 0.6705882352941176, ((max_max-min_min)/16*5+min_min), 0.0, 0.5372549019607843, 0.7725490196078432, ((max_max-min_min)/16*6+min_min), 0.0, 0.6274509803921569, 0.8705882352941177, ((max_max-min_min)/16*7+min_min), 0.0, 0.7176470588235294, 0.9647058823529412, ((max_max-min_min)/16*8+min_min), 0.0784313725490196, 0.7725490196078432, 1.0, ((max_max-min_min)/16*9+min_min), 0.20784313725490197, 0.8588235294117647, 1.0, ((max_max-min_min)/16*10+min_min), 0.3254901960784314, 0.9411764705882353, 1.0, ((max_max-min_min)/16*11+min_min), 0.45098039215686275, 1.0, 1.0, ((max_max-min_min)/16*12+min_min), 0.5607843137254902, 1.0, 1.0, ((max_max-min_min)/16*13+min_min), 0.6627450980392157, 1.0, 1.0, ((max_max-min_min)/16*14+min_min), 0.7607843137254902, 1.0, 1.0, ((max_max-min_min)/16*15+min_min), 0.8705882352941177, 1.0, 1.0, max_max, 1.0, 1.0, 1.0], UseLogScale=0, VectorComponent=0, NanColor=[0.4980392156862745, 0.0, 0.0], NumberOfTableValues=256, EnableOpacityMapping=0, ColorSpace='Lab', IndexedLookup=0, VectorMode='Magnitude', ScalarOpacityFunction=piecewise, HSVWrap=0, ScalarRangeInitialized=1.0, AllowDuplicateScalars=1, Annotations=[], LockScalarRange=0 )        
        elif contour == 'bluetored':
            pvlookup = GetLookupTableForArray( parameter, 1, Discretize=1, RGBPoints=[min_min, 0.0196078431372549, 0.18823529411764706, 0.3803921568627451, ((max_max-min_min)/16*1+min_min), 0.08850232700083925, 0.3211108567940795, 0.5649347676813916, ((max_max-min_min)/16*2+min_min), 0.1633936064698253, 0.444983596551461, 0.6975051499198901, ((max_max-min_min)/16*3+min_min), 0.24705882352941178, 0.5557030594338903, 0.7541008621347371, ((max_max-min_min)/16*4+min_min), 0.42069123369192035, 0.6764324406805524, 0.8186923018234531, ((max_max-min_min)/16*5+min_min), 0.6064545662623025, 0.7897764553292134, 0.8802777141985199, ((max_max-min_min)/16*6+min_min), 0.7614709697108415, 0.868513008316167, 0.9245593957427329, ((max_max-min_min)/16*7+min_min), 0.8780498970016022, 0.9257190814068819, 0.9519493400473029, ((max_max-min_min)/16*8+min_min), 0.969085221637293, 0.966475928892958, 0.9649347676813916, ((max_max-min_min)/16*9+min_min), 0.9838559548332951, 0.8975814450293736, 0.8468299382009613, ((max_max-min_min)/16*10+min_min), 0.9824673838406958, 0.8006866559853514, 0.706111238269627, ((max_max-min_min)/16*11+min_min), 0.9603265430685893, 0.6678263523308156, 0.5363393606469825, ((max_max-min_min)/16*12+min_min), 0.8945754177157245, 0.5038071259632257, 0.3997711146715496, ((max_max-min_min)/16*13+min_min), 0.8170748455024033, 0.3321736476691844, 0.2810406652933547, ((max_max-min_min)/16*14+min_min), 0.7284962233920805, 0.15501640344853895, 0.1973907072556649, ((max_max-min_min)/16*15+min_min), 0.576928358892195, 0.055359731441214616, 0.1492484931715877, max_max, 0.403921568627451, 0.0, 0.12156862745098039], UseLogScale=0, VectorComponent=0, NanColor=[0.4980392156862745, 0.0, 0.0], NumberOfTableValues=256, EnableOpacityMapping=0, ColorSpace='Lab', IndexedLookup=0, VectorMode='Magnitude', ScalarOpacityFunction=piecewise, HSVWrap=0, ScalarRangeInitialized=1.0, AllowDuplicateScalars=1, Annotations=[], LockScalarRange=0 )
        elif contour == 'blueyellowred':
            pvlookup = GetLookupTableForArray( parameter, 1, Discretize=0, RGBPoints=[min_min, 0.19121080338750285, 0.19121080338750285, 0.19121080338750285, ((max_max-min_min)/10000*1+min_min), 0, 0, 1, ((max_max-min_min)/16*2+min_min), 0.22059967956054016, 0.06175326161593042, 0.8635538261997406, ((max_max-min_min)/16*3+min_min), 0.17509727626459143, 0.2789806973373007, 0.9779354543373769, ((max_max-min_min)/16*4+min_min), 0.14352635996032653, 0.57607385366598, 0.9985503929198138, ((max_max-min_min)/16*5+min_min), 0.16646066987106126, 0.8718852521553369, 0.9659418631265736, ((max_max-min_min)/16*6+min_min), 0.3761959258411536, 0.9935606927595941, 0.9818265049210345, ((max_max-min_min)/16*7+min_min), 0.6820019836728466, 0.9913023575188831, 0.9992370489051652, ((max_max-min_min)/16*8+min_min), 0.9541771572442207, 0.9527275501640344, 0.9437399862668803, ((max_max-min_min)/16*9+min_min), 0.9997405966277562, 0.9930113679713131, 0.6628976882581826, ((max_max-min_min)/16*10+min_min), 0.9794003204394598, 0.9914702067597467, 0.35797665369649806, ((max_max-min_min)/16*11+min_min), 0.9687647821774624, 0.8549629968719005, 0.16266117341878386, ((max_max-min_min)/16*12+min_min), 0.9992523079270619, 0.5566948958571756, 0.14431982909895474, ((max_max-min_min)/16*13+min_min), 0.9739528496223392, 0.262226291294728, 0.17795071335927368, ((max_max-min_min)/16*14+min_min), 0.8523537041275654, 0.05267414358739605, 0.22298008697642482, ((max_max-min_min)/16*15+min_min), 0.5938963912413214, 0.00912489509422446, 0.2388494697489891, max_max, 0.19121080338750285, 0.19121080338750285, 0.19121080338750285], UseLogScale=0, VectorComponent=0, NanColor=[0.4980392156862745, 0.0, 0.0], NumberOfTableValues=256, EnableOpacityMapping=0, ColorSpace='Lab', IndexedLookup=0, VectorMode='Magnitude', ScalarOpacityFunction=piecewise, HSVWrap=0, ScalarRangeInitialized=1.0, AllowDuplicateScalars=1, Annotations=[], LockScalarRange=0 )
        elif contour == 'rainbowdesat':
            pvlookup = GetLookupTableForArray( parameter, 1, Discretize=1, RGBPoints=[min_min, 0.2784313725490196, 0.2784313725490196, 0.8588235294117647, ((max_max-min_min)/7*1+min_min), 0.0, 0.0, 0.3607843137254902, ((max_max-min_min)/7*2+min_min), 0.0, 1.0, 1.0, ((max_max-min_min)/7*3+min_min), 0.0, 0.5019607843137255, 0.0, ((max_max-min_min)/7*4+min_min), 1.0, 1.0, 0.0, ((max_max-min_min)/7*5+min_min), 1.0, 0.3803921568627451, 0.0, ((max_max-min_min)/7*6+min_min), 0.4196078431372549, 0.0, 0.0, max_max, 0.8784313725490196, 0.30196078431372547, 0.30196078431372547], UseLogScale=0, VectorComponent=0, NanColor=[1.0, 1.0, 0.0], NumberOfTableValues=256, EnableOpacityMapping=0, ColorSpace='RGB', IndexedLookup=0, VectorMode='Magnitude', ScalarOpacityFunction=piecewise, HSVWrap=0, ScalarRangeInitialized=1.0, AllowDuplicateScalars=1, Annotations=[], LockScalarRange=0 )
     
        else:
            sys.exit("Invalid contour inputted. Please input one of the following: 'cooltowarm', 'bluetocyan', 'bluetored', 'blueyellowred', '0min_blueyellowred' , 'rainbowdesat'") 
            

    
        # Render and export the images from each time step of the data set
        # There are piecewise functions to define what data set will be viewed out of the XDMF file and the max and min bounds for contour display
        # Notice that the XDMFReader is being used to interpret the input files since this was developed to originally handl ADHydro ouput.
        mesh_display_xmf = XDMFReader( guiName="mesh_display.xmf", FileName='./mesh_display.xmf')
        ##Here it is being determined how many time steps there are in order to extract all these as images later
        tsteps = mesh_display_xmf.TimestepValues
    
        # Fixes a bug if there is only one value for the output at time 0.0
        if tsteps == 0.0:
            tsteps = [0.0]
        elif tsteps != 0.0:
            pass
        
        
        # Prints out the time step number and value to a txt value to be written to the time machine docs later
#        tstepstotext = [('"Output Time: '+str(i)+'",') for i in tsteps]
#        np.savetxt('tstepstotext.txt',tstepstotext,delimiter=',', fmt="%s")
        
        
        total_frames = end_frame-start_frame
        # Keeps track of the rendering progress
        print("There are a total number of " + str(total_frames) + " images that will be extracted")
        
        tstepsnum = len(tsteps)
        
        
        # THe following sets up the rendering options used to define the extents, background color, and similar parameters for output
        RenderView1 = CreateRenderView()
        RenderView1.LightSpecularColor = [1.0, 1.0, 1.0]
        RenderView1.UseOutlineForLODRendering = 0
        RenderView1.KeyLightAzimuth = 10.0
        RenderView1.UseTexturedBackground = 0
        RenderView1.UseLight = 1
        RenderView1.CameraPosition = [self.xmid, self.ymid, self.zout]
        RenderView1.FillLightKFRatio = 3.0
        RenderView1.Background2 = [0.0, 0.0, 0.16470588235294117]
        RenderView1.FillLightAzimuth = -10.0
        RenderView1.LODResolution = 0.5
        RenderView1.BackgroundTexture = []
        RenderView1.InteractionMode = '3D'
        RenderView1.StencilCapable = 1
        RenderView1.LightIntensity = 1.0
        RenderView1.CameraFocalPoint = [self.xmid, self.ymid, self.zmid]
        RenderView1.ImageReductionFactor = 2
        RenderView1.CameraViewAngle = 30.0
        RenderView1.CameraParallelScale = 36120.14658587354
        RenderView1.EyeAngle = 2.0
        RenderView1.HeadLightKHRatio = 3.0
        RenderView1.StereoRender = 0
        RenderView1.KeyLightIntensity = 0.75
        RenderView1.BackLightAzimuth = 110.0
        RenderView1.OrientationAxesInteractivity = 0
        RenderView1.UseInteractiveRenderingForSceenshots = 0
        
        # If on, UseOffscreenRendering does not open a render window
        RenderView1.UseOffscreenRendering = 1
        
        # The three values are the RGB of the background divided by 255 so for example a green bg is 0/255, 255/255, 0/255
        RenderView1.Background = [0, 1, 0]
        
        RenderView1.UseOffscreenRenderingForScreenshots = 1
        RenderView1.NonInteractiveRenderDelay = 0.0
        RenderView1.CenterOfRotation = [self.xmid, self.ymid, self.zmid]
        RenderView1.CameraParallelProjection = 0
        RenderView1.CompressorConfig = 'vtkSquirtCompressor 0 3'
        RenderView1.HeadLightWarmth = 0.5
        RenderView1.MaximumNumberOfPeels = 4
        RenderView1.LightDiffuseColor = [1.0, 1.0, 1.0]
        RenderView1.StereoType = 'Red-Blue'
        RenderView1.DepthPeeling = 1
        RenderView1.BackLightKBRatio = 3.5
        RenderView1.StereoCapableWindow = 1
        RenderView1.CameraViewUp = [0.0, 1.0, 0.0]
        RenderView1.LightType = 'HeadLight'
        RenderView1.LightAmbientColor = [1.0, 1.0, 1.0]
        RenderView1.RemoteRenderThreshold = 20.0
        RenderView1.CacheKey = 120.423912
        RenderView1.UseCache = 0
        RenderView1.KeyLightElevation = 50.0
        RenderView1.CenterAxesVisibility = 0
        RenderView1.MaintainLuminance = 0
        RenderView1.StillRenderImageReductionFactor = 1
        RenderView1.BackLightWarmth = 0.5
        RenderView1.FillLightElevation = -75.0
        RenderView1.MultiSamples = 0
        RenderView1.FillLightWarmth = 0.4
        RenderView1.AlphaBitPlanes = 1
        RenderView1.LightSwitch = 0
        RenderView1.OrientationAxesVisibility = 0
        RenderView1.BackLightElevation = 0.0
        RenderView1.ViewTime = 120.423912
        RenderView1.OrientationAxesOutlineColor = [1.0, 1.0, 1.0]
        RenderView1.LODThreshold = 5.0
        RenderView1.CollectGeometryThreshold = 100.0
        RenderView1.UseGradientBackground = 0
        RenderView1.KeyLightWarmth = 0.6
        RenderView1.OrientationAxesLabelColor = [1.0, 1.0, 1.0]
        
        DataRepresentation1 = Show()
        DataRepresentation1.CubeAxesZAxisVisibility = 1
        DataRepresentation1.SelectionPointLabelColor = [0.5, 0.5, 0.5]
        DataRepresentation1.SelectionPointFieldDataArrayName = 'vtkOriginalPointIds'
        DataRepresentation1.SuppressLOD = 0
        DataRepresentation1.CubeAxesXGridLines = 0
        DataRepresentation1.BlockVisibility = []
        DataRepresentation1.CubeAxesYAxisTickVisibility = 1
        DataRepresentation1.Position = [0.0, 0.0, 0.0]
        DataRepresentation1.BackfaceRepresentation = 'Follow Frontface'
        DataRepresentation1.SelectionOpacity = 1.0
        DataRepresentation1.SelectionPointLabelShadow = 0
        DataRepresentation1.CubeAxesYGridLines = 0
        DataRepresentation1.CubeAxesZAxisTickVisibility = 1
        DataRepresentation1.OrientationMode = 'Direction'
        DataRepresentation1.ScaleMode = 'No Data Scaling Off'
        DataRepresentation1.Diffuse = 1.0
        DataRepresentation1.SelectionUseOutline = 1
        DataRepresentation1.SelectionPointLabelFormat = ''
        DataRepresentation1.CubeAxesZTitle = 'Z-Axis'
        DataRepresentation1.Specular = 0.1
        DataRepresentation1.SelectionVisibility = 1
        DataRepresentation1.InterpolateScalarsBeforeMapping = 1
        DataRepresentation1.CustomRangeActive = [0, 0, 0]
        DataRepresentation1.Origin = [0.0, 0.0, 0.0]
        DataRepresentation1.CubeAxesVisibility = 0
        DataRepresentation1.Scale = [1.0, 1.0, 1.0]
        DataRepresentation1.SelectionCellLabelJustification = 'Left'
        DataRepresentation1.DiffuseColor = [1.0, 1.0, 1.0]
        DataRepresentation1.SelectionCellLabelOpacity = 1.0
        DataRepresentation1.CubeAxesInertia = 1
        DataRepresentation1.Source = []
        DataRepresentation1.Masking = 0
        DataRepresentation1.Opacity = 1.0
        DataRepresentation1.LineWidth = 1.0
        DataRepresentation1.MeshVisibility = 0
        DataRepresentation1.Visibility = 1
        DataRepresentation1.SelectionCellLabelFontSize = 18
        DataRepresentation1.CubeAxesCornerOffset = 0.0
        DataRepresentation1.SelectionPointLabelJustification = 'Left'
        DataRepresentation1.OriginalBoundsRangeActive = [0, 0, 0]
        DataRepresentation1.SelectionPointLabelVisibility = 0
        DataRepresentation1.SelectOrientationVectors = ''
        DataRepresentation1.CubeAxesTickLocation = 'Inside'
        DataRepresentation1.BackfaceDiffuseColor = [1.0, 1.0, 1.0]
        DataRepresentation1.CubeAxesYLabelFormat = '%-#6.3g'
        DataRepresentation1.CubeAxesYAxisVisibility = 1
        DataRepresentation1.SelectionPointLabelFontFamily = 'Arial'
        DataRepresentation1.CubeAxesUseDefaultYTitle = 1
        DataRepresentation1.SelectScaleArray = ''
        DataRepresentation1.CubeAxesYTitle = 'Y-Axis'
        DataRepresentation1.ColorAttributeType = 'CELL_DATA'
        DataRepresentation1.AxesOrigin = [0.0, 0.0, 0.0]
        DataRepresentation1.UserTransform = [1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0]
        DataRepresentation1.SpecularPower = 100.0
        DataRepresentation1.Texture = []
        DataRepresentation1.SelectionCellLabelShadow = 0
        DataRepresentation1.AmbientColor = [1.0, 1.0, 1.0]
        DataRepresentation1.BlockOpacity = {}
        DataRepresentation1.MapScalars = 1
        DataRepresentation1.PointSize = 2.0
        DataRepresentation1.CubeAxesUseDefaultXTitle = 1
        DataRepresentation1.SelectionCellLabelFormat = ''
        DataRepresentation1.Scaling = 0
        DataRepresentation1.StaticMode = 0
        DataRepresentation1.SelectionCellLabelColor = [0.0, 1.0, 0.0]
        DataRepresentation1.EdgeColor = [0.0, 0.0, 0.5000076295109483]
        DataRepresentation1.CubeAxesXAxisTickVisibility = 1
        DataRepresentation1.SelectionCellLabelVisibility = 0
        DataRepresentation1.NonlinearSubdivisionLevel = 1
        DataRepresentation1.CubeAxesColor = [1.0, 1.0, 1.0]
        DataRepresentation1.Representation = 'Surface'
        DataRepresentation1.CustomRange = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
        DataRepresentation1.CustomBounds = [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
        DataRepresentation1.Orientation = [0.0, 0.0, 0.0]
        DataRepresentation1.CubeAxesXTitle = 'X-Axis'
        DataRepresentation1.ScalarOpacityUnitDistance = 2170.6532965413962
        DataRepresentation1.BackfaceOpacity = 1.0
        DataRepresentation1.SelectionPointLabelFontSize = 18
        
        # User specified variable for the parameter is assigned to the render option
        DataRepresentation1.SelectionCellFieldDataArrayName = parameter
        
        DataRepresentation1.SelectionColor = [1.0, 0.0, 1.0]
        DataRepresentation1.BlockColor = {}
        DataRepresentation1.Ambient = 0.0
        DataRepresentation1.CubeAxesXAxisMinorTickVisibility = 1
        DataRepresentation1.ScaleFactor = 5243.983899999969
        DataRepresentation1.BackfaceAmbientColor = [1.0, 1.0, 1.0]
        DataRepresentation1.ScalarOpacityFunction = piecewise
        DataRepresentation1.SelectMaskArray = ''
        DataRepresentation1.SelectionLineWidth = 2.0
        DataRepresentation1.CubeAxesZAxisMinorTickVisibility = 1
        DataRepresentation1.CubeAxesXAxisVisibility = 1
        DataRepresentation1.CubeAxesXLabelFormat = '%-#6.3g'
        DataRepresentation1.Interpolation = 'Gouraud'
        DataRepresentation1.CubeAxesZLabelFormat = '%-#6.3g'
        DataRepresentation1.SelectMapper = 'Projected tetra'
        DataRepresentation1.SelectionCellLabelFontFamily = 'Arial'
        DataRepresentation1.SelectionCellLabelItalic = 0
        DataRepresentation1.CubeAxesYAxisMinorTickVisibility = 1
        DataRepresentation1.CubeAxesZGridLines = 0
        DataRepresentation1.ExtractedBlockIndex = 0
        DataRepresentation1.SelectionPointLabelOpacity = 1.0
        DataRepresentation1.UseAxesOrigin = 0
        DataRepresentation1.CubeAxesFlyMode = 'Closest Triad'
        DataRepresentation1.Pickable = 1
        DataRepresentation1.CustomBoundsActive = [0, 0, 0]
        DataRepresentation1.CubeAxesGridLineLocation = 'All Faces'
        DataRepresentation1.SelectionRepresentation = 'Wireframe'
        DataRepresentation1.SelectionPointLabelBold = 0
        DataRepresentation1.ColorArrayName = ('CELL_DATA', parameter)
        DataRepresentation1.SelectionPointLabelItalic = 0
        DataRepresentation1.AllowSpecularHighlightingWithScalarColoring = 0
        DataRepresentation1.SpecularColor = [1.0, 1.0, 1.0]
        DataRepresentation1.CubeAxesUseDefaultZTitle = 1
        DataRepresentation1.LookupTable = pvlookup
        DataRepresentation1.SelectionPointSize = 5.0
        DataRepresentation1.SelectionCellLabelBold = 0
        DataRepresentation1.Orient = 0
        Render()
        
        
        imgdir = "./images"
        
        # If the imgdir exists, it will remove it and then remake it
        try :
            shutil.rmtree(imgdir)
        except :
            pass        
        
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)
        
        # Print out the time steps and the number of time steps to text file        
        timeout = open("frame_times.txt", "w")
        for tstepsnum in xrange(start_frame, end_frame):
            RenderView1.ViewTime = tsteps[tstepsnum]
            timeout.write(str(tstepsnum + 1)+','+str( '%0.4f' % RenderView1.ViewTime)+'\n')
        else:
            timeout.close()
            
#        tstepstotext = open("tstepstotext.txt", "w")
#        for tstepsnum in xrange(start_frame, end_frame):
#            RenderView1.ViewTime = tsteps[tstepsnum]
#            tstepstotext.write('"Output Time: '+str( '%0.4f' % RenderView1.ViewTime)+'",''\n')
#        else:
#            tstepstotext.close()
            
        tstepstotext = open("tstepstotext.txt", "w")
        for tstepsnum in xrange(start_frame, end_frame):
            printtime = self.datetimeout[tstepsnum]
            tstepstotext.write('"'+str(printtime)+'",''\n')
        else:
            tstepstotext.close()
        
            
        framenum = 0
        # This loop will go through the user-specified timestep interval and save out the images to the specified directory
        for tstepsnum in xrange(start_frame, end_frame):
            RenderView1.ViewTime = tsteps[tstepsnum]
#            RenderView1.ViewSize = [ 1500, 1500 ]
            Render()
            
            framenum = framenum+1
            WriteImage("images/" + str(tstepsnum) +".png", Magnification=10)
            print("Image " + str(framenum) + "/" + str(total_frames) + " was exctracted: " + str(round((framenum)/float(total_frames)*100, 2)) + "% of images rendered.")
        else:
            DataRepresentation1.Opacity = 0
            ScalarBarWidgetRepresentation1 = CreateScalarBar( TextPosition=1, Title=titletype, Position2=[0.1299999999999999, 0.5], TitleOpacity=1.0, TitleFontSize=12, NanAnnotation='NaN', TitleShadow=1, AutomaticLabelFormat=1, DrawAnnotations=1, TitleColor=[1.0, 1.0, 1.0], AspectRatio=15.0, NumberOfLabels=10, ComponentTitle='', Resizable=1, DrawNanAnnotation=0, TitleFontFamily='Arial', Visibility=1, LabelFontSize=10, LabelFontFamily='Arial', TitleItalic=0, LabelBold=1, LabelItalic=0, Enabled=1, LabelColor=[1.0, 1.0, 1.0], Position=[0.8141469013006885, 0.37274368231046917], Selectable=0, UseNonCompositedRenderer=1, LabelOpacity=0.9, TitleBold=0, LabelFormat='%-#6.3g', Orientation='Vertical', LabelShadow=0, LookupTable=pvlookup, Repositionable=1 )
            GetRenderView().Representations.append(ScalarBarWidgetRepresentation1)
            Render()
            WriteImage("images/legend.png", Magnification=10)
            print("All " + str(total_frames) + " images were extracted")
#         
    def output_info(self):
        """
        Returns the total number of frames and the associated output times to a text file
        entitled adhydro_frames_info.txt. Useful when the user doesn't know the quantity
        or range of the output.
        """        
        
        parameter = self.parameter       
        print parameter
        try:
            if parameter == 'meshElementZSurface':
                max_max = self.zmax
                min_min = self.zmin          
            elif parameter != 'meshElementZSurface':
                max_max = self.netcdfpar.variables[parameter][:].max()
                min_min = self.netcdfpar.variables[parameter][:].min()
                print max_max, min_min
            
        except Exception:

            sys.exit("Invalid parameter Inputted.")
        
        self.netcdfgeo.close()
        self.netcdfpar.close() 
        
        mesh_display_xmf = XDMFReader( guiName="mesh_display.xmf", FileName='./mesh_display.xmf')
        ##Here it is being determined how many time steps there are in order to extract all these as images later
        tsteps = mesh_display_xmf.TimestepValues
    
        # Fixes a bug if there is only one value for the output at time 0.0
        if tsteps == 0.0:
            tsteps = [0.0]
        elif tsteps != 0.0:
            pass
        

        tstepsnum = len(tsteps)
        print("There are a total number of " + str(tstepsnum) + " output steps that can be rendered.")
        
        # Print out the time steps and the number of time steps to text file        
        timeout = open("adhydro_frames_info.txt", "w")
        for tstepsnum in xrange(0, tstepsnum):
            timeout.write(str(tstepsnum + 1)+','+str( '%0.4f' % tsteps[tstepsnum])+'\n')
        else:
            timeout.close()
            
        print("You can find specific information about the output in the adhydro_frames_info.txt")


 


    

                
    