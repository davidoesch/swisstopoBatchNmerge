#!/usr/bin/env python
###############################################################################
# $Id: swisstopobatch.py 2021
#
# 
# Purpose:  Download swisstopo data see https://github.com/davidoesch/swisstopo-batchNmerge 
# Author:   David Oesch
#
#  usage : 
# TODO: Usage should appear when running the command empty
# TODO: Parameters in all caps is unusual (parameters are small caps most of the time
# TODO: Location and product paramenter need to be specified together. This needs to be mentioned
#           GUI : python swisstopobatchGUI.py 
#           GUI with proxy: python swisstopobatchGUI.py --PROXY http://proxy_url:proxy_port
#           CLI python swisstopobatchGUI.py --CSV "C:\Downloads\ch.swisstopo.swissimage-dop10-5H5DQOGd.csv" --noGUI 1 --noMERGE 1 --PROXY http://proxy_url:proxy_port
#           CLI python swisstopobatchGUI.py --URL "https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.pixelkarte-farbe-pk50.noscale/items?bbox=7.43,46.95,7.69,47.10" --noGUI 1 --noCROP 1 --noMERGE 1 --PROXY http://proxy_url:proxy_port
#           CLI python swisstopobatchGUI.py --LOCATION "Trimmis" --PRODUCT "ch.swisstopo.pixelkarte-farbe-pk50.noscale"  --noGUI 1 --noMERGE 1 --noCROP 1 --PROXY http://proxy_url:proxy_port
###############################################################################
# to do
# - add cliping geotiff based on ZIP PLZ Ortschaften using gdal and a shapefile
# - GUI selection place: https://github.com/TomSchimansky/TkinterMapView map_with_customtiktinkert, try to collect point with drawing points/rectangel and then get from string minmax of lat lon

# - LIDAR las support
# - error handling
# - Naming Convention: function and Var needs to be consistent

import argparse
import csv
import customtkinter
import gdal_merge as gm
import json
import math
import nested_lookup
import numpy as np
import os
import progressbar
import requests
import shutil 
import sys
import tkinter
import tkintermapview
import time
# TODO: requests already imported above. Use that instead of loading another url/request library
import urllib.request
from osgeo import gdal
from pyproj import Transformer
from typing import Union
import webbrowser
from requests.exceptions import Timeout


#os.environ['PROJ_LIB'] = 'C:\Program Files\Python39\Lib\site-packages\osgeo\data\proj'
#runtime_hooks=['hook.py']

#import rasterio #follow this guide for win10 https://github.com/mapbox/rasterio/issues/1963#issuecomment-672262445


# List of supported formats
# TODO: should come from stac
supportedformats = ['.tif', '.png', '.tiff', '.TIFF']
# suuported products
# TODO: hardcoded. You need to adapt the code for every dataset that is added. Add command to scan it and store
# in a cache locally

#StandarVars
GUI_Version="v1.3.0"
homedir = os.getcwd() 
pbar = None
nonImageLayers='swissalti'


#check if GUI Version is the same as the one github
try:
    response = requests.get("https://api.github.com/repos/davidoesch/swisstopoBatchNmerge/releases/latest")
except Timeout:
    print("Your internet connection is not working. Please check your connection and try again.")
    sys.exit(1)
github_version = response.json()['tag_name']
if (response.json()["name"]) != GUI_Version:
    print("You are using: "+GUI_Version+" New version available:"+github_version+" Download it from https://github.com/davidoesch/swisstopoBatchNmerge")
    GET_NEWVERSION=("New version available:")
else:
    GET_NEWVERSION=""

def callback():
    webbrowser.open_new("https://github.com/davidoesch/swisstopoBatchNmerge")

customtkinter.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

