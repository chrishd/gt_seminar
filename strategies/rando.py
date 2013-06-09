import random

# function rando
# parameters: history (list of tupels)
# returns: "a" or "b" (string)
#
def move(history):
	if random.randint(0,1) == 0: # play "a" or "b" with prob. 1/2
		return "a"
	else:
		return "b"


