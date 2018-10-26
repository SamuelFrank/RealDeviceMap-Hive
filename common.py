import os
import sys
import stat
import shutil
import time
from subprocess import call
import fileinput
from config import *

def editFile(file_path, target, new_value):
	print('Editing file: ' + file_path)

	# Read in the file
	with open(file_path, 'r') as file :
	  filedata = file.read()

	# Replace the target string
	filedata = filedata.replace(target, new_value)

	# Write the file out again
	with open(file_path, 'w') as file:
		file.write(filedata)

def getDirName(uuid):
	return absPath + "{}-RDM".format(uuid[:8])

def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def buildAll(devices):
	for device in devices:
		dir = getDirName(device)
		build(dir)
		editFile(dir + '/RealDeviceMap-UIControl/Config.swift', 'DEVICE_UUID', device)
		editFile(dir + '/RealDeviceMap-UIControl/Config.swift', 'http://RDM_UO:9001', backendURLBaseString)
		editFile(dir + '/run.py','DEVICE_UUID', device)
		
		if isinstance(devices[device],dict) and 'account_manager' in devices[device] and devices[device]['account_manager'] == True:
			editFile(dir + '/RealDeviceMap-UIControl/Config.swift', 'class Config: ConfigProto {', 'class Config: ConfigProto {\n\tvar enableAccountManager = true\n')
			
		if isinstance(devices[device],dict) and 'ilocation' in devices[device]:
			editFile(dir + '/spoof.py','DEVICE_UUID', device)
			editFile(dir + '/spoof.py','http://DEVICE_IP:8080/loc', 'http://{}:8080/loc'.format(devices[device]['ilocation']))
		

def build(dir):
	if os.path.exists(dir):
		print("Deleting directory {}...".format(dir))
		shutil.rmtree(dir, onerror=remove_readonly)

	print("Cloning repo in {}...".format(dir))
	os.system("git clone " + repoUrl + " ./" + dir)

def startAll(devices):
	for device in devices:
		print('Initializing {}...'.format(device))
		dir = getDirName(device)
		if isinstance(devices[device],dict) and 'ilocation' in devices[device]:
			print('Launching spoof.py...')
			os.system('start /D "{}" cmd /K python spoof.py'.format(dir))
		
		print('Launching run.py...')	
		os.system('start /D "{}" cmd /K python run.py'.format(dir))
		print("Waiting for {} seconds to start the next instance".format(startDelay))
		time.sleep(startDelay)
