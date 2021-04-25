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
# - GUI selection place
# - LIDAR las support
# - error handling
# - Naming Convention: function and Var needs to be consistent


import csv, sys
from sys import exit
import requests,json
import json
from nested_lookup import nested_lookup
# TODO: requests already imported above. Use that instead of loading another url/request library
import urllib.request
import os
import argparse
import gdal_merge as gm
from tkinter import *
from tkinter import filedialog
from osgeo import gdal
from pyproj import Transformer
import  progressbar
import shutil 

#os.environ['PROJ_LIB'] = 'C:\Program Files\Python39\Lib\site-packages\osgeo\data\proj'
#runtime_hooks=['hook.py']

#import rasterio #follow this guide for win10 https://github.com/mapbox/rasterio/issues/1963#issuecomment-672262445


# List of supported formats
# TODO: should come from stac
supportedformats = ['.tif', '.png', '.tiff', '.TIFF']
# suuported products
# TODO: hardcoded. You need to adapt the code for every dataset that is added. Add command to scan it and store
# in a cache locally
choices = {
    'SWISSIMAGE 10cm': 'ch.swisstopo.swissimage-dop10',
    'Landeskarte 1:10': 'ch.swisstopo.landeskarte-farbe-10',
    'Landeskarte 1:25': 'ch.swisstopo.pixelkarte-farbe-pk25.noscale',
    'Landeskarte 1:50': 'ch.swisstopo.pixelkarte-farbe-pk50.noscale',
    'Landeskarte 1:100': 'ch.swisstopo.pixelkarte-farbe-pk100.noscale',
    'Landeskarte 1:200': 'ch.swisstopo.pixelkarte-farbe-pk200.noscale',
    'swissALTI3D': 'ch.swisstopo.swissalti3d',
}

#StandarVars
homedir = os.getcwd() 
pbar = None
nonImageLayers='swissalti'


# Function for opening the 
# file explorer window
def browseFiles():
    # In variabel names, be as specific as possible (what it is)
    CSV_filepath = filedialog.askopenfilename(initialdir = "/",title = "Select a File",filetypes = (("Text files","*.csv*"),("all files","*.*")))
    # Change label contents
    label_file_explorer.configure(text="PROCESSING: "+CSV_filepath+" ...")
    # No need to create a variable, set some magic string to it and pass it to a function
    # Be explicit about what you do
    processCSV(CSV_filepath,None)
    label_file_explorer.configure(text="FINISHED: "+CSV_filepath+".tif  ")
    
      

# Function to create a CSV for import	
def createCSV(productname,LLlon,LLlat,URlon,URlat) :
    # TODO: Happy path programming. Basic error handling should be added. Try blocks.
    # Robust code/service is the result of well designed  error handling
    #preparing filename
    coords=(LLlon+"_"+LLlat+"_"+URlon+"_"+URlat)
    CSV_filepath=os.path.join(homedir,(productname+coords+".csv"))
    
    #gettingitemlist
    itemsrequest = requests.get("https://data.geo.admin.ch/api/stac/v0.9/collections/"+productname+"/items?bbox="+LLlon+","+LLlat+","+URlon+","+URlat) #cal on STAC API
    itemsresult = json.loads(itemsrequest.content)
    assets=(nested_lookup('assets', itemsresult)) #go throug nested results
    itemsfiles=(nested_lookup('href', assets))
    
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
        # what is breakpoint()?
        exit()
        return
    else :
        low_space_message=(str(round(requiredspaceGB,3))+"GB of "+(str(round(free_space_gb,3))+" GB remaining")) 

    
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
        print("Ausschneiden ...")
        
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
    exit


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

if args.PROXY is not None : 
 os.environ['HTTP_PROXY'] = args.PROXY
 
if args.noGUI == 0 :
    # Create the root window
    window = Tk()
    # Set window title
    window.title('SwisstopoBatchNmerge')
    label_file_explorer = Label(window, 
        text = "PREPARING ... ")
    Label(text = " ").grid(column=0)
    Label(text = " Download und Zusammensetzen ").grid(column=0)
    Label(text = " ").grid(column=0)
    Button(text = "Auswahl swisstopo CSV & START",command = browseFiles).grid(column=0)
    Label(text = " ").grid(column=0)
    Button(text = "EXIT",command = exit).grid(column=0)
    Label(text = " ").grid(column=0)
    label_file_explorer.grid(column = 0)
    
    window.mainloop()

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
    
exit
