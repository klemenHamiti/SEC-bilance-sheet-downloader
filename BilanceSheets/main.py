import bilanceDataGetter
from datetime import datetime
import sys

cik_dict = bilanceDataGetter.readCIKs()
ticker = None
year_of_rep = None
response = None
quarter = None
print('This program gets all relavant financial data for a company for desired quarter or year.')
print('Enter "quit" to quit the program.')
while ticker not in cik_dict.keys():
	ticker = input('Enter a valid ticker: ').upper()
	if ticker.lower() == 'quit':
		sys.exit(1)
print('Ticker provided successfully.')
print('Do you want quarterly data?')
while (response != 'y' and response != 'n'):
	response = input('y/n: ').lower()
while True:
	year_of_rep = input('enter a year of financial report: ')
	try:
		if int(year_of_rep) < 1994:
			print('No available data for years before 1994. Enter a different year.')
		elif int(year_of_rep) > int(datetime.now().year):
			print('Enter a valid year.')
		elif year_of_rep == 'quit':
			sys.exit(1)
		else:
			break
	except ValueError:
		print('Year must be a number.')
cik = cik_dict[ticker]
ids = bilanceDataGetter.getIds(cik, year_of_rep)
report_id = None
if response == 'y':
	while True:
		valid_quarters = [1, 2, 3, 4]
		quarter = input('Enter a quarter (1, 2, 3, 4): ')
		try:
			quarter = int(quarter)
			if quarter in valid_quarters and len(ids) >= quarter:
				print('Quarter entered successfully.')
				report_id = ids[quarter - 1]
				break
			elif len(ids) < int(quarter):
				print('Unfortunately data for this quarter does not exist.')
			else:
				print('Enter a valid number.')
		except ValueError:
			print('Quarter must be a number.')
else:
	report_id = ids[-1] # annual data
print('Trying to get the data...')
bilanceDataGetter.getData(cik, str(report_id), ''.join([ticker, '_', year_of_rep, '_financials.xls']))
print('Data saved successfully.')