choices = {
    'Luftbild 10cm': 'ch.swisstopo.swissimage-dop10',
    'Landeskarte 1:10': 'ch.swisstopo.landeskarte-farbe-10',
    'Landeskarte 1:25': 'ch.swisstopo.pixelkarte-farbe-pk25.noscale',
    'Landeskarte 1:50': 'ch.swisstopo.pixelkarte-farbe-pk50.noscale',
    'Landeskarte 1:100': 'ch.swisstopo.pixelkarte-farbe-pk100.noscale',
    'Landeskarte 1:200': 'ch.swisstopo.pixelkarte-farbe-pk200.noscale',
    'Höhenmodell': 'ch.swisstopo.swissalti3d',
}


choices_data = choices.items()
choices_list = list(choices_data)
choices_arr = np.array(choices_list)
#TOD DO create a product array: <product name> <technical layernmane> <wmts file extension> <files size download>
#CHOICES_ARR=np.array([
#        ['Luftbild 10cm', 'ch.swisstopo.swissimage-dop10','jpeg','40'],
#        ['Landeskarte 1:10', 'ch.swisstopo.landeskarte-farbe-10','png','60']
#        ])
#get second tuple from CHOICES_ARR where first element is 'Landeskarte 1:10'
#print(CHOICES_ARR[np.where(CHOICES_ARR[:,0]=='Landeskarte 1:10')[0][0],1])


def humansize(nbytes):
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (f, suffixes[i])


def osm_to_decimal(tile_x: Union[int, float], tile_y: Union[int, float], zoom: int) -> tuple:
    """ converts internal OSM coordinates to decimal coordinates """

    n = 2.0 ** zoom
    lon_deg = tile_x / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * tile_y / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg



# Function for opening the 
# file explorer window
def browseFiles():
    # In variabel names, be as specific as possible (what it is)
    CSV_filepath = tkinter.filedialog.askopenfilename(initialdir = "/",title = "Select a File",filetypes = (("Text files","*.csv*"),("all files","*.*")))
    # Change label contents
    label_file_explorer.configure(text="PROCESSING: "+CSV_filepath+" ...")
    # No need to create a variable, set some magic string to it and pass it to a function
    # Be explicit about what you do
    processCSV(CSV_filepath,None)
    label_file_explorer.configure(text="FINISHED: "+CSV_filepath+".tif  ")
    
