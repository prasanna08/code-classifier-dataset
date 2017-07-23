import json
import utils

def hash_generator(kw_to_id, kw):
	hash_val = 0
	n = len(kw) - 1

	for k in kw:
		hash_val += kw_to_id[k] * (len(kw_to_id) ** n )
		n -= 1

	return hash_val


def k_gram_hash_generator(token_program, kw_to_id, K):
	generated_hashes = [
		hash_generator(kw_to_id, token_program[i: i+K])
		for i in xrange(0, len(token_program) - K + 1)]
	return generated_hashes


def get_document_fingerprint(k_gram_hashes, window_size):
	generated_fingerprint = set()
	for i in xrange(0, len(k_gram_hashes) - window_size):
		window_hashes = k_gram_hashes[i: i + window_size]
		min_hash_index = i + min(
			xrange(window_size), key=window_hashes.__getitem__)
		min_hash = k_gram_hashes[min_hash_index]
		generated_fingerprint.add((min_hash, min_hash_index))

	return list(generated_fingerprint)


def calc_jackard_coeff(A, B):
	small_set = A[:] if len(A) < len(B) else B[:]
	union_set = B[:] if len(A) < len(B) else A[:]
	for elem in union_set:
		if elem in small_set:
			small_set.remove(elem)
	union_set.extend(small_set)

	if len(union_set) == 0:
		return 0

	small_set = A[:] if len(A) < len(B) else B[:]
	intersection_set = []
	for elem in small_set:
		if elem in A and elem in B:
			intersection_set.append(elem)
			A.remove(elem)
			B.remove(elem)

	coeff = float(len(intersection_set)) / len(union_set)
	return coeff

def calc_overlap_coeff(A, B):
	small_set = A if len(A) < len(B) else B
	if len(small_set) == 0:
		return 0

	small_set_len = len(small_set)
	intersection_set = []
	for elem in small_set[:]:
		if elem in A and elem in B:
			intersection_set.append(elem)
			A.remove(elem)
			B.remove(elem)

	coeff = float(len(intersection_set)) / small_set_len
	return coeff


def get_program_similarity(fingerprint_a, fingerprint_b):
	A = [h for (h, i) in fingerprint_a]
	B = [h for (h, i) in fingerprint_b]
	return calc_jackard_coeff(A, B)


def K_gram_hashes(analyzed_data, kw_to_id, K=3):
	# K-gram hashes value.
	for program_id in analyzed_data:
		analyzed_data[program_id]['k_gram_hashes'] = k_gram_hash_generator(
			analyzed_data[program_id]['tokens'], kw_to_id, K)
	return analyzed_data


def doc_fingerprints(analyzed_data, T=5, K=3):
	# Threshold value. Minimum length of the substring that is guaranteed to be
	# identified.
	window_size = T - K + 1
	for program_id in analyzed_data:
		analyzed_data[program_id]['fingerprint'] = get_document_fingerprint(
			analyzed_data[program_id]['k_gram_hashes'], window_size)
	return analyzed_data	


def get_top_similars(analyzed_data, top=3):
	for program_id_1 in analyzed_data:
		overlaps = []
		for program_id_2 in analyzed_data:
			overlap = get_program_similarity(
				analyzed_data[program_id_1]['fingerprint'],
				analyzed_data[program_id_2]['fingerprint'])
			overlaps.append((program_id_2, overlap))
		top_overlaps = sorted(
			overlaps, key=lambda e: e[1], reverse=True)[:top]
		analyzed_data[program_id_1]['top_similar'] = top_overlaps
	return analyzed_data


def main():
	# Open the dataset.
	data = utils.read_file()
	T = 5
	K = 3
	top = 3
	# Tokenize programs.
	analyzed_data, kw_to_id = utils.winnowing_tokenize_data(data)
	# print analyzed_data[1]['k_gram_hashes']
	analyzed_data = K_gram_hashes(analyzed_data, kw_to_id, K)
	analyzed_data = doc_fingerprints(analyzed_data, T, K)
	analyzed_data = get_top_similars(analyzed_data, top)

	# Check some program
	pid = 50
	similars = analyzed_data[pid]['top_similar']
	print similars
	print '\n\n\n\n'
	print analyzed_data[pid]['source']
	print '\n\n\n\n'
	print analyzed_data[similars[0][0]]['source']
	print '\n\n\n\n'
	print analyzed_data[similars[1][0]]['source']
	print '\n\n\n\n'
	print analyzed_data[similars[2][0]]['source']	


if __name__ == '__main__':
	main()
