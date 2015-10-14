#!/usr/bin/env python
"""
Mastermind solver
S. Altekar 2/27/2015
"""

import itertools
import random


NCOLORS = 6   # total number of colors used (from 0 to NCOLORS-1)
NPLACES = 4   # total number of peg positions
MAXCOMBINATIONS = NCOLORS**NPLACES
sixcolors = ['Pink','Violet','Orange','White','Green','Yellow']
if NCOLORS == 6:
  colorlist = ''.join([c[0] for c in sixcolors])  # e.g. colorlist = 'PVOWGY'
else:
  colorlist = [str(ii) for ii in range(NCOLORS)]   # colors represented by numbers if not six colors


def vector_to_index( vec ):
  'Converts a vector representing peg colors into an index'
  index = 0;
  for ii in range(NPLACES-1,-1,-1):
    index *= NCOLORS
    index += vec[ii]
  return index
       

def index_to_vector( index ):
  'Converts an index into a vector representing peg colors'
  vec = [0]*NPLACES
  for ii in range(NPLACES):
    (index,entry) = divmod(index,NCOLORS)
    vec[ii] = entry
  return vec


def score( guess_index, secret_index ):
  'Compute mastermind score given guess and secret indices'
  guess_color_vec = [0]*NCOLORS   # these count number of occurances of each color
  secret_color_vec = [0]*NCOLORS
  correct_position = 0            # count pegs with correct color and position
  for ii in range(NPLACES):
    (guess_index,guess_peg) = divmod(guess_index,NCOLORS)
    (secret_index,secret_peg) = divmod(secret_index,NCOLORS)
    if guess_peg == secret_peg:
      correct_position += 1
    else:
      guess_color_vec[guess_peg] += 1
      secret_color_vec[secret_peg] +=1 
  correct_color = sum(itertools.imap(min,guess_color_vec,secret_color_vec)) 
  return (correct_position, correct_color)


def evaluate_guess( guess_index, working_set ):
  'Counts how many times each score occurs for given guess against working set and returns highest count'
  score_occurance = [0]*(NPLACES+1)*(NPLACES+1);
  for ii in range(MAXCOMBINATIONS):
    if working_set[ii]:
      (black,white) = score(guess_index,ii)
      score_occurance[black*(NPLACES+1)+white] += 1
  highest_occurance = 0
  for ii in range((NPLACES+1)*(NPLACES+1)):
    if score_occurance[ii] > 0:
      if score_occurance[ii] > highest_occurance:
        highest_occurance = score_occurance[ii]
  return highest_occurance


def find_best_guess( working_set ):
  'Find the minimax best guess that minimizes the maximum number of possibilities'
  best_evaluation = [MAXCOMBINATIONS]*2
  best_guess = [0]*2
  for ii in range(MAXCOMBINATIONS):
      evaluation = evaluate_guess( ii, working_set )
      if evaluation < best_evaluation[working_set[ii]]:
        best_evaluation[working_set[ii]] = evaluation
        best_guess[working_set[ii]] = ii
  return best_guess[best_evaluation[1] <= best_evaluation[0]]


def reduce_working_set( guess_index, current_score, working_set ):
  'Reduce working set to those entries compatible with current score'
  for ii in range(MAXCOMBINATIONS):
    if working_set[ii] and not (score(guess_index,ii) == current_score):
      working_set[ii] = False


def print_banner():
  print '\n'
  print 'Welcome!  I am an interactive MasterMind solver.'
  print 'Challenge me with a MasterMind puzzle.'
  print 
  print 'The peg colors are:',
  if NCOLORS == 6:
    print ', '.join(sixcolors)
  else:
    print ', '.join(c for c in colorlist)
  print
  print 'All scores are input as a two digit number'
  print '  - the first digit indicates the number of pegs in the correct position'
  print '  - the second digit indicates the number of pegs with the right color'
  print '\n'
  

def interactive_input( guess_index, working_set ):
  class HarmlessException(Exception):
    pass
  print 'There are currently ', working_set.count(True), ' possibilities.'
  print 'I guess: ', ' '.join([colorlist[ii] for ii in index_to_vector(guess_index)]),
  print ' which surprisingly is not a possible solution.' if not working_set[guess_index] else ''
  while True:
    try:
      user_input = raw_input('Enter score: ')
      if user_input.upper() == 'L':
        print '\nList of Current Possibilities'
        for ii in range(MAXCOMBINATIONS):
          if working_set[ii]:
            print ' '.join([colorlist[jj] for jj in index_to_vector(ii)])
        raise HarmlessException()
      elif user_input.upper() == 'Q':
        raise KeyboardInterrupt()
      if not len(user_input) == 2:
        raise ValueError()
      score = divmod(int(user_input),10)
      if score[0] < 0 or score[1] < 0 or score[0] > NPLACES or score[1] > NPLACES or score[0]+score[1]>NPLACES:
        raise ValueError()
      break
    except ValueError:
      print 'Unexpected input, try again.'
    except HarmlessException:
      pass 
  return score


def random_first_guess():
  'Create random first guess for 4 places and 6 colors case'
  rcolors = random.sample(xrange(NCOLORS),2)
  rplace = random.sample(xrange(NPLACES),2)
  rguess = [rcolors[1]]*NPLACES
  rguess[rplace[0]] = rcolors[0]
  rguess[rplace[1]] = rcolors[0]
  return vector_to_index(rguess)
 
      
def play_game( secret_index = None ):
  'Plays mastermind game interactively or in simulation (if secret_index is provided)'
  if secret_index == None:
    print_banner()
  working_set = [True]*MAXCOMBINATIONS
  game_log = []
  current_score = (0,0)
  nguess = 0
  while not current_score == (NPLACES,0):
    if nguess == 0 and NPLACES == 4 and NCOLORS == 6:
      guess_index = random_first_guess()
    else:
      guess_index = find_best_guess(working_set)
    if secret_index == None:
      current_score = interactive_input( guess_index, working_set )
    else:
      current_score = score( guess_index, secret_index )    
    nguess += 1
    game_log.append( (working_set.count(True), guess_index, current_score, list(working_set)) )
    reduce_working_set( guess_index, current_score, working_set )
    if working_set.count(True) == 0 and secret_index == None:
      print 'You have made a scoring error, a solution is not possible.'
      print 'Please try again.'
      break
  return (nguess,game_log)      


def compute_game_stats():
  'Compute maximum number and average number of guesses required by this mastermind solver.'
  nguess = [0]*MAXCOMBINATIONS
  game_log = [None]*MAXCOMBINATIONS
  for ii in range(0,MAXCOMBINATIONS):
    (nguess[ii],game_log[ii]) = play_game(ii)
    print ii, nguess[ii]
  print 'maximum number of guesses: ', max(nguess)
  print 'average number of guesses: ', sum(nguess)/float(MAXCOMBINATIONS)
  

if __name__ == '__main__':
  try:
    play_game()
  except KeyboardInterrupt:
    print '\nBye.  Come back soon.'