# Function to retrieve items for an AOI	      
#gettingitemlist 
def getitems(productname,LLlon,LLlat,URlon,URlat,first100):
    
    itemsrequest = requests.get("https://data.geo.admin.ch/api/stac/v0.9/collections/"+productname+"/items?bbox="+LLlon+","+LLlat+","+URlon+","+URlat) #cal on STAC API
    #print("https://data.geo.admin.ch/api/stac/v0.9/collections/"+productname+"/items?bbox="+LLlon+","+LLlat+","+URlon+","+URlat)
    
    itemsresult = json.loads(itemsrequest.content)
    #find elements in the list itemsresult where the key "properties" has the value "download"
    assets=(nested_lookup.nested_lookup('assets', itemsresult)) #go throug nested results
    count=0
  
    if len(itemsresult['links'])>=6:
        morethan100=1
    else:
        morethan100=0
    
    #Take the pagination into account':
    if len(itemsresult['links'])>=6 and first100==0:        
        pagination=1
        while pagination==1:
            nextpage=itemsresult['links'][5]['href']
            itemsrequest = requests.get(nextpage)
            itemsresult = json.loads(itemsrequest.content)
            assets=np.append(assets,(nested_lookup.nested_lookup('assets', itemsresult)))
            
            if len(itemsresult['links'])>=6 and itemsresult['links'][5]['rel']=='next':
                pagination=1
                print("Collecting Download URLs: "+str(count*100))
                count=count+1
            else:
                pagination=0
                assets=assets.tolist()
    else:
        pass
   
    
    itemsfiles=(nested_lookup.nested_lookup('href', assets))
    
    #edge case _krel_ : swisstopo provides also grey an relief free raster maps ,we go only for krel
    # TODO: make special cases generic (outsource to dedicated function that is genereic for similar special cases)
    # in this case something like 'filter_if_contains(list, term)'. There might be even a ready-made python lib/function
    # for that -> https://www.kite.com/python/answers/how-to-filter-a-list-in-python
    krel=[i for i in itemsfiles if "_krel_" in i]
    if len(krel) != 0 :
        itemsfiles=krel
    
    #edge case swissimage_ : swisstopo provides different spatiale resolution we go for the 0.1 ,we go only for krel
    # TODO: See, you repeat the same code here for another special case
    highres=[i for i in itemsfiles if "_0.1_" in i]
    if len(highres) != 0 :
        itemsfiles=highres


    #edge case swissalti : swisstopo provides different spatiale resolution we go for the 0.1 ,we go only for krel
    # TODO: See, you repeat the same code here for another special case
    if productname == 'ch.swisstopo.swissalti3d':
        tiff=[i for i in itemsfiles if ".tif" in i]
        if len(tiff) != 0 :
            itemsfiles=tiff
        highres=[i for i in itemsfiles if "_0.5_" in i]
        if len(highres) != 0 :
            itemsfiles=highres
      
    #edge case creation date get the most recent one
    
    #split the name of the file to get the dates etc
    itemdate=[]
    itemblatt=[]
    itemend=[]
    itemname=[]
    for i in itemsfiles:     
        x=(os.path.basename(i))
        x=x.split("_",3)
        itemblatt.append(x[2])
        itemdate.append(x[1])
        itemend.append(x[3])
        itemname.append(x[0])

    #sort the list by date
    latest_itemsfiles=[]
    i=0
    while i < len(itemblatt):

        #find index of duplicates in itemblatt
        y=itemblatt[i]
        indices = [idx for idx, s in enumerate(itemblatt) if y in s]
        #datelist
        datelist=[]
        for idx in indices:
            datelist.append(itemdate[idx])
        datemax=max(datelist)
        latest_itemsfiles.append("https://data.geo.admin.ch"+"/"+productname+"/"+itemname[i]+"_"+datemax+"_"+itemblatt[i]+"/"+itemname[i]+"_"+datemax+"_"+itemblatt[i]+"_"+itemend[i])
        i=i+1
    #remove duplicates
    itemsfiles= list(dict.fromkeys(latest_itemsfiles))
    return itemsfiles,morethan100

# Function to create a CSV for import	
def createCSV(productname,LLlon,LLlat,URlon,URlat) :
    # TODO: Happy path programming. Basic error handling should be added. Try blocks.
    # Robust code/service is the result of well designed  error handling
    #preparing filename
    coords=(LLlon+"_"+LLlat+"_"+URlon+"_"+URlat)
    CSV_filepath=os.path.join(homedir,(productname+coords+".csv"))
    
    itemsfiles=getitems(productname,LLlon,LLlat,URlon,URlat,0)
    itemsfiles=itemsfiles[0]
    
    #create temporaryCSV file
    with open(CSV_filepath, 'w') as f:
        for item in itemsfiles:
            f.write("%s\n" % item)
    return(CSV_filepath)

def cropRaster(inputRaster,outputRaster,bbox): #bbox = (ULx,ULy,LRx,LRy)
    transformer = Transformer.from_crs("epsg:4326", "epsg:2056")# transform
    bbox95=(transformer.transform(bbox[3],bbox[0]))+(transformer.transform(bbox[1],bbox[2]))
    # Create variable, then return nothing?
    result=gdal.Translate(outputRaster,inputRaster, projWin = bbox95) 
    # Just omitting the return statement will return None
    return()

# There might be a better way to handle this
def show_progress(block_num, block_size, total_size):
    global pbar
    widgets = [ 'Progress: ' , progressbar.Percentage(),  ' ' ,
                    progressbar.Bar(marker= '#' , left= '[' , right= ']' ),
                    ' ' , progressbar.ETA(),  ' ' , progressbar.FileTransferSpeed()]
    if pbar is None:
        pbar = progressbar.ProgressBar(widgets=widgets, maxval=total_size).start()
        pbar.start()

    downloaded = block_num * block_size
    if downloaded < total_size:
        pbar.update(downloaded)
    else:
        pbar.finish()
        pbar = None
