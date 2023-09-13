import numpy as np
import multiprocessing
import os, glob, json
import random
import time
import copy
import itertools

"""
Optimizer function to find a contract of classified items with maximised ROI (%)

"""

globalROI = -100
globalContract = []
covertPrices = {}
classifiedPrices = {}
classifiedDict = {}
covertFloats = {}

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

def mapWear(num,floats):
	count = 0
	for i in floats:
		if num <= i:
			return count
		count +=1
	return -1

def getROI(contract):
	"""
	Given a contract of 10 items with their respective floats, output the ROI

	"""
	cost = ev = floatSum = MinFloat = result = 0
	MaxFloat = 1
	outcomes = []
	for nameFloatPair in contract:
		name = nameFloatPair[0]
		wear = nameFloatPair[1]
		for i, j in enumerate(classifiedPrices[name]):
			if j[0] == wear:
				cost += classifiedPrices[name][i][1][0]
				break
		for outcome in classifiedDict[name]:
			outcomes.append(outcome)
		floatSum += wear

	n = len(outcomes)
	for outcome in outcomes:
		MaxFloat = float(covertFloats[outcome][1])
		MinFloat = float(covertFloats[outcome][0])
		outputFloat = (MaxFloat - MinFloat) * floatSum/10 + MinFloat
		floatRange = np.arange(MinFloat+ 0.05, min(MaxFloat,0.45) , 0.05)
		floats = [0.01,0.03,0.05,0.07,0.08,0.1,0.12,0.15,0.16,0.18,0.25,0.38,0.4,0.45]
		floatRange = np.array(floats)
		floatRange = floatRange[(floatRange >= MinFloat) & (floatRange <= MaxFloat)]
		floatTranslate = floatRange[mapWear(outputFloat,floatRange)]
		for i, j in enumerate(covertPrices[outcome]):
			if j[0] == floatTranslate:
				ev += 1/n * covertPrices[outcome][i][1][1]
				#print(f"{outcome}: {getWear(floatTranslate)} | {covertPrices[outcome][i][1][1]}") #output results
				break
	roi = 100 * ((ev-cost) / cost)
	return roi

def optimiseROI(contract):
	"""
	Keeps track of the current contract yielding the current maximum ROI

	"""
	global globalROI
	global globalContract
	cost = ev = floatSum = MinFloat = result = 0
	MaxFloat = 1
	outcomes = []
	for nameFloatPair in contract:
		name = nameFloatPair[0]
		wear = nameFloatPair[1]
		for i, j in enumerate(classifiedPrices[name]):
			if j[0] == wear:
				cost += classifiedPrices[name][i][1][0]
				break
		for outcome in classifiedDict[name]:
			outcomes.append(outcome)
		floatSum += wear

	n = len(outcomes)
	for outcome in outcomes:
		MaxFloat = float(covertFloats[outcome][1])
		MinFloat = float(covertFloats[outcome][0])
		outputFloat = (MaxFloat - MinFloat) * floatSum/10 + MinFloat
		floatRange = np.arange(MinFloat+ 0.05, min(MaxFloat,0.45) , 0.05)
		floats = [0.01,0.03,0.05,0.07,0.08,0.1,0.12,0.15,0.16,0.18,0.25,0.38,0.4,0.45]
		floatRange = np.array(floats)
		floatRange = floatRange[(floatRange >= MinFloat) & (floatRange <= MaxFloat)]
		floatTranslate = floatRange[mapWear(outputFloat,floatRange)]
		for i, j in enumerate(covertPrices[outcome]):
			if j[0] == floatTranslate:
				ev += 1/n * covertPrices[outcome][i][1][1]
				break
	roi = 100 * ((ev-cost) / cost)
	if (roi > globalROI):
		globalROI = roi
		globalContract = contract
	else:
		globalContract = []
	return [globalROI,globalContract]

if __name__ == "__main__":

	print("Loading price data...")

	with open("covertPrices.json", "r") as f:
		covertPrices = json.load(f)
	with open("classifiedPrices.json", "r") as f:
		classifiedPrices = json.load(f)
	with open("classifiedDict.json", "r") as f:
		classifiedDict = json.load(f)
	with open("covertFloats.json", "r") as f:
		covertFloats = json.load(f)
	with open("classifiedFloats.json", "r") as f:
		classifiedFloats = json.load(f)

	print("Price data loaded")
	contract = [['M4A4 | Desolate Space', 0.15], ['M4A4 | Desolate Space', 0.15], ['M4A4 | Desolate Space', 0.1], ['M4A4 | Desolate Space', 0.1], ['M4A4 | Desolate Space', 0.1], ['M4A4 | Desolate Space', 0.01], ['M4A4 | Desolate Space', 0.01], ['M4A4 | Desolate Space', 0.01], ['M4A4 | Desolate Space', 0.01], ['M4A4 | Desolate Space', 0.01]]
	bestcontracts = []
	bestROI = -100
	ROI = -100
	n = 7

	# Get n best contracts for a contract of 10 of the same items with the same floats as a strong starting point

	for i in classifiedPrices:
		for j in classifiedPrices[i]:
			ROI = -100
			for k in range(10):
				contract[k] = [i,j[0]]
			ROI = getROI(contract)
			if ROI > bestROI:
				if len(bestcontracts) < n:
					bestcontracts.append([ROI, copy.deepcopy(contract)])
					bestROI = ROI
				else: 
					bestcontracts.sort(key=lambda x:x[0])
					bestcontracts[0] = [ROI, copy.deepcopy(contract)]
					bestcontracts.sort(key=lambda x:x[0])
					bestROI = bestcontracts[0][0]

	print(f"Initial best {n} contracts calculated")

	# Make a list with the top n new items and a selection of float values (eg. 0.07, 0.08, 0.1 which are common float values used in a factory new tradeup)
	
	refined = []
	for i in bestcontracts:
		MaxFloat = float(classifiedFloats[i[1][0][0]][1])
		MinFloat = float(classifiedFloats[i[1][0][0]][0])
		floatRange = np.arange(MinFloat+ 0.05, min(MaxFloat,0.45) , 0.05)
		floats = [0.07,0.08,0.1]
		floatRange = np.array(floats)
		floatRange = floatRange[(floatRange >= MinFloat) & (floatRange <= MaxFloat)]
		for j in floatRange:
			refined.append([i[1][0][0],j])

	print(f"Optimising within the top {n} contracts (May take some time):")

	num_processes = 16
	with multiprocessing.Pool(processes=num_processes) as pool:
		results = pool.map(optimiseROI, itertools.combinations_with_replacement(refined, 10))

	bestContract = []
	bestROI = -100
	ROI = -100

	# Find the max ROI from the search and output it with the respective contract

	for ROI in results:
		if ROI[0] > bestROI:
			bestROI = ROI[0]
			bestContract = ROI[1]

	print(f"Optimized ROI: {round(bestROI,3)}%")
	print(f"Respective contract: {bestContract}")
	