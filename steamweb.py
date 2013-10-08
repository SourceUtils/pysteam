#!/usr/bin/env python3
# import steam
# steam.key = "303E8E7C12216D62FD8F522602CE141C"
# dir(steam)
#from inspect import getcallargs # getcallargs(f, 1, 2, 3)
import requests, json

key = None

aid_max = 2**32-1

def tta(x):
	g = re.match("(?i)STEAM_(.*):(.*):(.*)", x).groups()
	return (g[2] << 1) + g[1]

aid   = lambda x: 0xffffffff        & x # from 64 bit
id64  = lambda x: 0x110000100000000 | x # from account id

tt64  = lambda x: id64(tta(x))

start = id64(1) # 76561197960265728
end   = id64(aid_max) # 81064793292668927

att   = lambda x: (x & 1, x >> 1)

def execute(interface, method, http="GET", version=1, *args, **kwargs):
	if key != None:
		kwargs["key"] = key
	url = "http://api.steampowered.com/%s/%s/v%04d" % (interface, method, version)
	if(len(kwargs) > 0):
		attrs = "&".join("%s=%s" % (arg,val) for arg,val in kwargs.items())
		url += "?" + attrs
	print(url)
	request = requests.get(url)
	print(str(request.status_code) + " " + request.reason)
	if not request.ok:
		return None
	response = request.json()
	#while True:
	#	try: return requests.get(url).json()
	#	except: continue
	return response

def create_method(interface, method, http, version, doc):
	fn = lambda self, *args, **kwargs: execute(interface, method, http, version, *args, **kwargs)
	fn.__doc__ = doc
	return fn

def init(key=None):
	"""
	Specify api_key=<key> for more methods
	"""
	listing = execute(interface="ISteamWebAPIUtil", method="GetSupportedAPIList")
	for interface in listing["apilist"]["interfaces"]:
		intname = str(interface["name"])
		methods = {}
		versions = {}
		for method in interface["methods"]:
			methname, httpmethod, version = str(method["name"]), method["httpmethod"], method["version"]
			if not methname in versions:
				versions[methname] = []
			versions[methname].append((intname, version, httpmethod, method["parameters"]))
		for k,value in versions.items():
			#print(k + "," + str(value))
			docstrings = []
			for v in value:
				methname, intname, version, httpmethod, params = k, v[0], v[1], v[2], v[3]
				arg_gen = (str("%s %s %s" % (x["type"], x["name"], ("(optional)" if x["optional"] == True else ""))).ljust(35) + ": " + x.get("description", "No description") for x in params)
				docstrings.append("version %d:\n" % version + "\n".join(arg_gen))
			documentation = "\n\n".join(x for x in docstrings)
			# always the latest version
			print("steam." + intname + "." + methname + "() = " + httpmethod)
			methods[methname] = create_method(intname, methname, httpmethod, version, documentation)
		globals()[intname] = type(intname, (object,), methods)()

init()
