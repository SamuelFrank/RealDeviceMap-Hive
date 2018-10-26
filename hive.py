import sys
from common import *

if "-make" in sys.argv:
	make()

elif "-build" in sys.argv:
	buildAll(devices)

elif "-start" in sys.argv:
	startAll(devices)

else:
	print("\nHive for RealDeviceMap")
	print("\nUsage: python hive.py -make -build -start")
	print("\t-make\t\tMakes a new RealDeviceMap-UIControl folder to add your provisioning credentials to.")
	print("\t-build\t\tBuilds folders for all devices and edits the files")
	print("\t-start\t\tLaunches each device in its own window and executes python run.py")

print("\nDone.")