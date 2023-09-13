import argparse
import numpy as np
import os, glob, json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium_stealth import stealth
import random
import undetected_chromedriver as uc
import time

"""
Main function to generate data files and scrape price details for a given grade of item.

For each rarity category a dictionary is made to store the possible float ranges for each item. Some items range from [0,1] but for example can range from [0.06,0.8].

Additionally, for each rarity category a dictionary is made to store the items that every item in that cateogry trades up to in the category above it. (Note, covert is excluded as they cannot be traded up.)

"""

def getWear(num):
    if num<=0.07:
        return " (Factory New)" 
    if num<=0.15:
        return " (Minimal Wear)" 
    if num<=0.38:
        return " (Field-Tested)" 
    if num<=0.45:
        return " (Well-Worn)" 
    return " (Battle-Scarred)" 

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Generate data files and scrape price details for a given grade of item",
    )


    parser.add_argument(
        "-d",
        "--dir",
        help="path to chromium config directory used for scraping (eg. /home/Ali/.config/chromium)",
        default="/home/USERNAME/.config/chromium",
    )

    parser.add_argument(
        "-s",
        "--scrape",
        help="scrape prices for a given item rarity (consumer, industrial, milspec, restricted, classified, covert)",
        default="",
    )
    
    # Parse arguments
    args = parser.parse_args()

    # Adapt this for the marketplace to scrape price data from where itemids.txt contains a dictionary of the marketplaces ids for each item 

    # idMap = {}
    # with open("itemids.txt", "r") as fptr:
    #         with open("tradeupids.txt", "w") as gptr:
    #             for i in range(21526):
    #                 line = fptr.readline().strip()
    #                 if ("Battle-Scarred" in line or "Minimal Wear" in line or "Field-Tested" in line or "Well-Worn" in line or "Factory New" in line):
    #                     if ("★" in line or ";Souvenir" in line or "P250 | X-Ray" in line):
    #                         # print(f"Discard: {line}")
    #                         continue
                        
    #                     gptr.write(f"{line}\n")   
    #                     kvp = ["",""]
    #                     kvp = line.split(";")
    #                     idMap[kvp[1]] = kvp[0]

    
    path = './jsonStash/'
    print("Updating database..")
    for dataIter in range(2):
        count = 0
        classifiedDict = {}
        restrictedDict = {}
        milspecDict = {}
        industrialDict = {}
        consumerDict = {}

        classifiedFloats = {}
        restrictedFloats = {}
        milspecFloats = {}
        industrialFloats = {}
        consumerFloats = {}
        covertFloats = {}
        wearRange = []

        consumerPrices = {}
        restrictedPrices = {}
        milspecPrices = {}
        industrialPrices = {}
        classifiedPrices = {}
        covertPrices = {}

        # Get price data for each item across these float values.

        floats = [0.01,0.03,0.05,0.07,0.08,0.1,0.12,0.15,0.16,0.18,0.25,0.38,0.4,0.45]
        
        for filename in glob.glob(os.path.join(path, '*.json')):
            with open(os.path.join(os.getcwd(), filename), 'r') as f:
                data = json.load(f)
                covert = []
                for i,k in enumerate(data['content']['Covert Skins']):
                    covert.append(k['name'])
                    for j in k['wears']:
                        wearRange = j.split('-')
                    floatRange = np.array(floats)
                    # Some items have a minimum and or maximum float so for those we need to adjust the float data points used
                    floatRange = floatRange[(floatRange >= float(wearRange[0])) & (floatRange <= float(wearRange[1]))]
                    covertFloats[k['name']] = floatRange if not dataIter == 1 else wearRange
                    
                classified = []
                for i,k in enumerate(data['content']['Classified Skins']):
                    classified.append(k['name'])
                    for j in k['wears']:
                        wearRange = j.split('-')
                    floatRange = np.array(floats)
                    floatRange = floatRange[(floatRange >= float(wearRange[0])) & (floatRange <= float(wearRange[1]))]
                    classifiedFloats[k['name']] = floatRange if not dataIter == 1 else wearRange

                restricted = []
                for i,k in enumerate(data['content']['Restricted Skins']):
                    restricted.append(k['name'])
                    for j in k['wears']:
                        wearRange = j.split('-')
                    floatRange = np.array(floats)
                    floatRange = floatRange[(floatRange >= float(wearRange[0])) & (floatRange <= float(wearRange[1]))]
                    restrictedFloats[k['name']] = floatRange if not dataIter == 1 else wearRange
                milspec = []
                for i,k in enumerate(data['content']['Mil-Spec Skins']):
                    milspec.append(k['name'])
                    for j in k['wears']:
                        wearRange = j.split('-')
                    floatRange = np.array(floats)
                    floatRange = floatRange[(floatRange >= float(wearRange[0])) & (floatRange <= float(wearRange[1]))]
                    milspecFloats[k['name']] = floatRange if not dataIter == 1 else wearRange
                industrial = []
                for i,k in enumerate(data['content']['Industrial Grade Skins']):
                    industrial.append(k['name'])
                    for j in k['wears']:
                        wearRange = j.split('-')
                    floatRange = np.array(floats)
                    floatRange = floatRange[(floatRange >= float(wearRange[0])) & (floatRange <= float(wearRange[1]))]
                    industrialFloats[k['name']] = floatRange if not dataIter == 1 else wearRange
                consumer = []
                for i,k in enumerate(data['content']['Consumer Grade Skins']):
                    consumer.append(k['name'])
                    for j in k['wears']:
                        wearRange = j.split('-')
                    floatRange = np.array(floats)
                    floatRange = floatRange[(floatRange >= float(wearRange[0])) & (floatRange <= float(wearRange[1]))]
                    consumerFloats[k['name']] = floatRange if not dataIter == 1 else wearRange

                if dataIter == 0:
                    for i in covert:
                        floatArray = []
                        for j in covertFloats[i]:
                            floatArray.append([round(j,2), [0, 0]])
                            covertPrices[i] = floatArray

                for i in classified:
                    classifiedDict[i] = covert
                    if dataIter == 0:
                        floatArray = []
                        for j in classifiedFloats[i]:
                            floatArray.append([round(j,2), [0, 0]])
                            classifiedPrices[i] = floatArray

                for i in restricted:
                    restrictedDict[i] = classified
                    if dataIter == 0:
                        floatArray = []
                        for j in restrictedFloats[i]:
                            floatArray.append([round(j,2), [0, 0]])
                            restrictedPrices[i] = floatArray
                for i in milspec:
                    milspecDict[i] = restricted
                    if dataIter == 0:
                        floatArray = []
                        for j in milspecFloats[i]:
                            floatArray.append([round(j,2), [0, 0]])
                            milspecPrices[i] = floatArray
                for i in industrial:
                    industrialDict[i] = milspec
                    if dataIter == 0:
                        floatArray = []
                        for j in industrialFloats[i]:
                            floatArray.append([round(j,2), [0, 0]])
                            industrialPrices[i] = floatArray
                for i in consumer:
                    consumerDict[i] = industrial
                    if dataIter == 0:
                        floatArray = []
                        for j in consumerFloats[i]:
                            floatArray.append([round(j,2), [0, 0]])
                            consumerPrices[i] = floatArray

        if dataIter == 1:
            with open("covertFloats.json", "w") as gptr:
                json.dump(covertFloats , gptr) 
            with open("classifiedFloats.json", "w") as gptr:
                json.dump(classifiedFloats , gptr) 
            with open("restrictedFloats.json", "w") as gptr:
                json.dump(restrictedFloats , gptr) 
            with open("milspecFloats.json", "w") as gptr:
                json.dump(milspecFloats , gptr) 
            with open("industrialFloats.json", "w") as gptr:
                json.dump(industrialFloats , gptr) 
            with open("consumerFloats.json", "w") as gptr:
                json.dump(consumerFloats , gptr) 
        else:
            with open("classifiedDict.json", "w") as gptr:
                json.dump(classifiedDict , gptr) 
            with open("restrictedDict.json", "w") as gptr:
                json.dump(restrictedDict , gptr) 
            with open("milspecDict.json", "w") as gptr:
                json.dump(milspecDict , gptr) 
            with open("industrialDict.json", "w") as gptr:
                json.dump(industrialDict , gptr) 
            with open("consumerDict.json", "w") as gptr:
                json.dump(consumerDict , gptr)

    print("Database updated successfully")

    # Get prices for a certain category of item rarity

    scrapedPrices = {}
    toScrape = True

    if (args.scrape == "covert"):
        scrapedPrices = covertPrices
    elif (args.scrape == "classified"):
        scrapedPrices = classifiedPrices
    elif (args.scrape == "restricted"):
        scrapedPrices = restrictedPrices
    elif (args.scrape == "milspec"):
        scrapedPrices = milspecPrices
    elif (args.scrape == "industrial"):
        scrapedPrices = industrialPrices
    elif (args.scrape == "consumer"):
        scrapedPrices = consumerPrices
    else:
        toScrape = False

    if (toScrape):
        print("Attempting web scrape")
        options = webdriver.ChromeOptions()
        options.add_argument("--user-data-dir="+args.dir) # /home/USERNAME/.config/chromium
        driver = uc.Chrome(use_subprocess=True, headless=False, options=options)

        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        print("Web driver launched")
        count = 0
        itemid = 0
        with open(args.scrape+"Prices.json", "w") as gptr:
            for i in scrapedPrices:
                print(f"{count}: {i}")
                for j in scrapedPrices[i]:
                    sleepTime = np.random.randint(20, 35)/10
                    time.sleep(sleepTime)
                    skinName = i+getWear(float(j[0]))
                    # Get item id for marketplace
                    # itemid = idMap[skinName]
                    driver.get("URL REDACTED"+itemid+"&minfloat=0.00&maxfloat="+str(j[0])+"&sortby=asc")
                    data = json.loads(driver.find_element(By.TAG_NAME,'body').text)
                    try:
                        j[1][0] = float(data['data']['items'][9]['price']) # Buy price
                        j[1][1] = float(data['data']['items'][0]['price']) # Sell price
                    except IndexError:
                        j[1][0] = float('inf')
                        j[1][1] = float('-inf')
                    except KeyError:
                        time.sleep(sleepTime)
                        data = json.loads(driver.find_element(By.TAG_NAME,'body').text)
                        try:
                            j[1][0] = float(data['data']['items'][9]['price'])
                            j[1][1] = float(data['data']['items'][0]['price'])
                        except IndexError:
                            j[1][0] = float('inf')
                            j[1][1] = float('-inf')
                        except KeyError:
                            j[1][0] = float('inf')
                            j[1][1] = float('-inf')
                    count+=1
            json.dump(scrapedPrices, gptr) 
    else:
        print("Scraping not selected")
    print("Done!")