import os

PIP_MODULES = ['beaker','httplib2','bottle','boto','oauth2client','google-api-python-client','BeautifulSoup']

def run():
	os.system('sudo python csc326/get-pip.py')
	os.system('sudo apt-get update')
	os.system('sudo apt-get -y install python-pip')		
	
	for module in PIP_MODULES:
		os.system('sudo pip install %s' % module)
	os.chdir("lab4_final/backend/frontend/")
	os.system("screen -dm sudo python HelloWorld.py")

run()

