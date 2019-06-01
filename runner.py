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


class RunError(Exception):
    pass


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
        demicalDigit = plex.Range("09")
        binaryDigit = plex.Range('01')
        
        equals = plex.Str('=')
        parentheniL = plex.Str('(')
        parentheniR = plex.Str(')')
        binaryNumber =plex.Rep1(binaryDigit)		
        name = letter + plex.Rep(letter | demicalDigit )
        space = plex.Any(" \t\n")
        print_key = plex.Str('print')
        andOperator = plex.Str('and')			
        orOperator = plex.Str('or')
        xorOperator = plex.Str('xor')
        self.variableList = {}


        # the scanner lexicon - constructor argument is a list of (pattern,action ) tuples
        lexicon = plex.Lexicon([
            (space,plex.IGNORE),
            (parentheniL, plex.TEXT),
            (parentheniR, plex.TEXT),
            (equals, plex.TEXT),
            (print_key, 'print'),
            (binaryNumber, 'number'),
            (andOperator, plex.TEXT),
            (orOperator, plex.TEXT),
            (xorOperator, plex.TEXT),
            (name, 'id' )
            ])
        
        # create and store the scanner object
        self.scanner = plex.Scanner(lexicon,fp)
        
        # get initial lookahead
        self.la,self.text = self.next_token()


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
        
        if self.la == token:
            self.la,self.text = self.next_token()
        else:
            raise ParseError("found {} instead of {}".format(self.la,token))
    
    
    def parse(self,fp):
        """ Creates scanner for input file object fp and calls the parse logic code. """
        
        # create the plex scanner for fp
        self.create_scanner(fp)
        
        # call parsing logic
        self.statement_list()
    
            
    def statement_list(self):
        
        if self.la == 'id' or self.la == 'print':
            self.statement()
            self.statement_list()
            
        elif  self.la == None:
            return
        
        else:
            raise ParseError("in statement_list: id or print expected")
            
            

    def statement(self):
        
        if self.la =='id':
            variableName = self.text
            self.match('id')
            self.match('=')
            expr = self.expretion()
            self.variableList[variableName] = expr
            
            
        elif self.la == 'print':
            self.match('print')
            expr = self.expretion()

            print('= {:b} '.format(expr))
            
        else:
            raise ParseError("in statement: id or print expected")
            
            
    
    def expretion(self):
        
        if self.la == '(' or self.la=='id' or self.la == 'number':
            ter = self.term()
            
            while self.la == 'xor':
                self.match('xor')
                ter2 = self.term()
                print(' | {:b} xor {:b} '.format(ter,ter2), end = "")
                ter = ter ^ ter2
                
            if self.la == ')' or self.la == 'id' or self.la == 'print' or self.la == None:
                return ter
                
            raise ParseError('in expretion: xor expected')                
                
        else:
            raise ParseError("in expretion: ( or id or number expected")
            
            
            
    def term(self):
        
        if self.la == '(' or self.la=='id' or self.la == 'number':
            fac = self.factor()
            
            while self.la == 'or':
                self.match('or')
                fac2 = self.factor()
                print(' | {:b} or {:b} '.format(fac,fac2), end = "")
                fac = fac | fac2
                
            if self.la == ')' or self.la == 'xor' or self.la == 'id' or self.la == 'print' or self.la == None:
                return fac
                
            raise ParseError("in term_tail: xor expected")
            
        else:
            raise ParseError("in term: ( or id or number expected")



    def factor(self):
        
        if self.la == '(' or self.la == 'id' or self.la == 'number':
            ato = self.atom()
            
            while self.la == 'and':
                self.match('and')
                ato2 = self.atom()
                print(' | {:b} and {:b} '.format(ato,ato2), end = "")
                ato = ato & ato2
                
            if self.la == ')' or self.la == 'or' or self.la == 'xor' or self.la == 'id' or self.la == 'print' or self.la == None:
                return ato
                
            raise ParseError("in factor_tail: or expected")
            
        else:
            raise ParseError("in factor: ( or id or number expected")	
            
        
        
    def atom_tail(self):
        
        if self.la == 'and':
            self.match('and')
            self.atom()
            self.atom_tail()		
        
        elif self.la == ')' or self.la == 'xor' or self.la == 'id' or self.la == 'print' or self.la == None :
            return
        
        else:
            raise ParseError("in atom_tail: and expected")			
        
        
        
    def atom(self):
        
        if self.la == '(':
            self.match('(')
            expr = self.expretion()
            self.match(')')
            return(expr)
        
        elif self.la=='id':
            variableName = self.text
            self.match('id')
            
            if variableName in self.variableList:
                
                return self.variableList[variableName]
                
            raise RunError('id variableName doesnot exist')
            
        elif self.la=='number':
            number = int(self.text,2)
            self.match('number')
            return (number)
            
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
        parser.parse(fp)
