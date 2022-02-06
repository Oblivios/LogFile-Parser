from os import system
import os

try:    
    import csv
    from collections import Counter
    from dict2xml import dict2xml
    import folium
    import json
    import matplotlib.pyplot as plt
    import platform
    import requests
    import re
    from time import sleep
    from tqdm import tqdm
    from user_agents import parse
    import webbrowser
except ImportError:
    input("Press your Enter key to install needed modules.")
    system("py -m pip install -r requirements.txt")
    system("python -m pip install -r requirements.txt")
    system("python3 -m pip install -r requirements.txt")

def parsing(file,DictIP={},IP_Country={},IP_OS={},IP_WB={},IP_Status={},DateList=[],reg='([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)"',ind=0):
    #Change the reg variable above, if you want to personalize it.
    with open(file) as f:
        string = f.readlines()
    print("This step may take time depending on the size of the file given...")
    if DictIP=={}:
        for line in tqdm(string, desc="Loading...", bar_format='{l_bar}{bar:30}{r_bar}{bar:-30b}'):
            Infos = re.match(reg,line).groups()
            IP, Date, Status, UserAgent = Infos[0], Infos[1], Infos[3], parse(Infos[6])
            OS = str(UserAgent.os.family)
            WB = str(UserAgent.browser.family)
            if IP not in DictIP:
                try:
                    IP_OS[f'OS{ind}']=OS
                    IP_WB[f'WB{ind}']=WB
                    IP_Status[f'Status{ind}']=Status
                    DateList.append(Date)
                    IPInfos = getIP_infos(IP)
                    DictIP[IP]=[IPInfos["continent"],IPInfos["country"],IPInfos['city'],IPInfos['lat'],IPInfos['lon']]
                    IP_Country[f'Country{ind}']=IPInfos["country"]
                    sleep(0.7)
                except (KeyError, json.decoder.JSONDecodeError):
                    pass
                except requests.exceptions.ConnectionError:
                    sleep(1)
            ind+=1
    else:
        for line in tqdm(string, desc="Loading...", bar_format='{l_bar}{bar:30}{r_bar}{bar:-30b}'):
            Infos = re.match(reg,line).groups()
            IP, Date, Status, UserAgent = Infos[0], Infos[1], Infos[3], parse(Infos[6])
            OS = str(UserAgent.os.family)
            WB = str(UserAgent.browser.family)
            DateList.append(Date)
            IP_OS[f'OS{ind}']=OS
            IP_WB[f'WB{ind}']=WB
            IP_Status[f'Status{ind}']=Status
            ind+=1
        ind=0
        for country in DictIP.values():
            IP_Country[f'Pays{ind}']=country[1]
            ind+=1
    EnumCountry = Counter(IP_Country.values())
    EnumOS = Counter(IP_OS.values())
    EnumWB = Counter(IP_WB.values())
    EnumStatus = Counter(IP_Status.values())
    print("Done!")
    return DictIP, EnumOS, EnumWB, EnumStatus, EnumCountry, DateList  

#IP & Geo Infos
def Marker(DictIP):
    for IP,Infos in DictIP.items():
        folium.Marker((Infos[3],Infos[4]), popup=f"<b>{IP}</b><br>{Infos[0]}<br>{Infos[1]}<br>{Infos[2]}").add_to(map)

def getIP_infos(ip):
    return requests.get(f"http://ip-api.com/json/{ip}?fields=continent,country,city,lat,lon").json()

#Graphics
def reqCountry(EnumCountry):
    plt.bar(list(EnumCountry.keys()),list(EnumCountry.values()),color="blue")
    plt.show()

def reqDate(DateList,listDays=[],listDaysTemp=[],dictTime={},ind=0,temp=0):
    for date in DateList:
        if date[0:2] not in listDays:
            listDays.append(date[0:2])
    listDays.reverse()
    print(f"Present day(s): {listDays}")
    day_choice = str(input("Specific day (1), or every present days (2) ? "))
    match day_choice:
        case "1":
            try:
                print(f"Present day(s): {listDays}")
                day_choice_ = str(input("Please take a present day (ex: 09): "))
                for date in DateList:
                    if day_choice_ == date[0:2]:
                        if date[12:14] not in listDaysTemp:
                            listDaysTemp.append(date[12:14])
                            temp+=1
                        dictTime[f"day{ind}"]=f"{date[12:14]}h"
                        ind+=1
                enumSpecDay = Counter(dictTime.values())
                plt.bar(list(enumSpecDay.keys()),list(enumSpecDay.values()),color="blue")
                plt.show()
            except:
                print("A problem has occured.")
            listDays,listDaysTemp,dictTime,ind,temp=[],[],{},0,0
        case "2":
            try:
                for date in DateList:
                    if date[0:2] not in listDaysTemp:
                        listDaysTemp.append(date[0:2])
                        temp+=1
                    dictTime[f"day{ind}"]=f"{date[0:2]} {date[3:6]}"
                    ind+=1
                enumDays = Counter(dictTime.values())
                plt.bar(list(enumDays.keys()),list(enumDays.values()),color="blue")
                plt.show()
            except:
                print("A problem has occured.")
            listDays,listDaysTemp,dictTime,ind,temp=[],[],{},0,0
        case _:
            print("Invalid choice.")
    #clean()

