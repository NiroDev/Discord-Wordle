import random

# Damit die Wörter besser verarbeitet werden können, werden Sie im Programm in Listen gespeichert.
def word_in_array(word):
    array = []
    for letter in word:
        array.append(letter)
        
    return array

# Der Wordle-Check-Algorithmus
def compare_words_wordle(word_a, word_b):
    correct_guess = 0
    for a in range(5):
        letter_a = word_a[a]
        found = False
        # In der 2. Schleife wird zuerst geprüft, ob ein Buchstabe an der richtigen Stelle steht, 
        # falls nicht, wird auf "vorhanden" geprüft.
        for b in range(len(word_b)):
            letter_b = word_b[(b + a) % len(word_b)]
            if letter_a == letter_b and b==0:
                print ("\033[1;32;40m" + letter_a, end="")
                found = True
                # Richtige positionierte Buchstaben werden aufsummiert,
                # um das Spiel bei 5 beenden zu können.
                correct_guess +=1
                break
            
            elif letter_a == letter_b:
                print ("\033[1;33;40m" + letter_a, end="")
                found = True
                break
        # Wurde der Buchstabe überhaupt nicht im Lösungswort gefunden,
        # wird dieser in der Farbe "weiß" ausgegeben.
        if found == False:
            print("\033[1;37;40m" + letter_a, end="")
        # Prüft, ob 5 richtig positionierte Buchstaben gefunden wurden.
        if correct_guess == 5:
            return True        
    return False

def wordle_frame(tries, wordle):
    guess_result = False
    for i in range(tries):
    
        # Prüfe, ob das richtige Wort geraten wurde und beende das Spiel.
        if guess_result == True:
            print ("\n\033[1;37;40m" + "Congratulations! You won!")
            break
        
        # Setze loop auf True, damit neues Wort geraten werden kann.
        loop = True
        
        # Schleife um sicherzustellen, dass das Wort 5 Buchstaben hat.
        while loop == True:
            guess = word_in_array(input ("\n\033[1;37;40m" + "Whats your guess ?:  ").lower())
            if len(guess) == 5:
                guess_result = compare_words_wordle(guess, wordle)
                loop = False
                
            else:
                print("\n\033[1;37;40m" + "Your word need to have 5 letters")
        

    

# Importiert Wörterbuch
dictionary = open("C://Python-Projekte/Wordle-Bot-Alt/words.txt").read().splitlines()
# Wählt ein zufälliges Wort aus dem Wörtbuch aus
wordle = word_in_array(random.choice(dictionary))

# Startet das Wordle-Spiel (Versuche, Lösungswort)
wordle_frame(6, wordle)
