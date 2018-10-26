import sys
from common import *

if "-build" in sys.argv:
	buildAll(devices)

if "-start" in sys.argv:
	startAll(devices)
	
print("Done.")