#Exports
def exportToCSVFile(dataIP, dataOS, dataWB, dataStatus, detailsIP = ["IP","Continent","Country","City","Latitude","Longitude"], OSDetails = ["OS","numbers"], WBDetails = ["WebBrowsers","numbers"], StatusDetails = ["Status","numbers"], liste_temp=[]):
    for i,y in dataIP.items():
        y.insert(0,i)
        liste_temp.append(y)
    with open(curr_dir+"\csvIP.csv",'w',encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(detailsIP)
        writer.writerows(liste_temp)
        f.close()
    liste_temp.clear()

    for i,y in dataOS.items():
        y = [y]
        y.insert(0,i)
        liste_temp.append(y)
    with open(curr_dir+"\csvOS.csv",'w',encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(OSDetails)
        writer.writerows(liste_temp)
        f.close()
    liste_temp.clear()

    for i,y in dataWB.items():
        y = [y]
        y.insert(0,i)
        liste_temp.append(y)
    with open(curr_dir+"\csvWB.csv",'w',encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(WBDetails)
        writer.writerows(liste_temp)
        f.close()
    liste_temp.clear()

    for i,y in dataStatus.items():
        y = [y]
        y.insert(0,i)
        liste_temp.append(y)
    with open(curr_dir+"\csvStatus.csv",'w',encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(StatusDetails)
        writer.writerows(liste_temp)
        f.close()
    liste_temp.clear()

def exportToJSONFile(dataIP, dataOS, dataWB, dataStatus):
    with open(curr_dir+"\jsonIP.json",'w',encoding='utf-8') as f:
        f.write(dataIP)
        f.close()
    with open(curr_dir+"\jsonOS.json",'w',encoding='utf-8') as f:
        f.write(dataOS)
        f.close()
    with open(curr_dir+"\jsonWB.json",'w',encoding='utf-8') as f:
        f.write(dataWB)
        f.close()
    with open(curr_dir+"\jsonStatus.json",'w',encoding='utf-8') as f:
        f.write(dataStatus)
        f.close()

def exportToXMLFile(dataIP, dataOS, dataWB, dataStatus):
    with open(curr_dir+r"\xmlIP.xml",'w',encoding='utf-8') as f:
        f.write(dict2xml(dataIP))
        f.close()
    with open(curr_dir+r"\xmlOS.xml",'w',encoding='utf-8') as f:
        f.write(dict2xml(dataOS))
        f.close()
    with open(curr_dir+r"\xmlWB.xml",'w',encoding='utf-8') as f:
        f.write(dict2xml(dataWB))
        f.close()
    with open(curr_dir+r"\xmlStatus.xml",'w',encoding='utf-8') as f:
        f.write(dict2xml(dataStatus))
        f.close()

def clean():
    system('cls') if platform.system() == 'Windows' else system('clear')

clean()
map = folium.Map()
log_file = input("Please copy and paste here the path of the .log file: ")
name_file = "\\"+log_file.split("\\")[-1]
curr_dir = log_file.replace(name_file,"")

print("Is there already a JSON file for the .log file that you want ? (Y/N)")
choice_json, create_json = str(input(" > ")).lower(), True
clean()
match choice_json:
    case "y":
        dump_json = input("Please copy and paste here the path of the JSON file: ")
        file_json = open(dump_json)
        json_load = json.load(file_json)
        create_json = False
        parse_ = parsing(log_file,json_load)
    case _:
        parse_ = parsing(log_file)

DictIP, EnumOS, EnumWB, EnumStatus, EnumCountry, DateList = parse_[0], parse_[1], parse_[2], parse_[3], parse_[4], parse_[5]
JSONDumpIP = json.dumps(DictIP)

if create_json:
    with open(curr_dir+"\JsonIP.json",'w',encoding='utf-8') as f:
        f.write(JSONDumpIP)
        f.close()
    print("Do you wanna keep the dump of the JSON file to make it faster next time, with the same .log file ? (Y/N)")
    choice_json = str(input(" > ")).lower()
    match choice_json:
        case "n":
            os.remove(curr_dir+"\JsonIP.json")

while True:
    choice = str(input("""
1. Locate the IP addresses of the log file via the API of https://ipapi.com and OpenStreetMap.
2. Display a graph of the number of requests according to a specific duration.
3. Display a graph of the number of requests according to their countries.
4. Display Operating Systems that have connected to the server.
5. Display Web Browsers that have connected to the server.
6. Display the number of response errors.
7. Export all the data to CSV format.
8. Export all the data to JSON format.
9. Export all the data to XML format.
10. Leave the program.

> """))
    match choice:
        case "1":
            Marker(parse_[0])
            map.save(curr_dir+"\gg.html")
            webbrowser.open(curr_dir+"\gg.html")
        case "2":
            reqDate(DateList)
        case "3":
            clean()
            reqCountry(EnumCountry)
        case "4":
            clean()
            print("Number of OS that have connected to the server:\n")
            for i,y in EnumOS.items():
                print(str(i)+": "+str(y))
            input("")
        case "5":
            clean()
            print("Number of Web Browsers that have connected to the server:\n")
            for i,y in EnumWB.items():
                print(str(i)+": "+str(y))
            input("")
        case "6":
            clean()
            print("Number of response errors depending of the HTTP return code:\n")
            for i,y in EnumStatus.items():
                print(str(i)+": "+str(y))
            input("")
        case "7":
            exportToCSVFile(DictIP, EnumOS, EnumWB, EnumStatus)
        case "8":
            exportToJSONFile(JSONDumpIP, json.dumps(EnumOS), json.dumps(EnumWB), json.dumps(EnumStatus))
        case "9":
            exportToXMLFile(DictIP, EnumOS, EnumWB, EnumStatus)
        case "10":
            clean()
            print("Goodbye!\n")
            break
        case _:
            print("Invalid argument. Please retry.\n")