from sklearn import svm
import numpy as np
import utils
import winnowing
import copy

def get_kernel(analyzed_data):

	def kernel(X, Y):
		i = 0
		K = np.zeros(shape=(X.shape[0], Y.shape[0]))
		for a in X:
			j = 0
			A = analyzed_data[a[0]]['fingerprint']
			for b in Y:
				B = analyzed_data[b[0]]['fingerprint']
				sim = winnowing.get_program_similarity(A, B)
				K[i][j] = sim
				j += 1
			i += 1
		return K

	return kernel

data = utils.read_file()
T = 7
K = 5

# Train and get the score. Run winnowing. Preprocessing step.
analyzed_data, kw_to_id = utils.winnowing_tokenize_data(data)
analyzed_data = winnowing.K_gram_hashes(analyzed_data, kw_to_id, K)
analyzed_data = winnowing.doc_fingerprints(analyzed_data, T, K)

Y = np.array([analyzed_data[pid]['class'] for pid in analyzed_data])
X = np.array(analyzed_data.keys()).reshape(-1, 1)

# Get kernel fn.
kernel = get_kernel(analyzed_data)

# Accumulate metrics.
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
	clf = svm.SVC(kernel=kernel)
	clf.fit(Xt, Yt)
	Yp = clf.predict(Xc)
	metric_list.append(utils.calc_metrics(Yc, Yp))

print utils.average(metric_list)
