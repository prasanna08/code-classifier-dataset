from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
import utils

data = utils.read_file()

programs = [data[pid]['source'] for pid in data]
cv = CountVectorizer(tokenizer=utils.tokenizer, min_df=4)
cv.fit(programs)
program_vecs = cv.fit_transform(programs)

# Calculate bag of words vectorizer.
for pid in data:
	data[pid]['vector'] = program_vecs[pid].todense()

train_data = [data[pid]['vector'] for pid in data]
train_result = [data[pid]['class'] for pid in data]
X = np.array(train_data)
Y = np.array(train_result)

# Fix X dims.
X = np.squeeze(X)

# Shuffle data.
X, Y = utils.shuffle_data(X, Y)
metric_list = []

# K fold cross validation.
for k in range(450 / 50):
	start_cv = k * 50
	end_cv = (k + 1) * 50
	Xc = X[start_cv: end_cv, :]
	Yc = Y[start_cv: end_cv]
	Xt = np.concatenate([X[end_cv:, :], X[:start_cv, :]])
	Yt = np.concatenate([Y[end_cv:], Y[:start_cv]])
	# Train and get the score.
	clf = MultinomialNB()
	clf.fit(Xt, Yt)
	Yp = clf.predict(Xc)
	metric_list.append(utils.calc_metrics(Yc, Yp))

print utils.average(metric_list)