#Code to generate models from the data.

from os import walk
from sklearn import svm

def get_data(file_name):
	fp=open(file_name)
	data=fp.read()
	return data

def get_time(time_string):
	if time_string is not None:
		time_bucket = time_string.split(':')
		if(len(time_bucket) > 1):
			return int(time_bucket[1])
	else:
       		return 0

attr_list = []    # Stores all the attributes that can be present in a request.
global_order = {} # Stores the order of the attributes in the user request.
response_type = [] # Indexing of the different request type
request_action = [] # Indexing of the different request actions
request_protocol = [] #Indexing of the different request protocols.

def extract_training_data(raw_data):
	lines = raw_data.split('\n')
	data={}
	for line in lines:
		tokens_init = line.split(' ')
		if(len(tokens_init) >= 10):
			IP = tokens_init[0]
			if IP not in data:
				data[IP]=[]
			feature = []
			feature.append(get_time(tokens_init[3])) # time. 
			response = tokens_init[8]
			if response not in response_type:
				response_type.append(response)
			feature.append(response_type.index(response)) # response.
			if(tokens_init[9] == '-'):
				tokens_init[9] = 0
			feature.append(int(tokens_init[9])) # size.
			tokens_req = line.split('"')
			if(len(tokens_req) > 2):
				user_request = tokens_req[1]
				tokens = user_request.split(' ')
				action = tokens[0]
				if action not in request_action:
					request_action.append(action)
				feature.append(request_action.index(action)) # Request_action

				protocol = tokens[2]
				if protocol not in request_protocol:
					request_protocol.append(protocol)
				feature.append(request_protocol.index(protocol)) # Request_protocol
				feature.append(len(tokens[1])) # Actual request length
				feature.append(tokens[1]) # Saved for the second round.
				update_global_parameters(tokens[1])
			data[IP].append(feature)
	keys = data.keys()
	for key in keys:
		print key + " : " + str(len(data[key]))
		for feature in data[key]:
			user_request = feature.pop()
			feature.append(get_order_value(user_request))
			feature += get_attribute_vector(user_request)
#			print feature
#			raw_input()
	return data

def get_attribute_vector(user_request):
	vector = [0 for i in range (0, len(attr_list))]
	tokens = user_request.split('?')
	if(len(tokens) > 1):
		attributes = tokens[1].split('&')
		for attr in attributes:
			key = attr.split('=')[0]
			if key in attr_list:
				vector[attr_list.index(key)] = 1
	return vector

def get_order_value(user_request):
	order = {}
	tokens = user_request.split('?')
	if(len(tokens) > 1):
		attributes = tokens[1].split('&')
		l = len(attributes) - 1
		for index in range(0, l):
			parent = attributes[index].split('=')[0]
			if(index  + 1 < l):
				child = attributes[index + 1].split('=')[0]
				if parent in order:
					order[parent].append(child)
				else:
					order[parent] = [child]
		keys = order.keys()
		for key in keys:
			global_vals = global_order[key]
			for val in order[key]:
				if val not in global_vals:
					print user_request
					raw_input()
					return 1
	return 0	
				
def train_model(training_data):
#	print '|| Inside train model ||'
#	print len(training_data)
	user_model = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
	user_model.fit(training_data)
	return user_model

accuracy_table = []

def predict_accuracy(user_model, test_data, accuracy_row, flag):
	Z = user_model.decision_function(test_data)
	accuracy = 0.
	if(flag == 1):
		count = 0.
		for z in Z:
			if z >= 0:
				count += 1
		accuracy = count/len(Z)
	else:
		count = 0.
		for z in Z:
			if z < 0:
				count += 1
		accuracy = count/len(Z)
	accuracy_row.append(accuracy)
	accuracy_table.append(accuracy_row)
#		print "Accuracy : " + str(count/len(Z))

def update_global_parameters(req):
	tokens = req.split('?')
	if(len(tokens) > 1):
#		print req
		attributes = tokens[1].split('&')
		for attr in attributes:
			item = attr.split('=')
			if(len(item) == 2):
				key = item[0]
				value = item[1] # Not used as of now.
				if key not in attr_list:
					attr_list.append(key)
		l = len(attributes) - 1
		for index in range(0, l):
			parent = attributes[index].split('=')[0]
			if(index + 1 < l):
				child = attributes[index+1].split('=')[0]
				if parent not in global_order:
					global_order[parent] = []
				global_order[parent].append(child)

def main():
	raw_data = ''
	mypath = '/home/jayant/Downloads/Datasets/LOGS'
	files=[]
	for(dirpath, dirnames, filenames) in walk(mypath):
		files.extend(filenames)
	for f in files:
	 	print f
		if '.txt' in f:
		 	print 'true'
		 	raw_data = get_data(f)
#		 	raw_data += get_data(f)
#		 	break
#			raw_data=get_data(mypath)
#			data = extract_training_data(raw_data)
#			keys = data.keys()
#			user_classifiers = {}
#			for key in keys:
#				user_classifiers[key] = train_model(data[key])
#			for classifier_key in keys:
#				for data_key in keys:
#					accuracy_row = [classifier_key, data_key]
#					if(data_key == classifier_key):
#						predict_accuracy(user_classifiers[classifier_key], data[data_key], accuracy_row, flag = 1)
#					else:
#						predict_accuracy(user_classifiers[classifier_key], data[data_key], accuracy_row, flag = 0)
#			for row in accuracy_table:
#				print row
	
if __name__=="__main__":
	main()
