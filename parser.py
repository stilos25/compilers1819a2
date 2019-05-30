#!/usr/bin/env python3
# -*- coding: utf_8 -*-

"""
Example of recursive descent parser written by hand using plex module as scanner
NOTE: This progam is a language recognizer only.
Sample grammar from p.242 of:
Grune, Dick, Jacobs, Ceriel J.H., "Parsing Techniques, A Practical Guide" 2nd ed.,Springer 2008.
Session  -> Facts Question | ( Session ) Session
Facts    -> Fact Facts | ε
Fact     -> ! string
Question -> ? string
FIRST sets
----------
Session:  ( ? !
Facts:    ε !
Fact:     !
Question: ?
FOLLOW sets
-----------
Session:  # )
Facts:    ?
Fact:     ! ?
Question: # )
  
"""


import plex



class ParseError(Exception):
	""" A user defined exception class, to describe parse errors. """
	pass



class MyParser:
	""" A class encapsulating all parsing functionality
	for a particular grammar. """
	
	def create_scanner(self,fp):
		""" Creates a plex scanner for a particular grammar 
		to operate on file object fp. """

		# define some pattern constructs
		letter = plex.Range("AZaz")
		digit = plex.Range("09")

		string = plex.Rep1(letter | digit)
		operator = plex.Any("!?()")		
		space = plex.Any(" \t\n")

		# the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
		lexicon = plex.Lexicon([
			(operator,plex.TEXT),
			(space,plex.IGNORE),
			(string, 'string')
			])
		
		# create and store the scanner object
		self.scanner = plex.Scanner(lexicon,fp)
		
		# get initial lookahead
		self.la,self.val = self.next_token()


	def next_token(self):
		""" Returns tuple (next_token,matched-text). """
		
		return self.scanner.read()		

	
	def position(self):
		""" Utility function that returns position in text in case of errors.
		Here it simply returns the scanner position. """
		
		return self.scanner.position()
	

	def match(self,token):
		""" Consumes (matches with current lookahead) an expected token.
		Raises ParseError if anything else is found. Acquires new lookahead. """ 
		
		if self.la==token:
			self.la,self.val = self.next_token()
		else:
			raise ParseError("found {} instead of {}".format(self.la,token))
	
	
	def parse(self,fp):
		""" Creates scanner for input file object fp and calls the parse logic code. """
		
		# create the plex scanner for fp
		self.create_scanner(fp)
		
		# call parsing logic
		self.session()
	
			
	def session(self):
		""" Session  -> Facts Question | ( Session ) Session """
		
		if self.la=='!' or self.la=='?':
			self.facts()
			self.question()
		elif self.la=='(':
			self.match('(')
			self.session()
			self.match(')')
			self.session()	
		else:
			raise ParseError("in session: !, ? or ( expected")
			 	
	
	def facts(self):
		""" Facts -> Fact Facts | ε """
		
		if self.la=='!':
			self.fact()
			self.facts()
		elif self.la=='?':	# from FOLLOW set!
			return
		else:
			raise ParseError("in facts: ! or ? expected")
	
	
	def fact(self):
		""" Fact -> ! string """
		
		if self.la=='!':
			self.match('!')
			self.match('string')
		else:
			raise ParseError("in fact: ! expected")
			 	

	def question(self):
		""" Question -> ? string """
		
		if self.la=='?':
			self.match('?')
			self.match('string')
		else:
			raise ParseError("in question: ? expected")

		
# the main part of prog

# create the parser object
parser = MyParser()

# open file for parsing
with open("recursive-descent-parsing.txt","r") as fp:

	# parse file
	try:
		parser.parse(fp)
	except plex.errors.PlexError:
		_,lineno,charno = parser.position()	
		print("Scanner Error: at line {} char {}".format(lineno,charno+1))
	except ParseError as perr:
		_,lineno,charno = parser.position()	
		print("Parser Error: {} at line {} char {}".format(perr,lineno,charno+1))
