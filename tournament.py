#!/user/bin/python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import random
import time

# used for error message
status = {"strategyA": "dummyA", "strategyB": "dummyB", "move": 0}
# defines how often two players play against each other
GAME_ITERATIONS = 100

# function determine_payoff
# parameters: game, p1Act, p2Act (all string) 
# returns: payoff (tuple) 
#
# This function takes the name of the game (game) and the actions
# of players 1 (p1Act) and 2 (p2Act) and looks up the corresponding
# payoff tuple, which it then returns.
#
def determine_payoff(game,p1Act,p2Act):
	games = {
		'prison':{'aa':(1,1), 'ab':(3,0), 'ba':(0,3), 'bb':(2,2)}, 
		'staghunt':{'aa':(8,8), 'ab':(0,4), 'ba':(4,0), 'bb':(6,6)},
		'chicken':{'aa':(2,2), 'ab':(1,3), 'ba':(3,1), 'bb':(0,0)},
		'pennies':{'aa':(1,-1), 'ab':(-1,1), 'ba':(-1,1), 'bb':(1,-1)}
	}
	code = p1Act+p2Act #combine actions to reference cell of normal form game
	return games[game][code]; # return corresponding payoff

# function play
# parameters: game (string), f1, f2 (function), his1, his2 (list of tuples)
# returns: 	three-element list, containing the payoff-tupel, and 
# 			newly appended histories for players 1 and 2
#
def play(game, f1, f2, his1, his2):
	p1Action = f1(game, 1, his1) # determine player 1's action
	p2Action = f2(game, 2, his2) # and player2's.
	if (p1Action != "a" and p1Action != "b"):
		sys.exit("Illegal move in strategy " + status["strategyA"] + " in move " + str(status["move"]))
	if (p2Action != "a" and p2Action != "b"):
		sys.exit("Illegal move in strategy " + status["strategyB"] + " in move " + str(status["move"]))
	his1.append([p1Action,p2Action]) # add decisions to history of player 1
	his2.append([p2Action,p1Action]) # and 2
	payoff = determine_payoff(game,p1Action,p2Action) # determine payoff
	return [payoff,his1,his2]; # return payoff-tupel and appended histories as a three-element list

# function determine_rounds
# Determines the number of played rounds. After 1000 rounds each round ends with independet
# chance of 1/10.
# parameters: -
# returns: number of rounds 
#
def determine_rounds():
	i = 1000
	while random.randint(0, 9) != 0:
		i += 1
	return i

# function one_on_one 
# parameters: a (function), b (function), rounds (int), game (string)
# returns: returns a 4-element list containing average of strategyA payoff, average of strategyB payoff,
#		   history1, history2 (each with the first element beeing the respective strategy
#
def one_on_one(a, b, rounds, game):
	history1 = []
	history2 = []
	sumA = 0
	sumB = 0
	AccPayOff = []

	# play the game
	for i in range(rounds):
		status["move"] = i
		Result = play(game, a, b, history1, history2) # play the round
		AccPayOff.append(Result[0]) # first collect all payoffs, sum up later
		history1 = Result[1] # update histories after decisions have been made
		history2 = Result[2]

	# calculate payoffs
	for poff in AccPayOff:
		sumA = sumA+poff[0] # sum up all payoffs of player 1 
		sumB = sumB+poff[1] # and player 2

	avgA = sumA/float(rounds)
	avgB = sumB/float(rounds)

	#print sumA
	#print sumB
	#print rounds
	#print avgA
	#print avgB
	
	return (avgA, avgB, history1, history2)

# function run_tournement
# parameters: game (string), rounds (int array)
#
def run_tournement(game, rounds):
	results = {}
	strategies = {}
	histories = {} # histories[strategy][opposing_strategy][game] 
				   #  -> history array [move_strategy, move_opposing_strategy]
	strategiesFolder = os.path.abspath(os.path.join(os.curdir, "strategies")) # find strategies in this folder
	sys.path.append(os.path.join(strategiesFolder))

	for root, dirs, files in os.walk(strategiesFolder):
		# import strategies
		for filename in files:
			split = os.path.splitext(filename)
			name = split[0]
			if name[0] == "." or split[1] != ".py": # use filename as strategy name
				continue
			exec("import " + name)
			results[name] = 0
			strategies[name] = eval(name + ".move")

		# initialize histories
		for i in results.keys():
			histories[i] = {}

		tournament_start = time.time()
		# play tournement
		for i in results.keys():
			for n in results.keys():
				if i == n: # don't let strategies play against themselves
					break
				histories[i][n] = []
				histories[n][i] = []
				status["strategyA"] = i
				status["strategyB"] = n
				# Play 100 times

				print "playing " + str(len(rounds)) + " iterations of " + i + " against " + n + "..."
				round_start = time.time()
				for c in range(len(rounds)):
					(resultA, resultB, historyA, historyB) = one_on_one(strategies[i], strategies[n], rounds[c], game)
					results[i] += resultA
					results[n] += resultB
					histories[i][n].append(historyA)
					histories[n][i].append(historyA)
					#print "run " + str(c+1) + ": " + i + " played " + str(rounds[c]) + " rounds against " + n + " with average results: " + str(resultA) + "," + str(resultB)		
				print "...which took "+ str(time.time()-round_start)+" seconds"
				print ""

		print "Finished. Tournament took "+str(time.time()-tournament_start) + " seconds to run."

		print ""
		# write histories to file
		##write_histories(histories, os.path.join(os.curdir, "game_details"))

		# print results
		print "Leaderboard ("+str(game)+"):"  

		if (game == "prison"): 
			rev = False 
		else: 
			rev = True

		count = 1
		ordered_results = sorted(results.items(), key = key_fun(), reverse = rev)
		for result in ordered_results:
			print str(count)+ ". " + result[0] + ": " + str(result[1]/GAME_ITERATIONS) # print average payoff of 100 round robins
			count += 1

		print ""	
# function write_histories 
# writes history in a human readable format to disk - I don't particular like the format
# for further processing though
# parameter: histories (histories object - see run_tournement), root (string)
#
def write_histories(histories, root):
	create_folder(root)
	for strategy in histories.keys():
		folder = os.path.join(root, strategy)
		create_folder(folder)
		for opposing_strategy in histories[strategy].keys():
			mfile = os.path.join(folder, opposing_strategy + ".csv")
			f = open(mfile, "w")
			for game in histories[strategy][opposing_strategy]:
				rounds = map(lambda s:",".join(s), game)
				f.write(";".join(rounds) + "\n")

# function create_folder 
# parameter: path (string)
#
def create_folder(path):
	if not os.path.exists(path):
		os.makedirs(path)

# function key_fun
# Generates the key function for sorted. This function exists, because exec is forbidden in nested
# functions.
#
def key_fun():
	return lambda s:s[1]

if __name__ == "__main__":
	game_names = ["prison", "staghunt", "chicken", "pennies"]

	# get neccessary information from arguments
	parser = argparse.ArgumentParser()
	parser.add_argument("game", help="game", type=str, choices=game_names)
	parser.add_argument("-n", help="number of rounds", type=int, default=0)
	args = parser.parse_args()

	rounds = []
	for i in range(GAME_ITERATIONS):
		if args.n == 0:
			rounds.append(determine_rounds())
		else:
			rounds.append(args.n)

	run_tournement(args.game, rounds)
	
