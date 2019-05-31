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
	
			
	def statement_list(self):
		
		if self.la=='id' or self.la=='print':
			self.statement()
			self.statement_list()
			
		elif  self.la==None:
			return
		
		else:
			raise ParseError("in statement_list: id or print expected")
			
			

	def statement(self):
		
		if self.la=='id':
			self.match('id')
			self.match('=')
			self.expretion()
			
		elif self.la=='print':
			self.match('print')
			self.expretion()
			
		else:
			raise ParseError("in statement: id or print expected")
			
			
	
	def expretion(self):
		
		if self.la=='parentheniL' or self.la=='id' or self.la=='number':
			self.term()
			self.term_tail()
			
		else:
			raise ParseError("in expretion: ( or id or number expected")
			
			
			
	def term_tail(self):
		
		if self.la=='xor':
			self.match('xor')
			self.term()
			self.term_tail()
		
		elif self.la=='parentheniR' or self.la=='id' or self.la=='print':
			return
		
		else:
			raise ParseError("in term_tail: xor expected")
		
	
		
	
	def term(self):
		
		if self.la=='parentheniL' or self.la=='id' or self.la=='number':
			self.factor()
			self.factor_tail()
			
		else:
			raise ParseError("in factor: ( or id or number expected")
			
			
		
	def factor_tail(self):
		
		if self.la=='or':
			self.match('or')
			self.factor()
			self.factor_tail()
			
		elif self.la=='parentheniR' or self.la=='xor' or self.la=='id' or self.la=='print':
			return
		
		else:
			raise ParseError("in factor_tail: or expected")
			
		
		
	def factor(self):
		
		if self.la=='parentheniL' or self.la=='id' or self.la=='number':
			self.atom()
			self.atom_tail()
			
		else:
			raise ParseError("in factor: ( or id or number expected")	
			
		
		
	def atom_tail(self):
		
		if self.la=='and':
			self.match('and')
			self.atom()
			self.atom_tail()		
		
		elif self.la=='parentheniR' or self.la=='xor' or self.la=='id' or self.la=='print':
			return
		
		else:
			raise ParseError("in atom_tail: and expected")			
		
		
		
	def atom(self):
		
		if self.la=='parentheniL':
			self.match('parentheniL')
			self.expretion()
			self.match('parentheniR')
		
		elif self.la=='id':
			self.match('id')
			
		elif self.la=='number':
			self.match('number')
			
		else:
			raise ParseError("in atom: ( or id or number expected")		
	


	
'''									sxolia palios kodikas	
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

					
					sxolia palios kodikas
'''
		
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
