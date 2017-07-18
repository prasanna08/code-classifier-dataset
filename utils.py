import tokenize
import token
import json
import keyword
from StringIO import StringIO
from sklearn.metrics import precision_score, f1_score, accuracy_score, recall_score
import numpy as np

def read_file():
	f = open('tagged_dataset.json', 'r')
	data = json.loads(f.read()) 
	data = {int(i): data[i] for i in data}
	return data


def get_tokens(program):
	for tid, tname, tstart, tend, _ in tokenize.generate_tokens(
		StringIO(program).readline):
		yield (tid, tname)


def tokenizer(program):
	token_program = []
	for tid, tname in get_tokens(program):
		if tid == token.N_TOKENS or tid == 54:
			continue
		elif tid == token.NAME:
			if tname in keyword.kwlist:
				token_program.append(tname)
			else:
				token_program.append('V')
		else:
			token_program.append(tname)

	return token_program


def winnowing_tokenize_data(analyzed_data, threshold=10):
	alphabet = {}
	variables = 0

	for pid in analyzed_data:
		program = analyzed_data[pid]['source']
		for tid, tname in get_tokens(program):
			# If tid is tokens.NAME then only add if it is a python keyword.
			# Treat all variables same. Treat all methods same.
			if tid == token.N_TOKENS or tid == 54:
				continue
			elif (tid == token.NAME):
				if tname in keyword.kwlist:
					alphabet[tname] = alphabet.get(tname, 0) + 1
				else:
					variables += 1
			else:
				alphabet[tname] = alphabet.get(tname, 0) + 1

	kw_to_count = {k: v for k, v in alphabet.iteritems() if v > threshold}
	kw_to_id = dict(zip(kw_to_count.keys(), xrange(0, len(kw_to_count))))

	# Add 'UNK' in kw_to_id
	unk_count = sum(v for v in alphabet.values() if v <= threshold)
	kw_to_count['UNK'] = unk_count
	kw_to_id['UNK'] = len(kw_to_id)

	# Add 'V' in kw_to_id
	kw_to_count['V'] = variables
	kw_to_id['V'] = len(kw_to_id)

	# A simple test for hash_generator.
	# print hash_generator(kw_to_id, '70', '"num"', '"b:"') --> 1414395
	for program_id in analyzed_data:
		program = analyzed_data[program_id]['source']
		token_program = []
		for tid, tname in get_tokens(program):
			if tid == token.N_TOKENS or tid == 54:
				continue
			elif tid == token.NAME:
				if tname in keyword.kwlist:
					if tname not in kw_to_id:
						token_program.append('UNK')
					else:
						token_program.append(tname)
				else:
					token_program.append('V')
			else:
				if tname not in kw_to_id:
					token_program.append('UNK')
				else:
					token_program.append(tname)

		analyzed_data[program_id]['tokens'] = token_program

	return analyzed_data, kw_to_id


def shuffle_data(X, Y):
	order = np.arange(X.shape[0])
	np.random.shuffle(order)
	X = X[order]
	Y = Y[order]
	return X, Y


def calc_metrics(Yt, Yp):
	F1 = f1_score(Yt, Yp, average='weighted')
	acc = accuracy_score(Yt, Yp)
	precision = precision_score(Yt, Yp, average='weighted')
	recall = recall_score(Yt, Yp, average='weighted')
	return {
		'F1': F1,
		'Accuracy': acc,
		'Precision': precision,
		'Recall': recall
	}


def average(metric_list):
	average_metric = metric_list[0]
	for result in metric_list[1:]:
		for metric in result:
			average_metric[metric] += result[metric]

	for metric in average_metric:
		average_metric[metric] /= len(metric_list)

	return (average_metric['F1'], average_metric['Recall'],
		    average_metric['Precision'], average_metric['Accuracy'])
