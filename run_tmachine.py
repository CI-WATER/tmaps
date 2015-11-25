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

'''

import os
import sys
import shutil



def runtm(cores, tmcname, tmc_ct_dir, mapxmin, mapxmax, mapymin, mapymax):
    '''
    This is a script to run the Time Machine Video creator from the terminal. It
    will write out the necessary project file definition.tmc which tells the ct.rb
    code what Time Machine options will be used. It also writes out the updated 
    css files for the legend overlay and the output times of the frames.
    '''

    print('Creating new text file') 
    # Name and directory of the defintion.tmc file
    defname = './tmc-1.2.1-linux/ct/'+tmcname+'.tmc/definition.tmc'

    try:
        file = open(defname,'w')   # Trying to create a new file or open one
        file.write('''{
  "sort_by": "filename",
  "source": {
    "type": "images",

    "tilesize": 512
  },
  "videosets": [
    {
      "type": "h.264",
      "label": "720p",
      "size": [
        1256,
        720
      ],
      "quality": 24,
      "fps": "4"
    }
  ]
}''')        
        file.close()
    except:
        print('Something went with generating the definition.tmc file')
        sys.exit(0) # quit Python

    # Erase the files that might remain from a prior run which can cause problems
    try :
        shutil.rmtree('./tmc-1.2.1-linux/ct/'+tmcname+'.tmc/0200-tiles')
    except :
        pass
    try :
        shutil.rmtree('./tmc-1.2.1-linux/ct/'+tmcname+'.tmc/0300-tilestacks')
    except :
        pass
    try :
        shutil.rmtree('./tmc-1.2.1-linux/ct/'+tmcname+'.timemachine')
    except :
        pass
    
    os.chdir(tmc_ct_dir)
    os.system("ruby ct.rb "+ tmcname + ".tmc " + tmcname + ".timemachine -j "+ str(cores))
    
    playercss = tmcname + '.timemachine/css/customUI.css'

    try :
        shutil.copyfile('../../legend.png','./' + tmcname + '.timemachine/images/legend.png')
    except :
        print('There is not a legend image to be overlain onto the viewer. Please place a legend.png with dimensions 235x581 in the two directories up from the tmc_ct_dir')
        sys.exit(0)

    for name in os.listdir('./' + tmcname + '.timemachine/'):
        if 'crf' in name:
            video_tile_folder = name
    
    # generate an updated css file for allowing the updated legend to be visible
    try:
        file = open(playercss,'w')   # Trying to create a new file or open one
        file.write('''@charset "UTF-8";

.modisCustomPlay.ui-button {
  position: absolute;
  width: 50px;
  height: 50px;
  bottom: 7px;
  left: 21px;
  background: white;
  border: 1px solid #656565;
  border-radius: 35px !important;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  z-index: 10;
  outline: none;
}

.modisTimeText {
  position: absolute;
  top: 0px;
  width: 91px;
  height: 26px;
  font-size: 28pt;
  text-shadow: -1px 0 #656565, 0 1px #656565, 1px 0 #656565, 0 -1px #656565, 2px 2px 3px rgba(0,0,0,0.3);
  font-family: Arial, Helvetica, sans-serif;
  text-align: right;
  margin-top: -42px;
  margin-left: 14px;
  color: white;
  font-weight: lighter;
  background-color: transparent;
  border: 0px solid #656565;
  z-index: 9;
  border-radius: 3px;
  cursor: default;
}

.modisCustomToggleSpeed.ui-button {
  position: absolute;
  width: 56px;
  height: 16px;
  top: 36px;
  left: 105px;
  background: white;
  border: 1px solid #656565;
  border-radius: 3px !important;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  z-index: 10;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8pt;
  color: #656565;
  display: none;
}

.modisCustomToggleSpeed .ui-button-text {
  text-align: center;
  padding: 0px;
  padding-top: 0px;
  margin-left: 1px;
}

.toggleLock.ui-button {
  position: absolute;
  width: 20px;
  height: 16px;
  top: -6px;
  left: 124px;
  background: white;
  border: 1px solid #656565;
  border-radius: 3px !important;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  z-index: 11;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8pt;
  color: #656565;
  display: none;
}

.toggleLock .ui-button-text {
  text-align: center;
  padding: 0px;
  margin-left: 12px;
}

.toggleLock .ui-icon {
  padding: 0px;
  margin-left: -8px;
}

