# Counter-Strike Trade-Up Optimiser

### Introduction

Counter-Strike items have a real world total marketcap of [> $3.5bn][1].

Each item in the game are released in collections or cases which cost real money to open and items in rarer tiers are less likely to be opened than common tiers. Every item can be traded on Valve's 1st party Steam Marketplace for a balance that cannot be withdrawn and only be spent within Steam. However, many 3rd party marketplaces exist where users can buy and sell Counter-Strike items for real money. The most popular marketplace at the time of writing is  buff163 operated by NetEase. 

In Counter-Strike you can trade up 10 items of a given rarity tier to produce one item at one higher tier of rarity. The outcome is based on the case/collection and float values of the 10 inputted items. A float value [0,1] for an item corresponds to the condition of the item, lower float or closer to 0 leads to the item looking in an aesthetically better condition. The potential outcomes of a tradeup can be calculated and the exact float values for each possible outcome is directly known from the input and potential output using a formula.

For each potential outcome item the formula to determine the float of one item is:

Outcome item float = ((Max float of outcome item - Min float of outcome item) × Average float of 10 input items) + Min float of outcome item

[There are online resources you can use to demonstrate some examples for yourself.][2]

### Description

In some instances we can create a contract of 10 input items which we can buy on a marketplace and then trade them up with a guaranteed profitable ROI and this project aim to search for these profitable contracts. 

The main.py file is used to parse the data of all the items into a digestible format that we can later optimise. This file also handles the web-scraping of the a generic marketplace to gather the current prices of all items at different float values. Note that some marketplaces do not allow web-scraping in their terms and conditions, so to be on the safe side the exact source-code for web-scraping has had marketplace specifics redacted. The current source requires mnimimal customisation for the users desired marketplace and is to be used at the users own risk.

I provide two json file of recent historic price data to demonstrate the optimiser's performance.







[1]: <https://pricempire.com/analytics/items?to=1000000&sort=marketcap:DESC> Counter-Strike GO/2 marketcap data
[2]: <https://csfloat.com/trade-up> Trade-Up calculator website