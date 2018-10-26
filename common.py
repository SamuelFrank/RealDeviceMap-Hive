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
	return relPath + "{}-RDM".format(uuid[:8])


def remove_readonly(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def make():
	# Clone the base repo
	print('Cloning repo...')
	dir = relPath + "RealDeviceMap-UIControl"
	os.system("git clone " + repoUrl + " ./" + dir)
	os.chdir(dir)
	print('Running pod install...')
	os.system('pod install')
	os.chdir('..')


def buildAll(devices):
	numDevices = len(devices)
	numDone = 1

	for device in devices:
		print('Building instance {} out of {}'.format(numDone, numDevices))

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

		os.chdir(dir)
		print('Running pod install...')
		os.system('pod install')

		print('Deleting old project files...')
		shutil.rmtree('RealDeviceMap-UIControl.xcodeproj', onerror=remove_readonly)
		shutil.rmtree('RealDeviceMap-UIControl.xcworkspace', onerror=remove_readonly)
		os.chdir(os.path.dirname(os.path.realpath(__file__)))

		print('Copying project files...')
		shutil.copytree(relPath + 'RealDeviceMap-UIControl/RealDeviceMap-UIControl.xcodeproj', dir + '/RealDeviceMap-UIControl.xcodeproj')
		shutil.copytree(relPath + 'RealDeviceMap-UIControl/RealDeviceMap-UIControl.xcworkspace', dir + '/RealDeviceMap-UIControl.xcworkspace')
		numDone += 1
		

def build(dir):
	if os.path.exists(dir):
		print("Deleting directory {}...".format(dir))
		shutil.rmtree(dir, onerror=remove_readonly)

	print("Cloning repo in {}...".format(dir))
	os.system("git clone " + repoUrl + " ./" + dir)


def launch(bashScript, script, dir):
	scriptData = """
	#!/bin/bash
	cd {0}
	cd {1}
	echo "Launching {2}..."
	python {2}
	""".format(os.path.dirname(os.path.realpath(__file__)), dir, script)

	with open(bashScript, 'w') as file:
		file.write(scriptData)

	os.system('chmod +x ' + bashScript)

	os.system('open -a Terminal.app ' + bashScript)

def startAll(devices):
	numDevices = len(devices)
	numDone = 1

	for device in devices:
		print('Initializing {}...'.format(device))
		print('Instance {} out of {}'.format(numDone, numDevices))
		dir = getDirName(device)

		launchScript = device[:8] + ".launch.command"

		print('Launching run.py...')
		launch(launchScript, 'run.py', dir)

		if isinstance(devices[device],dict) and 'ilocation' in devices[device]:
			print('Launching spoof.py...')
			time.sleep(5)
			launch(launchScript, 'spoof.py', dir)

		if numDone < numDevices:
			print("Waiting for {} seconds to start the next instance".format(startDelay))
			time.sleep(startDelay)
		
		numDone += 1