.toggleLockType.ui-button {
  position: absolute;
  width: 38px;
  height: 16px;
  top: 30px;
  left: 161px;
  background: white;
  border: 1px solid #656565;
  border-radius: 3px !important;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  z-index: 9;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8pt;
  color: #656565;
  display: none;
}

.toggleLockType .ui-button-text {
  text-align: center;
  padding: 0px;
  margin-left: 0px;
}

.toggleLockType .ui-icon {
  padding: 0px;
  margin-left: 0px;
}

.monthSpinnerContainer {
  left: 77px;
  top: -76px;
  position: absolute;
  cursor: pointer;
  z-index: 10;
}

.monthSpinnerTxt {
  left: 32px;
  top: 46px;
  text-shadow: -1px 0 #656565, 0 1px #656565, 1px 0 #656565, 0 -1px #656565, 2px 2px 3px rgba(0,0,0,0.3);
  position: absolute;
  font-size: 18px;
  color: white;
  width: 48px;
  text-align: center;
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 550;
}

.googleLogo {
  width: 235px;
  height: 581px;
  position: absolute;
  bottom: 80px;
  right: 15px;
  border: 0px;
  background-image: url("../images/legend.png");
  -ms-transform: scale(0.5); /* IE 9 */
  -webkit-transform: scale(0.5); /* Chrome, Safari, Opera */
  transform: scale(0.5);
  -ms-transform-origin: 100% 100%;
  -webkit-transform-origin: 100% 100%;
  transform-origin: 100% 100%;
}

.googleLogo-touchFriendly {
  bottom: 95px;
}

.customControl {
  position: absolute;
  background-color: rgba(255,255,255,0);
  height: 60px;
  left: 0px;
  right: 0px;
  bottom: 0px;
  width: auto;
  z-index: 19;
  -webkit-user-select: none;
  -khtml-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  -o-user-select: none;
  user-select: none;
}

.customTimeline {
  position: absolute;
  height: inherit;
  margin-top: 0px;
  width: auto;
}

.customTimeline-touchFriendly {
  margin-top: -29px;
}



.timeText {
  position: absolute;
  top: 0px;
  left: 41px;
  width: 80px;
  height: 25px;
  font-size: 8pt;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  font-family: Arial, Helvetica, sans-serif;
  padding-top: 5px;
  padding-bottom: 5px;
  padding-left: 37px;
  padding-right: 0px;
  color: #656565;
  font-weight: normal;
  background-color: white;
  border: 1px solid #656565;
  z-index: 6;
  border-radius: 3px;
  cursor: default;
  text-align: left;
}

.timeText-touchFriendly {
  top: -28px;
  left: 63px;
  width: 81px;
  height: 33px;
  font-size: 6pt;
}

.timeTextTour {
  left: 23px;
  width: 81px;
  padding-left: 35px;
}

.timeTextHover {
  position: absolute;
  font-size: 6pt;
  text-shadow: -1px 0 #656565, 0 1px #656565, 1px 0 #656565, 0 -1px #656565, 2px 2px 3px rgba(0,0,0,0.3);
  font-family: Arial, Helvetica, sans-serif;
  text-align: center;
  color: white;
  font-weight: normal;
  cursor: default;
  z-index: 1;
  opacity: 1;
  cursor: pointer;
  display: none;
}

.endTimeDotClickRegion {
  position: absolute;
  border: 0px;
  opacity: 0;
  cursor: pointer;
  z-index: 6;
}

.endTimeDotContainer {
  position: absolute;
  border: 0px;
}

.endTimeDot {
  border: 1px solid #656565;
  background-color: white;
  opacity: 1;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  margin: 0px auto;
}

.timeTickContainer {
  position: absolute;
  border: 0px;
}

.timeTickGrow {
  border: 1px solid white !important;
  background-color: transparent !important;
}

.timeTick {
  margin: 0px auto;
  border: 1px solid #656565;
  background-color: white;
  opacity: 1;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  border-radius: 2px;
}

.timeTickClickRegion:focus {
  outline: 0;
}

.currentTimeTick {
  position: absolute;
  border: 1px solid #656565;
  background-color: white;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  border-radius: 2px;
  z-index: 5;
}

.timeTickClickRegion {
  position: absolute;
  border: 0px;
  opacity: 0;
  cursor: pointer;
  z-index: 6;
}

.customToggleSpeed.ui-button {
  position: absolute;
  width: 55px;
  height: 23px;
  top: 30px;
  left: 75px;
  background: white;
  border: 1px solid #656565;
  border-radius: 3px !important;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  z-index: 9;
  font-family: Arial, Helvetica, sans-serif;
  font-size: 8pt;
  color: #656565;
  display: none;
}

