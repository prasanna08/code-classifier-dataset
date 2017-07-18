from collections import Counter
import numpy as np
import utils
import winnowing

data = utils.read_file()
T = 7
K = 5
top = 5

# Train and get the score. Run winnowing.
analyzed_data, kw_to_id = utils.winnowing_tokenize_data(data)
analyzed_data = winnowing.K_gram_hashes(analyzed_data, kw_to_id, K)
analyzed_data = winnowing.doc_fingerprints(analyzed_data, T, K)
analyzed_data = winnowing.get_top_similars(analyzed_data, top)

# Predict classes for each program.
for pid in analyzed_data:
	similars = analyzed_data[pid]['top_similar']
	if pid in similars:
		similars.remove(pid)
	nearest_classes = [analyzed_data[i]['class'] for (i, s) in similars]
	cnt = Counter(nearest_classes)
	analyzed_data[pid]['prediction'] = cnt.most_common(1)[0][0]

# Calculate metrics.
Y = np.array([data[pid]['class'] for pid in data])
Yp = np.array([analyzed_data[pid]['prediction'] for pid in analyzed_data])
metric_list = [utils.calc_metrics(Y, Yp)]
print utils.average(metric_list)
