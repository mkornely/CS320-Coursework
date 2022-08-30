# project:p5

# submitter:mkornely

# partner:none 

# hours:12

import time
import sys
import json 
import netaddr
import re
import pyproj
import geopandas
from shapely.geometry import Polygon, box, Point
import pandas as pd
from zipfile import ZipFile, ZIP_DEFLATED
 

index=0
previousip=0
df=pd.read_csv("ip2location.csv")


def region(zips):
    global index
    with ZipFile(zips[0], "r", compression=ZIP_DEFLATED) as zf:
        with zf.open("rows.csv", "r") as f: 
            df=pd.read_csv(f)        
    
    df['ip']=df['ip'].apply(lambda x: x[:-3] + "000") 
    df['ip']=df['ip'].apply(lambda x: int(netaddr.IPAddress(x)))
    df.sort_values(by=['ip'],inplace=True)
    
    df["region"] = df["ip"].apply(lambda ip: ip_check([ip])[0]["region"])

    with ZipFile(zips[1], "w", compression=ZIP_DEFLATED) as zf:
        with zf.open("rows.csv", "w") as f:
            df.to_csv(f, index=False)
    
     
def ip_check(ips):
    global index, previousip,df
    jsonlist=[] 
    df_length=len(df)
    
    for ip in ips:
        before=time.time()
        ip_json= {}
        int_ip= int(netaddr.IPAddress(ip))

        if(int_ip==previousip):
            after=time.time()
            ip_json['ip']=ip
            ip_json['int_ip']=int_ip
            ip_json['region']=df.at[index,'region']
            ip_json['ms']=after-before 
            jsonlist.append(ip_json) 
            break; 
            
        elif(int_ip<=previousip):
            for rowindex in range(index,0,-1):
                if(int_ip>=df.at[rowindex,'low'] and int_ip<=df.at[rowindex,'high']):
                    after=time.time()
                    ip_json['ip']=ip
                    ip_json['int_ip']=int_ip
                    ip_json['region']=df.at[rowindex,'region']
                    ip_json['ms']=after-before 
                    jsonlist.append(ip_json) 
                    index=rowindex
                    previousip=int_ip
                    break; 

        else:
            for rowindex in range(index, df_length):
                if(int_ip>=df.at[rowindex,'low'] and int_ip<=df.at[rowindex,'high']):
                    after=time.time()
                    ip_json['ip']=ip
                    ip_json['int_ip']=int_ip
                    ip_json['region']=df.at[rowindex,'region']
                    ip_json['ms']=after-before 
                    jsonlist.append(ip_json) 
                    index=rowindex
                    previousip=int_ip
                    break; 
    
    return jsonlist
            
    
    
def zipcode(zip_file):
    file_list=[]
    zipcodes=[]
    
    with ZipFile(zip_file) as zf:
        for i in zf.namelist():
            if(i.endswith('-index.htm') or i.endswith('-index.html')):
                file_list.append(i)
        
        for htmfile in file_list:
            with zf.open(htmfile, 'r') as file:
                data=str(file.read())
            
            address=re.findall(r"(?:NY|IL|CA|WI)\s\d{5}(?:\-\d{4})?",data)
            for x in address:
                zipcode=re.findall(r"\d{5}(?:\-\d{4})?",x) 
                zipcodes.append(zipcode[0])
    return(set(zipcodes))
                    

def geo(espg,svg_name):
    with ZipFile("server_log2.zip", "r", compression=ZIP_DEFLATED) as zf:
        with zf.open("rows.csv", "r") as f: 
            df=pd.read_csv(f)
            
    frequency=df['region'].value_counts().to_frame().reset_index()
    
    world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))
    crs = pyproj.CRS.from_epsg(espg)
    
    
    world["colorname"]="gray"
    for i in range(0,len(frequency)):
        corresponding_frame=world.loc[world['name']==frequency.at[i,'index'],'colorname']
        if(frequency.at[i,'region']>=1000):
            if(not corresponding_frame.empty):
                world.at[world['name'] == frequency.at[i,'index'],'colorname']='red'
        elif(frequency.at[i,'region']>=1):
            if(not corresponding_frame.empty):
                world.at[world['name'] == frequency.at[i,'index'],'colorname']='orange'

                
    window = box(crs.area_of_use.west, crs.area_of_use.south, crs.area_of_use.east, crs.area_of_use.north)
    world["geometry"] = world["geometry"].intersection(window)
    world = world[~world.is_empty]
    
    ax=world.to_crs(crs).plot(color=world["colorname"])
    ax.get_figure().savefig(svg_name)

    
    
        
def main():
    if len(sys.argv) < 2:
        print("usage: main.py <command> args...")
    
    elif sys.argv[1] == "ip_check":
        ips = sys.argv[2:]
        print(json.dumps(ip_check(ips)))
    
    elif sys.argv[1]=="region":
        zips=sys.argv[2:]
        region(zips)
    
    elif sys.argv[1]=="zipcode":
        zip_file=sys.argv[2]
        zipcodes=(zipcode(zip_file))
        for z in zipcodes:
            print(z)
    
    elif sys.argv[1]=="geo":
        espg=sys.argv[2]
        svg=sys.argv[3]
        geo(espg,svg)
    
    else:
        print("unknown command: "+sys.argv[1])

if __name__ == '__main__':
     main()       
        
        
        
        
    
    