.customToggleSpeed-touchFriendly.ui-button {
  width: 67px;
  height: 25px;
  top: 14px;
  left: 102px;
  font-size: 10pt;
}

.customToggleSpeed .ui-button-text {
  text-align: center;
  padding: 0px;
  padding-top: 3px;
}

.customPlay.ui-button {
  position: absolute;
  width: 50px;
  height: 50px;
  bottom: 20px;
  left: 20px;
  background: white;
  border: 1px solid #656565;
  border-radius: 35px !important;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
  z-index: 10;
  outline: none;
}

.customPlay-touchFriendly.ui-button {
  width: 70px;
  height: 70px;
  bottom: 30px;
}

.customHelpLabel.ui-button {
  position: absolute;
  width: 25px;
  height: 25px;
  bottom: 30px;
  right: 20px;
  background: white;
  border: 1px solid #656565;
  border-radius: 15px !important;
  box-shadow: 2px 2px 3px rgba(0,0,0,0.3);
}

.customHelpLabel-touchFriendly.ui-button {
  width: 40px;
  height: 40px;
  bottom: 44px;
  border-radius: 21px !important;
}

.customHelpLabel .ui-icon {
  margin-top: -9px;
}

.customInstructions {
  background-color: rgba(0, 0, 0, 0.5);
  position: absolute;
  top: 0px;
  left: 0px;
  bottom: 0px;
  right: 0px;
  width: auto;
  height: auto;
  z-index: 999;
  display: none;
}

.customInstructions span {
  font-size: 12px;
  color: black;
  position: absolute;
  display: block;
  line-height: 18px;
}

.customInstructions p {
  font-size: 12px;
}

.customInstructions-touchFriendly p {
  font-size: 16px;
}

.customInstructions span.customMovehelp {
  top: 30px;
  left: 110px;
  width: 140px;
  padding: 68px 0px 0px 0px;
  color: white !important;
  background-repeat: no-repeat;
  background-position: center top;
  background-image: url(../images/drag_mouse_white.png);
}

.customInstructions-touchFriendly span.customMovehelp {
  position: absoulte;
  top: 35%;
  left: 30%;
  width: 380px;
  padding: 112px 0px 0px 88px;
  background-image: url(../images/touch/drag_mouse_white.png);
}

.customInstructions span.customZoomhelp {
  background-color: white;
  border: 1px solid #656565;
  top: 150px;
  left: 67px;
  overflow: visible;
  border-radius: 3px;
}

.customInstructions-touchFriendly span.customZoomhelp {
  top: 50px;
}

.customInstructions span.modisCustomSpeedhelp {
  background-color: white;
  border: 1px solid #656565;
  bottom: 32px;
  left: 105px;
  overflow: visible;
  border-radius: 3px;
}

.customInstructions span.customSpeedhelp {
  background-color: white;
  border: 1px solid #656565;
  bottom: 35px;
  left: 74px;
  overflow: visible;
  border-radius: 3px;
}

.customInstructions-touchFriendly span.customSpeedhelp {
  bottom: 48px;
  left: 104px;
}

.customInstructions span.customZoomhelp p {
  margin: 0px -6px 0px -11px;
  padding: 12px 0px 12px 30px;
  background-repeat: no-repeat;
  background-position: center left;
  background-image: url(../images/bubble_edge_vertical_white.png);
  width: 190px;
}

.customInstructions-touchFriendly span.customZoomhelp p {
  width: 240px;
}

.customInstructions span.modisCustomSpeedhelp p {
  margin: 0px 0px -11px 0px;
  padding: 12px 15px 22px 15px;
  background-repeat: no-repeat;
  background-position: 20px 100%;
  background-image: url(../images/bubble_edge_horizontal_white.png);
  width: 190px;
}

.customInstructions-touchFriendly span.modisCustomSpeedhelp p {
  width: 290px;
}

.customInstructions span.customSpeedhelp p {
  margin: 0px 0px -11px 0px;
  padding: 12px 15px 22px 15px;
  background-repeat: no-repeat;
  background-position: 20px 100%;
  background-image: url(../images/bubble_edge_horizontal_white.png);
  width: 190px;
}

