import sys
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
from tqdm import tqdm
import time
from bs4 import BeautifulSoup
import re
import csv
#from unidecode import unidecode

def write(data):
	file = open('data.csv', 'a')
	file_write = csv.writer(file, delimiter=',')
	file_write.writerows(data)
	file.close()
	return 0

def resident(query):
	url = "http://www.magicbricks.com/Property-Rates-Trends/ALL-RESIDENTIAL-rates-in-"
	for x in query:
		url = url+x+"-"
	url=url[0:-1]
	return url

def commercial(query):
	url = "http://www.magicbricks.com/Property-Rates-Trends/ALL-COMMERCIAL-rates-in-"
	for x in query:
		url = url+x+"-"
	url=url[0:-1]
	return url

def scrapper(link):
	url = "http://www.magicbricks.com"+link;
	i=0
	flag = True
	while flag:
		try:
			response_code = requests.get(url)
			if response_code.status_code == 200:
				html = response_code.text
				tags = BeautifulSoup(html,"html.parser")
				scripts = tags.findAll('script',attrs={'type':"text/javascript"})
				if scripts[34].text:
					flag = False
				uppervals = re.findall(r"upperRange\.push\(parseFloat\('(\d+)'\)\);",scripts[34].text)
				lowervals = re.findall(r"lowerRange\.push\(parseFloat\('(\d+)'\)\);",scripts[34].text)
				intervals = re.findall(r'''quartrValues\.push\("(\w{3}-\w{3}'\d{2})"\);''',scripts[34].text)
				#print(intervals)
				#print(len(uppervals))
				#print(len(lowervals))
				#print(len(intervals))
				data = []
				for u,l,i in zip(uppervals,lowervals,intervals):
					print(u+" "+l+" "+i)
					data.append([u,l,i])
				write(data)

		except requests.ConnectionError:
			pass

def crawler(html):
	soup = BeautifulSoup(html, "html.parser")
	all_local = soup.select("#localitySec a")
	#all_local = soup.findAll("input",{"name" : "localityChk"})
	if all_local:
		for local in all_local:
			print(local.parent.text)
			data = [[],[local.parent.text]]
			write(data)
			print(local['href'])
			scrapper(local['href'])
	return 0

def page_selector(browser,page_no):
	select = browser.find_element_by_xpath('//div[@id="pagination"]//a[@class="act"]//b[text()="%s"]' %page_no)
	#crawler(browser.page_source)
	select.click()
	print("clicked on page no: %s"%page_no)
	time.sleep(5)
	return 0

def page_counter(browser):
	l=0
	check_pages = browser.find_element_by_xpath("//div[@id='pagination']")
	if check_pages.is_displayed():
		pages = browser.find_elements_by_xpath("//div[@id='pagination']//a[@class='act']")
		l = len(pages)+1
		print("No. of Pages: %s" %l)
		for page_no in range(2,l+1):
			crawler(browser.page_source)
			page_selector(browser,page_no)
			#print(page.get_attribute("href"))
		crawler(browser.page_source)
	else:
		print("No pages found")
		crawler(browser.page_source)
	return 0

def selector(url):
	browser = webdriver.Firefox()
	browser.get(url)
	select = browser.find_elements_by_xpath("//div[@class='proTrends-btn']//a")
	for sel in select:
		print(sel.text)
		data = [[],[sel.text]]
		write(data)
		sel.click()
		time.sleep(5)
		page_counter(browser)
	print(url)
	browser.quit()
	return 0

city=""
for a in sys.argv[1:]:
	city = city+" "+a
city = city.lstrip()
data = [[city],[],[],[]]
write(data)
urls = [resident(sys.argv[1:]),commercial(sys.argv[1:])]
i=0
for uri in urls:
	if i<=0:
		data = [['Residential'],[]]
		write(data)
	else:
		data = [['Commercial'],[]]
		write(data)
	selector(uri)
	i=i+1
	data = [[]]
	write(data)

