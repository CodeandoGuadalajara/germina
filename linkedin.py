import sys
import json
import time
import getopt
import subprocess
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

class LinkedinController:

	LOGIN_USER_VALUE = 'YOUR_EMAIL'
	LOGIN_PASS_VALUE = 'YOUR_PASSWORD'

	TIMEOUT = 5
	INITIAL_URL = 'https://www.linkedin.com/'
	LOGIN_USER_PATH = '#login-email'
	LOGIN_PASS_PATH = '#login-password'
	LOGIN_SUBMIT_PATH = '#loginbutton > input[type="submit"]'
	SEARCH_BAR_PATH = 'input.inputtext'
	SEARCH_URL = 'https://www.linkedin.com/vsearch/p?type=people&f_G=mx%3A0&keywords='
	SEARCH_URL_PAGE_NUMBER = '&page_num='
	SEARCH_PEOPLE_URL = '/keywords_users?ref=top_filter'
	SEARCH_WORK_STRING = 'People who work at '
	USER_CONTAINER_PATH = '#results'
	USER_LIST_CONTAINER_PATH = '#results li.result'
	USER_NAME_PATH = 'div > h3 > a'
	USER_POSITION_PATH = 'div > dl.snippet > dd > p'
	USER_LOCATION_PATH = 'div > dl.demographic'
	USER_COMMON_PATH = 'div > div.related-wrapper.collapsed > ul > li.shared-conn > a'
	USER_DESCRIPTION_PATH = 'div > div.description'
	USER_IMAGE_PATH = 'a img'
	USER_URL_PATH = 'a'
	USER_FRIENDLY_URL_PATH = '.view-public-profile'
	WAIT = 99999
	driver = None
	data = {}

	def loadPage(self, page):
		try:
			self.driver.get(page)
			return True
		except TimeoutException:
			return False

	def submitForm(self, element):
		try:
			element.submit()
			return True
		except TimeoutException:
			return False

	def waitShowElement(self, selector, wait=99999):
		try:
			wait = WebDriverWait(self.driver, wait)
			element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))
			return element
		except:
			return None

	def waitHideElement(self, selector, wait):
		try:
			wait = WebDriverWait(self.driver, wait)
			element = wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, selector)))
			return element
		except:
			return None

	def getElementFrom(self, fromObject, selector):
		try:
			return fromObject.find_element_by_css_selector(selector)
		except NoSuchElementException:
			return None

	def getElementsFrom(self, fromObject, selector):
		try:
			return fromObject.find_elements_by_css_selector(selector)
		except NoSuchElementException:
			return None		

	def getElement(self, selector):
		return self.getElementFrom(self.driver, selector)

	def getElements(self, selector):
		return self.getElementsFrom(self.driver, selector)

	def getElementFromValue(self, fromObject, selector):
		element = self.getElementFrom(fromObject, selector)
		if element:
			return element.text
		return None

	def getElementValue(self, selector):
		element = self.getElement(selector)
		if element:
			return element.text
		return None

	def getElementFromAttribute(self, fromObject, selector, attribute):
		element = self.getElementFrom(fromObject, selector)
		if element:
			return element.get_attribute(attribute)
		return None

	def getElementAttribute(self, selector, attribute):
		element = self.getElement(selector)
		if element:
			return element.get_attribute(attribute)
		return None

	def getParentNode(self, node):
		return node.find_element_by_xpath('..')

	def getChildNodes(self, node):
		return node.find_elements_by_xpath('./*')

	def selectAndWrite(self, field, value):
		fieldObject = self.getElement(field)
		fieldObject.send_keys(value)
		return fieldObject

	def waitAndWrite(self, field, value):
		fieldObject = self.waitShowElement(field, self.WAIT)
		fieldObject.send_keys(value)
		return fieldObject

	def click(self, element):
		actions = webdriver.ActionChains(self.driver)
		actions.move_to_element(element)
		actions.click(element)
		actions.perform()

	def login(self):
		self.loadPage(self.INITIAL_URL)
		self.selectAndWrite(self.LOGIN_USER_PATH, self.LOGIN_USER_VALUE)
		self.submitForm(self.selectAndWrite(self.LOGIN_PASS_PATH, self.LOGIN_PASS_VALUE))

	def searchPeopleWhoWorkAt(self, company, numPage):
		# companyId = self.getCompanyId(company)
		url = self.SEARCH_URL + company + self.SEARCH_URL_PAGE_NUMBER + str(numPage)
		self.loadPage(url)

	def getCompanyId(self, company):
		return '1431'

	def extractUsers(self):
		container = self.waitShowElement(self.USER_CONTAINER_PATH)
		containers = self.getElements(self.USER_LIST_CONTAINER_PATH)
		tmpList = {}
		for element in containers:
			userData = {}
			username = self.getElementFromValue(element, self.USER_NAME_PATH)
			if username:
				userData['name'] = username
				userData['position'] = self.getElementFromValue(element, self.USER_POSITION_PATH)
				userData['description'] = self.getElementFromValue(element, self.USER_DESCRIPTION_PATH)
				userData['image'] = self.getElementFromAttribute(element, self.USER_IMAGE_PATH, 'src')
				userData['location'] = self.getElementFromValue(element, self.USER_LOCATION_PATH)
				userData['common'] = self.getElementFromValue(element, self.USER_COMMON_PATH)
				tmpUrl = self.getElementFromAttribute(element, self.USER_URL_PATH, 'href')
				arrUrl = tmpUrl.split('&')
				varUrl = arrUrl[0]
				userData['url'] = varUrl
				arrId = varUrl.split('id=')
				varId = arrId[1]
				userData['id'] = varId
				print userData['id']
				tmpList[varId] = varUrl
				self.data[varId] = userData	
		for varId in tmpList.keys():
			url = tmpList[varId]
			print url
			self.loadPage(url)
			friendlyUrlContainer = self.waitShowElement(self.USER_FRIENDLY_URL_PATH, 20)
			if friendlyUrlContainer:
				friendlyUrl = friendlyUrlContainer.text
			else:
				friendlyUrl = url
			print friendlyUrl
			self.data[varId]['friendlyUrl'] = friendlyUrl
			self.data[varId]['profile'] = self.getInfo(friendlyUrl)
		return self.data

	def close(self):
		self.driver.quit()

	def extractPeopleWhoWorkAt(self, company, fromPage=1, toPage=1, store='linkedin.json'):
		print 'Logging in'
		self.login()
		toPage = toPage + 1
		for numPage in range(fromPage, toPage):
			print 'Searching people who work at ' + company + ' page ' + str(numPage)
			self.searchPeopleWhoWorkAt(company, numPage)
			print 'Extracting users'
			users = self.extractUsers()
			print 'Users extracted: ' + str(len(users))
			self.saveToFile(store)
		self.close()
		return users

	def getInfo(self, url):
		command = 'linkedin-scraper ' + url
		try:
			output = subprocess.check_output(command.split())
			userInfo = json.loads(output)
		except:
			userInfo = {}
		return userInfo

	def saveToFile(self, fileName):
		file_ = open(fileName, 'w')
		content = json.dumps(self.data, sort_keys=True, indent=4, separators=(',', ': '))
		file_.write(content)
		file_.close()

	def __init__(self): 
		self.driver = webdriver.Firefox()
		# self.driver = webdriver.PhantomJS()
		# self.driver = webdriver.Chrome('./chromedriver')
		self.driver.set_page_load_timeout(self.TIMEOUT)

def main(argv):
	company = 'mexico'
	fromPage = 1
	toPage = 100
	store = 'linkedin.json'
	opts, args = getopt.getopt(argv, "b:f:t:s:")
	if opts:
		for o, a in opts:
			if o == "-b":
				company = a
			elif o in ("-f"):
				fromPage = int(a)
			elif o in ("-t"):
				toPage = int(a)
			elif o in ("-s"):
				store = a
	linkedin = LinkedinController()
	users = linkedin.extractPeopleWhoWorkAt(company=company, fromPage=fromPage, toPage=toPage, store=store)
	print 'Total of users extracted: ' + str(len(users))

if __name__ == "__main__":
    main(sys.argv[1:])