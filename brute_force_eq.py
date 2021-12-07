import itertools
from pprint import pprint

def eq(a,b,c,d,e):
	return a + b*c**2 + d**3 - e

answer = {}
for a,b,c,d,e in itertools.permutations([2,3,5,7,9]):
	answer[eq(a,b,c,d,e)] = (a,b,c,d,e)
answer = dict(sorted(answer.items()))
pprint(answer)