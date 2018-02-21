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
config = ConfigParser.RawConfigParser(allow_no_value=True)

g = open('vars.conf')
config.readfp(g)

# print(config.items("ceph"))

# vars = [x.strip('\n').split(".") for x in g.readlines()]


cbt_fp = open('rbd_config.yaml')
cbt_config_data = yaml.load(cbt_fp)
# print cbt_config_data

# there are two files from which the configurations are collected, ceph-conf and the cbt-conf

# This function gets the category ie either ceph or cbt form the vars.conf file
def get_vars(category):
	vars_list = []
	g = open('vars.conf')
	config.readfp(g)
	vars_list = config.items(category)
	return vars_list

config_files = ["ceph", "cbt"]

# The purpose of this function is to map the variables form the vars.conf file from a given category 
# to the values form the respective config file
# variables contains the list of tuples form the vars file under the given category
def get_vals_from_config(category, variables):
	val_list = []
	if category == "ceph":
		fp.seek(0)
		config.readfp(fp)
		for var in variables:
			# var_list.append(var[0].split('.'))
			val = var[0].split('.')
			val_list.append((val[1], dict(config.items(val[0]))[val[1]]))
		# print val_list
		return val_list
		values_list = config.items(category)
	if category == "cbt":
		for var in variables:
			val = var[0].split('.')
			value = cbt_config_data
			for x in val:
				value = value[x]
			val_list.append((val[len(val)-1], value))
		# print val_list
		return val_list


# the result is jsonified to generate a json containing the necessary variables with their values
result = {}

for file in config_files:
	if file == "ceph":
		print("Gathering CEPH configurations")
		variables = get_vars(file)
		# print(variables)
		result[file] = get_vals_from_config(file, variables)
		# print result
	if file == "cbt":
		print("Gathering CBT configurations")		
		variables = get_vars(file)
		# print(variables)
		result[file] = get_vals_from_config(file, variables)
		# print result

pp.pprint(result)