# Warn if there is not enough free space in dir etc,
def check_local_system(gettempdir,filename,lines) :
    file_stats = os.stat(filename)
    requiredspaceGB=((file_stats.st_size / (1024 * 1024 * 1024)))*lines
    free_space = shutil.disk_usage(gettempdir).free
    free_space_gb = free_space / 1024 / 1024 / 1024
    
    low_space_message = ('The default temporary directory '+str(gettempdir)+' has '+str(round(free_space_gb,3))+' GB of free space available. Downloading/merging the selected data takes approximately '+str(round(requiredspaceGB,3))+' GB of temporary storage. Consider smaller extent or add disk space  to your system.')

    if free_space_gb < requiredspaceGB :
        print("!!!!!!!!!!!!!!!!!!!!!   WARNING  !!!!!!!!!!!!!!!!!!!!")
        print(low_space_message)
        
        sys.exit()
        return
    else :
        low_space_message=(str(round(requiredspaceGB,3))+"GB will be downloaded. Free space available: "+(str(round(free_space_gb,3))+" GB")) 

    
    return(low_space_message) 
   
# Function to derive bbox/geometry from Location name
def LocationGeomBBOX(location) :
    # This function uses 2 api calls. But using the swissboundaries3d layer, it could be done in one call with the identify and/or find function
    # Also, very happy path programming
    #BBOX via API call
    apirequest = requests.get("https://api3.geo.admin.ch/rest/services/api/SearchServer?searchText="+location+"&type=locations&origins=gg25&geometryFormat=geojson&sr=4326")
    apiresult = json.loads(apirequest.content)
    bbox=apiresult['features'][0]['properties']['geom_st_box2d']
    featureId=apiresult['features'][0]['properties']['featureId']
    
    #Geometry
    apirequest = requests.get("https://api3.geo.admin.ch/rest/services/api/MapServer/ch.swisstopo.swissboundaries3d-gemeinde-flaeche.fill/"+featureId+"?returnGeometry=true&sr=4326")
    apiresult = json.loads(apirequest.content)
    geometry=apiresult['feature']['geometry']['rings'][0]
    return(geometry,bbox)

def mergeRaster(iteration,merged,temp_merged,filename,name,ordername,filename_ext,homedir):
    if iteration == 0 :
        if os.path.exists(temp_merged):
            os.remove(temp_merged)
        else:
            os.rename(filename,temp_merged)   #move first file as current temp merge file
            
    else:
        print("merging file: ",name)
        
        if name.find(nonImageLayers) != -1: #TIFF with LZW
            gm.main(['', '-o', ordername+"_merged"+filename_ext[1], ordername+"_temp_merged"+filename_ext[1],name,'-co','COMPRESS=LZW']) 
        else:#TIFF with JPEG 
            gm.main(['', '-o', ordername+"_merged"+filename_ext[1], ordername+"_temp_merged"+filename_ext[1],name,'-co','COMPRESS=JPEG','-co','PREDICTOR=2','-co','TILED=YES','-co','TILED=YES','-co','BLOCKXSIZE=512','-co','BLOCKYSIZE=512','-co','PHOTOMETRIC=YCBCR','-ot','Byte']) 

        os.remove(temp_merged) #move iniitial
        os.remove(filename)
        os.rename(merged,temp_merged)
        print((check_local_system(homedir,temp_merged,1)+ " will be used up for merging the next image together"))
    return

# Name is not specific, uses other naming conventions as functions above
# In general, different naming conventions are used for functions and variables.
# BEtter consistency increases readability of code (code is written once, and read
# 100 times)
def LocationProduct(Loc,Prod):
    GeomBBOX=LocationGeomBBOX(Loc)
    coords=GeomBBOX[1].replace("BOX(","")
    coords=coords.replace(")","")
    coords=coords.replace(","," ")
    coords=coords.split(" ")  
    CSV_filepath=createCSV(Prod,coords[0],coords[1],coords[2],coords[3])
    bbox= (coords[0],coords[1],coords[2],coords[3])
    processCSV(CSV_filepath,bbox)
    
