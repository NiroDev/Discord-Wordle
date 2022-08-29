import random
from enum import Enum

import os

PROJECT_PATH=os.path.dirname(os.path.realpath(__file__)) + '\\'

class LetterComparison(Enum): 
    Exact_Match = 1
    Match = 2
    No_Match = 3
    

class Wordle:
    
    def __init__(self):
        """ Beim Aufruf von !newgame 2 ist das Spiel nicht beendet worden.
        Zusätzlich ist aufgefallen, dass noch die alten guesses von vorherigen Spielen in der Liste enthalten waren.
        Nicht-statische Variablen wurden in die __init__ verschoben. Klassen-Variablen werden von allen Objekten geteilt."""
        
        self.__word = random.choice(open(PROJECT_PATH + 'words.txt').read().splitlines()).lower()
        self.tries = 6
        self.guesses = []

    def get_guesses(self):
        return self.guesses

    def get_word(self): # for testing
        return self.__word

    def get_tries(self):
        return self.tries

    def tries_left(self):
        return self.tries - len(self.guesses)
    
    def check_win(self, guess):
        return guess.lower() == self.__word

    def can_guess(self):
        return len(self.guesses) < self.tries
    
    def compare_words_wordle(self, guess):
        matches = list()
        
        for i, letter in enumerate(guess.lower()):
            if letter == self.__word[i]:
                matches.append(LetterComparison.Exact_Match)
            elif letter in self.__word:
                matches.append(LetterComparison.Match)
            else:
                matches.append(LetterComparison.No_Match)
        return matches
            
    def restart(self):
        self.guesses.clear()
      
    def wordle_frame(self):
        while self.can_guess():
            guess = list(input ("\n\033[1;37;40m" + "Whats your guess ?:  ").lower())
            if len(guess) != 5:
                print("\n\033[1;37;40m" + "Your word need to have 5 letters")
                continue
            # Geratenes Wort in guesses speichern
            self.guesses.append(guess)
            # Gewonnen prüfen
            if self.check_win(guess):
                print(("\n\033[1;37;40m" + "Congratz!"))
                return
            
            matches = self.compare_words_wordle(guess)
            
            for i, match_type in enumerate(matches):
                match match_type:
                    case LetterComparison.Exact_Match:
                        print("\033[1;32;40m" + guess[i], end="")
                    case LetterComparison.Match:
                        print("\033[1;33;40m" + guess[i], end="")
                    case LetterComparison.No_Match:
                        print("\033[1;37;40m" + guess[i], end="")
        
        print(("\n\033[1;37;40m" + "Loose"))
         
        