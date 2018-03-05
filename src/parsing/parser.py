import yaml
import sys, json, collections
import pprint
import ConfigParser
import textwrap

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
fp = open('ceph.conf.bs',"r+")
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
cbt_fp = open('rbd_config.yaml')
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


# the result is jsonified to generate a json containing the necessary variables with their values
result = {}

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

pp.pprint(result)

