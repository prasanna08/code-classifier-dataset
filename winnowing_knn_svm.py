from collections import Counter
import numpy as np
import utils
import winnowing
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import svm
from sklearn.model_selection import GridSearchCV

data = utils.read_file()
T = 7
K = 5
top = 3 # No. of classes / 2

# Split data in train and cross validation sets.
predict_data = {i: data[i] for i in data if i > 400}
train_data = {i: data[i] for i in data if i <= 400}

# Train and get the score. Run winnowing.
analyzed_data, kw_to_id = utils.winnowing_tokenize_data(data)
analyzed_data = winnowing.K_gram_hashes(analyzed_data, kw_to_id, K)
analyzed_data = winnowing.doc_fingerprints(analyzed_data, T, K)
analyzed_data = winnowing.get_top_similars(analyzed_data, top)

# Predict classes for each program.
occurence = 0
for pid in analyzed_data:
	if pid <= 400:
		similars = analyzed_data[pid]['top_similar']
		if pid in similars:
			similars.remove(pid)
		nearest_classes = [analyzed_data[i]['class'] for (i, s) in similars]
		cnt = Counter(nearest_classes)
		common = cnt.most_common(1)
		analyzed_data[pid]['prediction'] = common[0][0]

		# Find average of number of occurence needed for correct prediction.
		if analyzed_data[pid]['prediction'] == analyzed_data[pid]['class']:
			occurence += common[0][1]

occurence /= 400.0 # No. of training example.

# Calculate metrics. Use only first 400 programs for training SVM so we can
# cross validate our results using remaining programs.
Y = np.array([data[pid]['class'] for pid in data if pid <= 400])
Yp = np.array(
	[analyzed_data[pid]['prediction'] for pid in analyzed_data if pid <= 400])

# Find missclassified points.
missclassified_data = np.where(Y != Yp)[0]

# Create a new dataset for missclassified points.
programs = [data[pid]['source'] for pid in sorted(data.keys())]
cv = CountVectorizer(tokenizer=utils.tokenizer, min_df=4)
cv.fit(programs)
program_vecs = cv.transform(programs)

# Calculate bag of words vectorizer.
for (i, pid) in enumerate(sorted(data.keys())):
	data[pid]['vector'] = program_vecs[pid].todense()

train_data = [data[pid]['vector'] for pid in data]
train_result = [data[pid]['class'] for pid in data]
Xt = np.array(train_data)
Yt = np.array(train_result)

# Fix X dims.
Xt = np.squeeze(Xt)

sample_weight = np.ones(Xt.shape[0])
sample_weight[missclassified_data] = 3

clf = svm.SVC(C=5.5)
clf.fit(Xt, Yt, sample_weight=sample_weight)
cv_missclassified_points = []

# Predict using KNN.
for pid in analyzed_data:
	if pid > 400:
		similars = analyzed_data[pid]['top_similar']
		if pid in similars:
			similars.remove(pid)
		nearest_classes = [analyzed_data[i]['class'] for (i, s) in similars]
		cnt = Counter(nearest_classes)
		common = cnt.most_common(1)
		if common[0][1] < occurence: # Average occurence for KNN to predict correct class.
			cv_missclassified_points.append(pid)
		else:
			analyzed_data[pid]['prediction'] = common[0][0]

cv_programs = [data[pid]['source'] for pid in cv_missclassified_points]
cv_program_vecs = cv.transform(cv_programs)

for (i, pid) in enumerate(cv_missclassified_points):
	data[pid]['vector'] = cv_program_vecs[i].todense()

Xc = np.array([data[pid]['vector'] for pid in cv_missclassified_points])
Xc = np.squeeze(Xc)

# Predict using SVM.
SYp = clf.predict(Xc)
for (i, pid) in enumerate(cv_missclassified_points):
	analyzed_data[pid]['prediction'] = SYp[i]

# Predictions.
Y = np.array([analyzed_data[pid]['class'] for pid in analyzed_data if pid > 400])
Yp = np.array(
	[analyzed_data[pid]['prediction'] for pid in analyzed_data if pid > 400])

print utils.calc_metrics(Y, Yp)