.customInstructions-touchFriendly span.customSpeedhelp p {
  width: 250px;
}''')
        file.close()
    except:
        print('Something went with generating the player.css file')
        sys.exit(0) # quit Python
        
    fileone = open('../../tstepstotext.txt', 'r')
    fileoneread = fileone.read()
    
    capture_times = tmcname + '.timemachine/tm.json'
    
    try:
        file = open(capture_times,'w')   # Trying to create a new file or open one
        file.write('''{
  "datasets": [
    {
      "id": "'''+str(video_tile_folder)+'''",
      "name": "720p"
    }
  ],
  "sizes": [
    "720p"
  ],
  "capture-times": [
''' + fileoneread + '''
  ],
  "projection-bounds": {
      "east": ''' + str(mapxmax) +''',
      "north": ''' + str(mapymax) +''',
      "south": ''' + str(mapymin) +''',
      "west": ''' + str(mapxmin) +''',
      }
}''')
        file.close()

    except:
        print('Something went wrong with generating the capture times tm.json file')
        sys.exit(0) # quit Python
        
        
        
    viewhtml = tmcname + '.timemachine/view.html'
    
    try:
        file = open(viewhtml,'w')   # Trying to create a new file or open one
        file.write('''<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8"/>

    <link href="css/snaplapse.css" rel="stylesheet" type="text/css"/>
    <link href="css/jquery-ui/smoothness/jquery-ui.custom.css" rel="stylesheet" type="text/css"/>
    <link href="css/defaultUI.css" rel="stylesheet" type="text/css"/>
    <link href="css/smallGoogleMap.css" rel="stylesheet" type="text/css"/>
    <link href="css/scaleBar.css" rel="stylesheet" type="text/css"/>
    <link href="css/visualizer.css" rel="stylesheet" type="text/css"/>
    <link href="css/annotator.css" rel="stylesheet" type="text/css"/>
    <link href="css/customUI.css" rel="stylesheet" type="text/css"/>

    <script src="js/jquery/jquery.min.js" type="text/javascript"></script>
    <script src="js/jquery/jquery-ui.custom.min.js" type="text/javascript"></script>
    <script src="js/jquery/plugins/mouse/jquery.mousewheel.min.js" type="text/javascript"></script>
    <script src="js/kinetic/kinetic.min.js" type="text/javascript"></script>
    <script src="js/org/gigapan/util.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/videoset.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/parabolicMotion.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/timelapse.js" type="text/javascript"></script>
    <script src="js/Math.uuid.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/snaplapse.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/snaplapseViewer.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/mercator.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/visualizer.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/annotator.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/scaleBar.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/smallGoogleMap.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/customUI.js" type="text/javascript"></script>

    <script src="js/org/gigapan/timelapse/defaultUI.js" type="text/javascript"></script>
    <script src="js/org/gigapan/timelapse/urlEncoder.js" type="text/javascript"></script>
    <script src="ajax_includes.js" type="text/javascript"></script>
    <script src="template_includes.js" type="text/javascript"></script>

    <script src="https://maps.google.com/maps/api/js?sensor=false&libraries=places" type="text/javascript" ></script>

    <script type="text/javascript">
      jQuery.support.cors = true;

      var url = "./";

      function init() {
        var settings = {
          url: url,
          enableEditor: true,
          onTimeMachinePlayerReady: function(viewerDivId) {
          },
          datasetType: "landsat",
          scaleBarOptions: {
            scaleBarDiv: "scaleBar1"
          },
          smallGoogleMapOptions: {
            smallGoogleMapDiv: "smallGoogleMap1"
          },
          disableTourLooping: true,
          mediaType: ".mp4",
          showFullScreenBtn: false,
          useThumbnailServer: false,
          showEditorModeButton: false
        };
        timelapse = new org.gigapan.timelapse.Timelapse("timeMachine", settings);
      }

      $(init);
    </script>
  </head>
  <body>
    <div id="timeMachine"></div>
  </body>
</html>''')
        file.close()

    except:
        print('Something went wrong with generating the capture times view.html file')
        sys.exit(0) # quit Python
    

    try:
        os.chdir(tmcname + '.timemachine/')
        os.system("ruby update_ajax_includes.rb")
    except:
        print('Capture times could not be updated')
        sys.exit(0) # quit Python

    try :
        shutil.copyfile('../../../tmaps_app_info.txt', 'tmaps_app_info.txt')
    except :
        print('No tmaps_info_app.txt found. This means one will need to be placed in the *.timemachine folder before moving it to the Tethys TMAPS app.')

    
    print ("Your timemachine video entitled " + tmcname + ".timemachine was created. It can be viewed in your browser by opening " + tmc_ct_dir + "/" + tmcname + ".timemachine/view.html")
    


                
    