# processCSV what?
def processCSV(CSV_filepath,geom):	
    
    filecsv=os.path.split(os.path.abspath(CSV_filepath))# OS path to CSV
    #extracting variables
    downloaddir=filecsv[0] #OS path to download
    ordername=filecsv[1] #ordername
    os.chdir(downloaddir) #go to downloadir
    
    #determine number files to download
    file = open(os.path.normpath(CSV_filepath))
    reader = csv.reader(file)
    lines= len(list(reader))
   
    # For every line in the file do
    for iteration, url in enumerate(open(os.path.normpath(CSV_filepath))):
        # Split on the rightmost / and take everything on the right side of that
        name = str.rstrip(url.rsplit('/', 1)[-1])
        #print(name)
        # Combine the name and the downloads directory to get the local filename
        filename = os.path.join(downloaddir, name)
        filename_ext=os.path.splitext(name)
        temp_merged=os.path.join(downloaddir,ordername+'_temp_merged'+filename_ext[1])
        merged=os.path.join(downloaddir,ordername+'_merged'+filename_ext[1])
        result=os.path.join(downloaddir,ordername+filename_ext[1])
        if filename_ext[1] not in supportedformats :
            print(filename+" is NOT one of the supported formats, only download" , supportedformats)
            args.noMERGE = 1
           
        # Download the file if it does not exist
        if not os.path.isfile(filename):
            print(" ")
            print(" ")
            print("downloading file: ",iteration+1," of ",lines)
            urllib.request.urlretrieve(url, filename,show_progress)

            if iteration == 0 :
                # sometimes you print in the function, sometimes outside of it
                low_space_message=check_local_system(homedir,filename,lines)
                print(" ")
                print("---------------------------------------------------------------------")
                print(low_space_message+ " for downloaded data needed, might take some time")
                print("---------------------------------------------------------------------") 
                print(" ")                
            if args.noMERGE == 0 :
                mergeRaster(iteration,merged,temp_merged,filename,name,ordername,filename_ext,homedir)
                
    #rename data
    if geom is not None and len(geom) == 4 and args.noCROP == 0 and args.noMERGE == 0: #geom has 4 bbox coordinates
        print("Clipping...")
        
        cropRaster(temp_merged,merged,geom)
        
        os.remove(temp_merged) #delete iniitial
    if args.noMERGE == 1: 
        print("Ergebnis in "+downloaddir)
    
    if args.noMERGE == 0: 
        if os.path.exists(result):
            print(" Result "+result+" already existed, delete it if you want reprocess")
        else :
            if os.path.exists(temp_merged):
                os.rename(temp_merged,result)
            if os.path.exists(merged):
                os.rename(merged,result)
        print(" ")
        print(" ")
        print("Ergebnis in "+result)
        os.chdir(homedir)
    #exit?
    return


#main partition
#checking arguments
# doc missing

parser = argparse.ArgumentParser(description='--h for all options , eg PROXY http://proxy_url:proxy_port')
parser.add_argument("--CSV")
parser.add_argument("--URL")
parser.add_argument("--LOCATION")
parser.add_argument("--PRODUCT")
parser.add_argument("--noCROP", type=int, default=0)
parser.add_argument("--noGUI", type=int, default=0)
parser.add_argument("--noMERGE", type=int, default=0)
parser.add_argument("--PROXY")
args = parser.parse_args()

#remove only test below
#args.URL="https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.landeskarte-farbe-10/items?bbox=7.43,46.95,7.69,47.10"
#args.noGUI=1

if args.PROXY is not None : 
 os.environ['HTTP_PROXY'] = args.PROXY
 
