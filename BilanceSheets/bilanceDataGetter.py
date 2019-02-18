import numpy
import pandas as pd
from pandas import ExcelWriter
import re
import sys
import string
from tabulate import tabulate
import time

def readCIKs():
	'''
	Returns dictionary, tickers are keys, CIK numbers are values
	'''
	cik_numbers = {}
	with open('cik_ticker.csv', 'r') as f:
		data = f.read()
		for line in data.split('\n'):
			line = line.split('|')
			cik_numbers[line[1]] = line[0]
	return cik_numbers

def extractID(text):
	'''
	Extracts 20 digit number (ID) from a string of characters (Description on SEC website)
	Args:
		text (str) : Description string form https://www.sec.gov/cgi-bin/browse-edgar?
										  action=getcompany&CIK={}&owner=
										  exclude&count=40&hidefilings=0
	'''
	m = re.search('Acc-no: (.+?) ', text)
	if m:
	    found = m.group(1)
	    found = re.sub('-', '', found[:21])
	    return found.encode("ascii", errors="ignore").decode() # remove non ascii characters

def getIds(cik, year_of_rep):
	'''
	Rerurns dictionary, keys are years, values are ids for financial reports over the years
	Args:
		cik (str) : CIK identifier of the company
		year_of_rep (str) : year of wanted report
	'''
	ids = []
	url = 'https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={}&type=&dateb=&owner=exclude&start={}&count=100'
	count = 0
	columns = ['Filings', 'Description', 'Filing Date']
	while True:
		company_url = url.format(cik, count*100)
		table_list = pd.read_html(company_url)
		try:
			df = table_list[2]
			df.drop([1, 4], axis=1, inplace=True)
			df.drop(0, axis=0, inplace=True)
			df.columns = columns
			df['Filing Date'] = list(map(lambda x: x[:4], df['Filing Date'])) # get only the year
			if year_of_rep in df['Filing Date'].unique():
				ix = df.index[(df['Filing Date'] == year_of_rep) \
						   & ((df['Filings'] == '10-Q') | (df['Filings'] == '10-K'))].tolist()
				df = df.loc[ix]
				ids += list(map(extractID, df['Description']))
				count += 1
				time.sleep(0.5)
			else:
				return ids
		except IndexError:
			print('No more data')
			return ids

def save_xls(list_dfs, xls_path):
	'''
	saves ExcelFile
	Args: 
		ExcelFile (object) : ExcelFile object gotten from SEC website containing financial data
		xls_path (str) : path where to save file and name of the file
	'''
	sheets = list(list_dfs.sheet_names)
	with ExcelWriter(xls_path) as writer:
		for i, name in enumerate(sheets):
			df = pd.read_excel(list_dfs, name)
			df.to_excel(writer, name)
		writer.save()

def getData(cik, report_id, xls_path):
	'''
	Retrieves the data from SEC website
	Args:
		cik (str) : CIK identifier of the company
		report_id (str) : unique id of financial report on SEC website
		xls_path (str) : path where to save file and name of the file
	'''
	url = 'https://www.sec.gov/Archives/edgar/data/{}/{}/Financial_Report.xlsx'
	try:
		df = pd.ExcelFile(url.format(cik, report_id))
		save_xls(df, xls_path)
	except Exception as err:
		print(str(err))
		print('No available data for this instance. Try a more recent year.')