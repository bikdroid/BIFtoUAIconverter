#!/usr/bin/python
# Author : Bikramjit

import re
import sys
import json
import collections
import os
import time

#Counters
variable_counter = 0
varlist = []
vardict = {}
arguments = []
var_index_map = {}
final_uai_list = []
prob_relations_counter = 0
table_size = 0

#UAI Specification
PREAMBLE_MAP = []
FUNCTION_MAP = []

# url = r"E:\ML\diabetes.bif\diabetes.bif"
url = r"E:\ML\diabetes.bif\diabetes.bif"

fulldata  = open(url).readlines()
# homesoup = BeautifulSoup(fulldata)

# variables = homesoup.find_all
varblock = False
probblock = False
new_dict = collections.OrderedDict()
print "MARKOV"

for line in fulldata:
	if line.find('variable')>-1:
		varblock = True
		# increase count of variables in the file.
		
		#varlist.append(line.split(' ')[1])
		varname = line.split(' ')[1]
		vardata = []
		vardata.append(varname)
		vardict[variable_counter] = [varname];
		var_index_map[varname] = variable_counter;
		# extract the type discrete value --> domain sizes
	if varblock:
		if line.find('type')>-1: # when line contains type
			parts = line.split(' ')
			domain_size = parts[5]
#			print "Domain Size = "+parts[5]
			mylist = vardict[variable_counter]
			mylist.append(domain_size)

			# list with variable name and domain size
			# added to dict.
			vardict[variable_counter] = mylist
			#print "Position of { = "+line.find('{').__str__()
			#print "Position of } = "+line.find('}').__str__()
			variable_counter = variable_counter+1
			varblock = False

	l = []
	if line.find('probabil')>-1:
		probblock = True

		'''

		probability (Z | X,Y){

			(X1,Y1) Vector1;
			(X2,Y2) Vector2;
			.
			.
			.
		}

		PREAMBLE_MAP : [
						[n1,x1,y1],
						[n2,x2,y2,z2]
		]
		FUNCTION_MAP : [
						{X1:[[Y1,Vector],[Y2,Vector]]},
						{X2:[[Y1,Vector],[Y2,Vector],...]},
						.
						.
						.
					]

		FULL_LIST.append(PROB_DICT) -- sequentially storing everything.
		'''

		# extract the values, write them in same sequence
		cardinals = re.findall(r'\((.*?)\)',line);
		#print cardinals
		arguments = re.split(', | \| |',cardinals[0].strip());
		#print arguments
		if len(arguments)==1:
			#print "single variable"
			l = [1,var_index_map[arguments[0]]]
			PREAMBLE_MAP.append(l)

		if len(arguments)==2:
			#print "double variables"
			l = [2,var_index_map[arguments[1]],var_index_map[arguments[0]]]
			PREAMBLE_MAP.append(l)

		if len(arguments)==3:
			#print "triple arguments"
			l = [len(arguments),var_index_map[arguments[1]],var_index_map[arguments[2]],var_index_map[arguments[0]]]
			PREAMBLE_MAP.append(l)
		#make a dictionary for the table, 
		###
		# key = value of left variable
		# value = list of the values for right variable

	if probblock:
		if not line.find('{')>-1 and not line.find('}')>-1:
			prob_relations_counter = prob_relations_counter+1
			#print re.findall(r'\((.*?)\)',line)
			
			
			
			if len(arguments)==1:
				vector = re.split(', |;|',re.split('table',line)[1].strip())
				variable_index = var_index_map[arguments[0]]
				attribute_name = arguments[0]
				nlist = []
				nlist.append([attribute_name,vector[:-1]])
				new_dict[attribute_name] = nlist
				table_size = table_size + len(vector[:-1])
				l = [table_size,dict(new_dict)]
				FUNCTION_MAP.append(l)

			if len(arguments)==2:
				# Get the domain value in the bracket.
				x_attrib = re.findall(r'\((.*?)\)',line);

				# Get the vector for the domain value.
				vector = re.split(', |;|',re.split('\) ',line)[1].strip())

				table_size = table_size+len(vector[:-1])
				if x_attrib[0] in new_dict.keys():
					nlist = new_dict[x_attrib[0]]
					nlist.append([arguments[0],vector[:-1]])
					new_dict[x_attrib[0]] = nlist
				else:
					nlist = []
					nlist.append([arguments[0],vector[:-1]])
					new_dict[x_attrib[0]] = nlist

			if len(arguments)==3:
				#print arguments[0]+", "+arguments[1]+", "+arguments[2]
				attribs = re.findall(r'\((.*?)\)', line)
				attrib_list = re.split(', ',attribs[0])
				x_attrib = attrib_list[0]
				y_attrib = attrib_list[1]
				# So we have the x and y attribute, which are arguments[2] and arguments[3]
				vector = re.split(', |;', re.split('\) ', line)[1].strip())
				#table_size = table_size+len(vector[:-1])
				table_size = table_size+len(vector[:-1])
				if x_attrib in new_dict.keys():
					nlist = new_dict[x_attrib]
					nlist.append([y_attrib,vector[:-1]])
					new_dict[x_attrib] = nlist
				else:
					nlist = []
					nlist.append([y_attrib,vector[:-1]])
					new_dict[x_attrib] = nlist
					# vector added to Ordered Dictionary new_dict()
#				print new_dict



		elif line.find('}')>-1: # Probability block is over
			probblock = False #no more probability block
			
			#prob_relations_counter = prob_relations_counter + 1
			if(len(arguments)==2): # for the case of 2 variables.
#				print "FOR 2 arguments"
				l = [table_size,dict(new_dict)]				
				FUNCTION_MAP.append(l)

			if(len(arguments)==3): # for the case of 3 variables
				#print "FOR 3 arguments"
				l = [table_size, dict(new_dict)]
#				print l
				FUNCTION_MAP.append(l)

			table_size = 0
			new_dict.clear()

		else:
			#print "..."
			{ }



#Write To UAI File

print "UAI\n"
# f = open("outputfile"+time.strftime("%Y%m%d-%H%M%S")+".uai","r+")
filename = "uaifile"+time.strftime("%Y.%m.%d-%H%M%S")+".uai"
if not os.path.exists(filename):
	f = open(filename,"w")
f.write(str(variable_counter))
print variable_counter
print "\n"
f.write('\n')
#print "Var List :: ", vardict
#print "Variable - Index Map : \n",var_index_map
#PRINT THE CARDINALITIES
#print vardict

for key, value in vardict.items():	
	print value[1],
	f.write(str(value[1])+" ")

f.write("\n")
print "\n"
#Number of cliques
num_of_cliques = len(FUNCTION_MAP)

print num_of_cliques
f.write("\n"+str(num_of_cliques))
print "\n"
f.write('\n')
for each in PREAMBLE_MAP:
	for e in each:
		print e, 
		f.write(str(e)+" ")
	print "\n"
	f.write("\n")

f.write("\n")
#Print the Function tables
# using FUNCTION_MAP
for func in FUNCTION_MAP:
	print func[0]
	print "\n"
	f.write(str(func[0]))
	f.write("\n")

	for k,v in func[1].items():
		print "\t",
		f.write("\t")
		
		y_line = ""
		for y_value in v:
			
			for value in y_value[1]:
					#print str(value),
					y_line = y_line+" "+str(value)
					#f.write(str(value)+" ")
				
			
			y_line = y_line+","

		print "\t"+y_line
		f.write(str(y_line))
		print "\n"
		f.writelines("\n")
f.flush()
f.close()
print "Please Find Output File = "+filename
