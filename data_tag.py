import json

FILE = 'compiled_dataset.json'

with open(FILE, 'r') as f:
	data = json.loads(f.read())

start = 0
end = 100
data = data[start: end]

class_to_feedback_mapping = {
	'1': 'Please write python program for summing all number divisible by either 5 or 3 upto 1000.',
	'2': 'Make sure that program does not go into infinite loop or recursion.',
	'3': 'Make sure that you are summing up all the numbers upto 1000.',
	'4': 'Make sure that you are summing up all the numbers divisible by either 3 or 5.',
	'5': 'Make sure that you are calling defined functions correctly.',
	'6': 'Program is working as expected.',
}

analysed_program = {i: {'source_program': data[i]} for i in range(len(data))}
# analysed_program = data

for pid in analysed_program:
	print '+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n\n'
	print analysed_program[pid]['source_program']
	print '\n\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
	# print 'Assigned feedback class: %s' % (analysed_program[pid]['feedback_class'])
	feedback = raw_input('Assigned class: ')
	# if feedback is not '':
	analysed_program[pid]['feedback_class'] = feedback

OUT_FILE = 'compiled_dataset_with_classes_%d-%d.%s'
OUT_JSON = OUT_FILE % (start, end, 'json')
with open(OUT_JSON, 'w') as f:
	f.write(json.dumps(analysed_program))

# convert it to CSV.
lines = [(pid, analysed_program[pid]['source_program'],
		  analysed_program[pid]['feedback_class']) for pid in analysed_program]
OUT_CSV = OUT_FILE % (start, end, 'csv')
with open(OUT_CSV, 'w') as f:
	f.write('"Program ID", "Source code", "Feedback class"\n')
	for line in lines:
		f.write('"%s", "%s", "%s"\n' % (line[0], line[1], line[2]))
