#!/usr/bin/env python
"""
Usage:
import steamweb
steamweb.init(<Web API key>)
dir(steam)
help(steamweb.ISomething.Method)
"""

import requests, json, re
#from inspect import getcallargs # getcallargs(f, 1, 2, 3)

key = None

aid   = lambda x: 0xffffffff        & x # from 64 bit
id64  = lambda x: 0x110000100000000 | x # from account id

def parse_aid(x):
	g = re.match("(?i)STEAM_(.*):(.*):(.*)", x).groups()
	return (g[2] << 1) + g[1]
	
parse_64  = lambda x: id64(parse_aid(x))

tuple_aid = lambda x: (x & 1, x >> 1)

# start = id64(1) # 76561197960265728
# end   = id64(2**32-1) # 81064793292668927

def execute(interface, method, http="GET", version=1, *args, **kwargs):
	if key != None: kwargs["key"] = key
	url = "http://api.steampowered.com/%s/%s/v%04d" % (interface, method, version)
	if(len(kwargs) > 0):
		attrs = "&".join("%s=%s" % (arg, val) for arg, val in kwargs.items())
		url += "?" + attrs
	print(url)
	request = requests.get(url)
	print(str(request.status_code) + " " + request.reason)
	if not request.ok:
		return None
	response = request.json()
	#while True: # keep trying in event of failure
	#	try: return requests.get(url).json()
	#	except: continue
	return response

def create_method(interface, method, http, version, doc):
	fn = lambda self, *args, **kwargs: execute(interface, method, http, version, *args, **kwargs)
	fn.__doc__ = doc
	return fn

def init(key):
	globals()['key'] = key
	for interface in execute(interface="ISteamWebAPIUtil", method="GetSupportedAPIList")["apilist"]["interfaces"]:
		intname = str(interface["name"])
		methods = {}
		versions = {}
		for method in interface["methods"]:
			methname, httpmethod, version = str(method["name"]), method["httpmethod"], method["version"]
			if not methname in versions:
				versions[methname] = []
			versions[methname].append((intname, version, httpmethod, method["parameters"]))
		for k, value in versions.items():
			#print(k + "," + str(value))
			docstrings = []
			for v in value:
				methname, intname, version, httpmethod, params = k, v[0], v[1], v[2], v[3]
				arg_gen = (str("%s %s %s" % (x["type"], x["name"], ("(optional)" if x["optional"] == True else ""))).ljust(35) + ": " + x.get("description", "No description") for x in params)
				docstrings.append("version %d:\n" % version + "\n".join(arg_gen))
			documentation = "\n\n".join(x for x in docstrings)
			# always use the latest version if not specified
			print("steamweb." + intname + "." + methname + "() = " + httpmethod)
			methods[methname] = create_method(intname, methname, httpmethod, version, documentation)
		globals()[intname] = type(intname, (object,), methods)()
