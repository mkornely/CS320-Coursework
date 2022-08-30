# project:p5

# submitter:mkornely

# partner:none 

# hours:7

import time
import sys
import json 
import netaddr
import pandas as pd
from zipfile import ZipFile, ZIP_DEFLATED
import csv 
from io import TextIOWrapper


 

index=0
previousip=0

def region(zips):
    global index
    with ZipFile(zips[0], "r", compression=ZIP_DEFLATED) as zf:
        with zf.open("rows.csv", "r") as f: 
            df=pd.read_csv(f)

            
    lookup_df=pd.read_csv("ip2location.csv")
    df_length=len(lookup_df)
    df['ip']=df['ip'].apply(lambda x: x[:-3] + "000") 
    df["region"] = df["ip"].apply(lambda ip: ip_check([ip])[0]["region"])


   
    

        
    df['ip']=df['ip'].apply(lambda x: int(netaddr.IPAddress(x)))

    df.sort_values(by=['ip'],inplace=True)

    
    with ZipFile(zips[1], "w", compression=ZIP_DEFLATED) as zf:
        with zf.open("rows.csv", "w") as f:
            df.to_csv(f, index=False)

   
        
        
def ip_check(ips):
    global index, previousip
    jsonlist=[] 
    iplist=[]
  
    csv_reader = csv.DictReader(open('ip2location.csv'))
    for row in csv_reader:
        iplist.append(row)

    list_length=len(iplist)
    
    for ip in ips:
        print(ip)
        before=time.time()
        ip_json= {}
        int_ip= int(netaddr.IPAddress(ip))
        high=int(iplist[index]['high'])
        low=int(iplist[index]['low'])


        if(int_ip>=low and int_ip<=high):
            after=time.time()
            ip_json['ip']=ip
            ip_json['int_ip']=int_ip
            ip_json['region']=iplist[index]['region']
            ip_json['ms']=after-before 
            jsonlist.append(ip_json)



        elif(int_ip<=low):
            for rowindex in range(index,0,-1):
                if(int_ip>=int(iplist[rowindex]['low']) and int_ip<=int(iplist[rowindex]['high'])):
                    after=time.time()
                    ip_json['ip']=ip
                    ip_json['int_ip']=int_ip
                    ip_json['region']=iplist[rowindex]['region']
                    ip_json['ms']=after-before 
                    jsonlist.append(ip_json) 
                    index=rowindex
                    break; 

        else:
            for rowindex in range(index, list_length):
                if(int_ip>=int(iplist[rowindex]['low']) and int_ip<=int(iplist[rowindex]['high'])):
                    after=time.time()
                    ip_json['ip']=ip
                    ip_json['int_ip']=int_ip
                    ip_json['region']=iplist[rowindex]['region']
                    ip_json['ms']=after-before 
                    jsonlist.append(ip_json) 
                    index=rowindex
                    break; 

        
    
    return jsonlist
            
        
def main():
    if len(sys.argv) < 2:
        print("usage: main.py <command> args...")
    elif sys.argv[1] == "ip_check":
        ips = sys.argv[2:]
        print(json.dumps(ip_check(ips)))
    elif sys.argv[1]=="region":
        zips=sys.argv[2:]
        region(zips)
    else:
        print("unknown command: "+sys.argv[1])

if __name__ == '__main__':
     main()       
        
        
        
        
    
    