if args.noGUI == 0 :
    class App(customtkinter.CTk):

        APP_NAME = "swisstopoDatenDownloader "+str(GUI_Version)
        WIDTH = 800
        HEIGHT = 500

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.title(App.APP_NAME)
            self.geometry(str(App.WIDTH) + "x" + str(App.HEIGHT))
            self.minsize(App.WIDTH, App.HEIGHT)

            self.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.bind("<Command-q>", self.on_closing)
            self.bind("<Command-w>", self.on_closing)
            self.createcommand('tk::mac::Quit', self.on_closing)

            self.marker_list = []
            
            # Product extent loading in background threads
            self.after(100, self.update_canvas_product)
            self.canvas_product_size="..."
            


            # ============ create two CTkFrames ============

            self.grid_columnconfigure(0, weight=0)
            self.grid_columnconfigure(1, weight=1)
            self.grid_rowconfigure(0, weight=1)

            self.frame_left = customtkinter.CTkFrame(master=self, width=150, corner_radius=0)
            self.frame_left.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

            self.frame_right = customtkinter.CTkFrame(master=self, corner_radius=0, fg_color=self.fg_color)
            self.frame_right.grid(row=0, column=1, rowspan=1, pady=0, padx=0, sticky="nsew")

            # ============ frame_left ============
            #pulldown menu
            self.optionmenu_1 =  customtkinter.CTkOptionMenu(master=self.frame_left,
                                                    values=[row[0] for row in choices_arr],
                                                    width=160, height=30,
                                                    command=self.loadmapproduct_event,
                                                    corner_radius=8)
            self.optionmenu_1.grid(pady=(20, 0), padx=(20, 20), row=2, column=0)
            self.optionmenu_1.set("Auswahl Datensatz")
            
            if GET_NEWVERSION != "":
                #New Version
                self.label_newversion = customtkinter.CTkLabel(master=self.frame_left,
                                                    text=GET_NEWVERSION)
                self.label_newversion.grid(pady=(20, 0), padx=(20, 20), row=3, column=0,sticky="w")
                #add download button
                self.button_newversion= customtkinter.CTkButton(master=self.frame_left,
                                                    text="Download "+github_version,
                                                    fg_color= "red",
                                                    command=callback,
                                                    width=160, height=30,
                                                    border_width=0,
                                                    corner_radius=8)
                self.button_newversion.grid(pady=(0, 0), padx=(20, 20),row=4, column=0,sticky="nsew")
            else:
                pass

            # ============ frame_right ============

            self.frame_right.grid_rowconfigure(0, weight=0)
            self.frame_right.grid_rowconfigure(1, weight=1)
            self.frame_right.grid_rowconfigure(2, weight=0)
            self.frame_right.grid_columnconfigure(0, weight=1)
            self.frame_right.grid_columnconfigure(1, weight=0)
            self.frame_right.grid_columnconfigure(2, weight=1)


            #map widget
            self.map_widget = tkintermapview.TkinterMapView(self.frame_right, corner_radius=11)
            self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(20, 20), pady=(5, 0))
            self.map_widget.set_tile_server("https://wmts.geo.admin.ch/1.0.0/ch.swisstopo.pixelkarte-farbe/default/current/3857/{z}/{x}/{y}.jpeg")  # no labels

            # set current map widget position and zoom
            self.map_widget.set_position(46.85841, 8.22548)  # center CH
            self.map_widget.set_zoom(8)

            # search
            self.entry = customtkinter.CTkEntry(master=self.frame_right,
                                                placeholder_text="Ort eingeben",
                                                width=140,
                                                height=30,
                                                corner_radius=8)
            self.entry.grid(row=0, column=0, sticky="we", padx=(20, 0), pady=20)
            self.entry.entry.bind("<Return>", self.search_event)

            self.button_5 = customtkinter.CTkButton(master=self.frame_right,
                                                    height=30,
                                                    text="Search",
                                                    command=self.search_event,
                                                    border_width=0,
                                                    corner_radius=8)
            self.button_5.grid(row=0, column=1, sticky="w", padx=(20, 0), pady=20)
            #zoom
            self.slider_1 = customtkinter.CTkSlider(master=self.frame_right,
                                                    width=200,
                                                    height=16,
                                                    from_=0, to=19,
                                                    border_width=5,
                                                    command=self.slider_event)
            self.slider_1.grid(row=0, column=2, sticky="e", padx=20, pady=20)
            self.slider_1.set(self.map_widget.zoom)
            
            #start download
            
            self.button_2 = customtkinter.CTkButton(master=self.frame_right,
                                                    text="START Download",
                                                    fg_color= "red",
                                                    command=self.start_download_event,
                                                    width=120, height=30,
                                                    border_width=0,
                                                    corner_radius=8)
            self.button_2.grid(row=2, column=2, sticky="e", padx=20, pady=20)

            #size of the download
            self.label_size = customtkinter.CTkLabel(master=self.frame_right,
                                                    text=self.canvas_product_size)
            self.label_size.grid(row=2, column=1, pady=20, padx=20, sticky="e")
            


            #TODO log in widget
            #------------------------------------------------------
            #self.log_widget = tkinter.scrolledtext.ScrolledText(self.frame_right, height=4,width=120,  font=("consolas", "8", "normal"))
            #self.log_widget.grid(row=2, columnspan=2, sticky="e", padx=20, pady=20)
            #logger = PrintLogger(self.log_widget)
            #sys.stdout = logger
            #sys.stderr = logger
            print("Produkt und Perimeter auswählen...")

        def search_event(self, event=None):
            self.map_widget.set_address(self.entry.get())
            self.slider_1.set(self.map_widget.zoom)

        def slider_event(self, value):
            self.map_widget.set_zoom(value)

        def update_canvas_product(self):
            #get upper coordinates
            LR=osm_to_decimal(self.map_widget.lower_right_tile_pos[0],self.map_widget.lower_right_tile_pos[1],self.map_widget.last_zoom)
            UL=osm_to_decimal(self.map_widget.upper_left_tile_pos[0],self.map_widget.upper_left_tile_pos[1],self.map_widget.last_zoom)
            
            #dont' calculate if the product is overview
            if  self.optionmenu_1.current_value == "Auswahl Datensatz" :
                self.LR_last = LR
                self.UL_last = UL
                self.last_product = self.optionmenu_1.current_value    
            # if the BBox is changed, calculate the new extent
            elif LR != self.LR_last or UL != self.UL_last or self.optionmenu_1.current_value != self.last_product:
                #get the number of files neede for download product, call only the first 100 files
                items=getitems(choices[self.optionmenu_1.current_value],str(UL[1]),str(LR[0]),str(LR[1]),str(UL[0]),1)
                numberofdownloads=len(items[0])
                
                if items[1] == 1:
                    prefix = "more than "
                else:
                    prefix = "                ~ "
                
                #size of the download
                self.label_size = customtkinter.CTkLabel(master=self.frame_right,text=prefix+humansize(numberofdownloads*self.filesize)+ "  to download")
                self.label_size.grid(row=2, column=1, pady=20, padx=20, sticky="e")
                self.last_product = self.optionmenu_1.current_value
                self.LR_last = LR
                self.UL_last = UL
                
            else:
                pass

            # This function calls itself every 10 ms with tk.after() so that the image updates come
            # from the main GUI thread, because tkinter can only be updated from the main thread.
            self.after(10, self.update_canvas_product)
        
        def loadmapproduct_event(self, event=None):
            
            LR=osm_to_decimal(self.map_widget.lower_right_tile_pos[0],self.map_widget.lower_right_tile_pos[1],self.map_widget.last_zoom)
            UL=osm_to_decimal(self.map_widget.upper_left_tile_pos[0],self.map_widget.upper_left_tile_pos[1],self.map_widget.last_zoom)
            #Get the first file and calculate the size of the download 
            
            items=getitems(choices[self.optionmenu_1.current_value],str(8.08698),str(46.29962),str(8.18698),str(46.39962),1)
            file=urllib.request.urlopen(items[0][0])
            
            self.filesize=file.length
            self.last_product = self.optionmenu_1.current_value
           
            
            z=self.map_widget.last_zoom
            self.map_widget.tile_image_cache={}
            if choices[self.optionmenu_1.current_value] =="ch.swisstopo.swissalti3d":
                WMTS_name="ch.swisstopo.swissalti3d-reliefschattierung"
                WMTS_fileextension=".png"
            elif choices[self.optionmenu_1.current_value] =="ch.swisstopo.swissimage-dop10":
                WMTS_name="ch.swisstopo.swissimage-product"
                WMTS_fileextension=".jpeg"
            elif choices[self.optionmenu_1.current_value] =="ch.swisstopo.landeskarte-farbe-10":
                WMTS_name=choices[self.optionmenu_1.current_value]
                WMTS_fileextension=".png"
            else:
                WMTS_name=choices[self.optionmenu_1.current_value]
                WMTS_fileextension=".jpeg"
            
            self.map_widget = tkintermapview.TkinterMapView(self.frame_right, corner_radius=11)
            self.map_widget.grid(row=1, rowspan=1, column=0, columnspan=3, sticky="nswe", padx=(20, 20), pady=(5, 0))
            self.map_widget.set_tile_server("https://wmts.geo.admin.ch/1.0.0/"+WMTS_name+"/default/current/3857/{z}/{x}/{y}"+WMTS_fileextension)  # no labels        
            # set current map widget position and zoom
            self.map_widget.set_position((LR[0]+UL[0])/2, (LR[1]+UL[1])/2)  # center current poistions
            self.map_widget.set_zoom(z)
            #self.update_canvas_product(self)
            
            

        def start_download_event(self):
            print("Starting download...")
            LR=osm_to_decimal(self.map_widget.lower_right_tile_pos[0],self.map_widget.lower_right_tile_pos[1],self.map_widget.last_zoom)
            UL=osm_to_decimal(self.map_widget.upper_left_tile_pos[0],self.map_widget.upper_left_tile_pos[1],self.map_widget.last_zoom)

            
            if self.optionmenu_1.current_value == 'Auswahl Datensatz':
                print("******************")
                print("Datensatz auswählen!")
            else:
                product= choices[self.optionmenu_1.current_value]

                CSV_filepath=createCSV(product,str(UL[1]),str(LR[0]),str(LR[1]),str(UL[0]))
                bbox= (UL[1],LR[0],LR[1],UL[0])
                processCSV(CSV_filepath,bbox)
                self.label_size = customtkinter.CTkLabel(master=self.frame_right,text_color="red",text="        ...download complete.")
                self.label_size.grid(row=2, column=1, pady=20, padx=20, sticky="e")
        

        def on_closing(self, event=0):
            self.destroy()

        def start(self):
            self.mainloop()


    if __name__ == "__main__":
        app = App()
        app.start()

# the below should be in an else statement, because otherwise
# combination of parameters have behaviour that is hard to
# understand (call with --noGUI=0 and --CSV=1 will start GUI and
# after that will do something with CSV
#CSV swisstopo CSV use case
if args.CSV is not None :
    processCSV(args.CSV,None)

#URL use case
if args.URL is not None :
    #preparing filename
    coords=args.URL.split("bbox=",1)[1] #coordinates LLlon,LLlat,URlon,URlat
    coords=coords.split(",")
    homedir = os.getcwd() #get home dir
    splitURL=args.URL.split("/")#get productname
    bbox= (coords[0],coords[1],coords[2],coords[3])
    CSV_filepath=createCSV(splitURL[7],coords[0],coords[1],coords[2],coords[3])
    processCSV(CSV_filepath,bbox)

#LOCATION and PRODUCT use case   
if args.LOCATION is not None and args.PRODUCT is not None :
    LocationProduct(args.LOCATION,args.PRODUCT)
    
sys.exit()
