import yaml
import json
import pprint
import ConfigParser
import textwrap
import os, re
from pymongo import MongoClient

path_to_ceph_config = "" # example : /path/to/ceph.conf.bs
path_to_cbt_config = ""  # example: /path/to/runtests.2osd_rbd_example.yaml 

'''
In this version of the parser, it is assumed that the 

Pseudocode for parsing the ceph configuration

First read the config file 
Remove the indentations from the config

Instantiate a ConfigParser object

Read and open "var.txt"
	then parse the file using ConfigParser
	extract the vars under "Ceph" and store them in a list

parse the config using ConfigParser 
	then extract only those items present in vars(list)

store the vals in the form of a dict to be later appended into a JSON.
'''
"""
TODO list:

- Add variables for file paths of ceph conf and cbt conf 
- Add the benchmark which ran in the output json
- Change a few variable names to make more sense
- Separate DB functionality into another script
- Modify code to allow for passing arguments from command line or from another file
- Clean code, by removing commented print statements
- Check mongodb version on incerta
- a shell-script to invoke both the parser and db insertion script to enable running over multiple test results
"""

pp = pprint.PrettyPrinter(indent=4)

#Read the ceph conf file
# fp = open('ceph.conf.bs',"r+")
fp = open(path_to_ceph_config,"r+")
indented_vars_file = fp.readlines()

#Remove the indentations in the ceph-config file
fp.seek(0)
for line in indented_vars_file:
	fp.write(textwrap.dedent(line))
fp.truncate()

# create a ConfigParser object
parsed_config = ConfigParser.RawConfigParser(allow_no_value=True)

# Load the file containing required configuration variables
g = open('vars.conf')
parsed_config.readfp(g)

# Loading the CBT config file
# cbt_fp = open('rbd_config.yaml')
cbt_fp = open(path_to_cbt_config)
cbt_config_data = yaml.load(cbt_fp) # cbt config data loaded as dict

# there are two files from which the configurations are collected, ceph-conf and the cbt-conf

# This function gets the category ie either ceph or cbt form the vars.conf file
def get_vars(category):
	vars_list = []
	ls = []
	g = open('vars.conf')
	parsed_config.readfp(g)
	vars_list = parsed_config.items(category)
	ls = map(lambda x: list(x), vars_list)
	map(lambda x: x.pop(), ls)
	# map(lambda x: x[0].split('.'), ls)
	# print ls
	return ls

config_files = ["ceph", "cbt"]

# The purpose of this function is to map the variables form the vars.conf file from a given category 
# to the values form the respective config file
# variables contains the list of tuples form the vars file under the given category
def get_vals_from_config(category, variables):
	config_val_mapped_dict = {}
	if category == "ceph":
		fp.seek(0)						# ceph config file pointer
		parsed_config.readfp(fp)		# configParser object for ceph config
		for var in variables:
			config = var[0].split('.')
			# print(config)
			config_val_mapped_dict[config[1]] = dict(parsed_config.items(config[0]))[config[1]]
		# print config_val_mapped_dict
		return config_val_mapped_dict
		values_list = parsed_config.items(category)
	if category == "cbt":
		for var in variables:
			val = var[0].split('.')
			cbt_value = cbt_config_data
			for x in val:
				cbt_value = cbt_value[x]
			config_val_mapped_dict[val[-1]] = cbt_value
			# print config_val_mapped_list
		return config_val_mapped_dict


def get_required_filepaths_from_results():
	fp = open("results_file_list.txt", "w+")
	for subdir, dirs, files in os.walk(path_to_cbt_results):
		for file in files:
			for pattern in patterns: 
				if re.search(pattern, file):
					if pattern == "benchmark_config":
						fp.write(os.path.join(subdir, file))
						fp.write("\n")
					if pattern == "json_output.1" or pattern == "json_output.0" :
						fp.write(os.path.join(subdir, file))
						fp.write("\n")
	fp.close()


def get_req_benchmark_configs_value_pairs(filepath, config_val_mapped_dict):
	fp = open(filepath)
	config_data = yaml.load(fp) # load the benchmark yaml as a dict
	req_config_list = get_vars("cbt_results") # retrieve the required results configurations from vars.conf 
	# print req_config_list
	config_dict = {}
	for config in req_config_list:
		# print config
		path = config[0].split('.') # path of the config represented as a list 
		# print value
		config_value = config_data 
		for nest in path:
			config_value = config_value[nest]
		config_val_mapped_dict[path[-1]] = config_value
		# config_dict[config] = config_data[config]
	fp.close()
	return config_val_mapped_dict

def get_result_file(filepath):
	fp = open(filepath)
	res = json.load(fp)
	fp.close()
	# pp.pprint(dict(res))	
	return res


path_to_cbt_results = "/home/soumya/outreachy/test/cbt_results/rbd-tests/3osd_rbd_example_hdd_hdd_bs"
patterns = ['json_output.0', 'json_output.1', 'benchmark_config']

result = {}

# the result is jsonified to generate a json containing the necessary variables with their values

for file in config_files:
	if file == "ceph":
		print("Gathering CEPH configurations ...........")
		variables = get_vars(file)
		# print(variables)
		result[file] = get_vals_from_config(file, variables)
		# print result
	if file == "cbt":
		print("Gathering CBT configurations ...........")		
		variables = get_vars(file)
		# print(variables)
		result[file] = get_vals_from_config(file, variables)
		# print result

# pp.pprint(result)

get_required_filepaths_from_results()
f = open("results_file_list.txt")
files_list = f.read().split("\n")
# print(files)
counter = 0
result["cbt_results"] = {}
for file in files_list:
	for pattern in patterns:
		if re.search(pattern, file):
			if not result["cbt_results"].has_key("output_"+str(counter)):
				result["cbt_results"]["output_"+str(counter)] = {}
			if pattern == "benchmark_config":
				# benchmark_value_pairs = get_req_benchmark_configs(file)
				# print file
				result["cbt_results"]["output_"+str(counter)] = get_req_benchmark_configs_value_pairs(file, result["cbt_results"]["output_"+str(counter)])
				counter += 1
			if pattern == "json_output.0":
				# print file
				result["cbt_results"]["output_"+str(counter)]["0"] = get_result_file(file)
			if pattern == "json_output.1":
				result["cbt_results"]["output_"+str(counter)]["1"] = get_result_file(file)
	# result["cbt_results"]["output_"+str(counter)] = {}

rp = open("input_to_db.json", "w")
rp.write(json.dumps(result, indent = 4))
rp.close()
# pp.pprint(result)


################## Database component ########################

client = MongoClient()

db = client['xyz']
collection = db['abc']
# im using mongoDB version 2.6.1, hence using the relevant pymongo
# because mongodb version 3.4.1 doesnt support/allow "." in key values,I am using the command of a deprecated version.
doc_id = collection.insert(result, check_keys=False)

# For pymongo version 3.6.1, 
# doc_id = collection.insert_one(result).inserted_id
print(doc_id)
