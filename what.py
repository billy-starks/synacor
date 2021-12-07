from pprint import pprint

def func(R1, R2, R8):
	memoize_dict = {}
	input_R1 = R1
	input_R2 = R2
	stack = [(R1, R2)]
	while stack:
		R1, R2 = stack.pop()
		if (R1, R2) in memoize_dict:
			continue

		if R1 == 0:
			memoize_dict[(R1, R2)] = (R2 + 1) % 2**15
		elif R2 == 0:
			answer = memoize_dict.get((R1 - 1, R8), None)
			if answer is not None:
				memoize_dict[(R1, R2)] = answer
			else:
				stack.append((R1, R2))
				stack.append((R1 - 1, R8))
		else:
			answer_inner = memoize_dict.get((R1, R2 - 1), None)
			if answer_inner is not None:
				answer = memoize_dict.get((R1 - 1, answer_inner), None)
				if answer is not None:
					memoize_dict[(R1, R2)] = answer
				else:
					stack.append((R1, R2))
					stack.append((R1 - 1, answer_inner))
			else:
				stack.append((R1, R2))
				stack.append((R1, R2 - 1))
	return memoize_dict.get((input_R1, input_R2))


for x in range(0,32678):
	if func(4,1,x) == 6:
		print(f"R8 is {x}")
		# R8 is 25734

