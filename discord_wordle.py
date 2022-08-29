from wordle import Wordle, LetterComparison, PROJECT_PATH
from PIL import Image, ImageDraw, ImageFont
from enum import Enum
import os

class Rule(Enum):
    Default = 1
    User_Once = 2
    Once_In_A_Row = 3


class DiscordWordle(Wordle):
    def __init__(self, tries):
        super().__init__()
        self.__rule = Rule.Default
        self.tries = tries
        self.lastguesser = 0
        self.guesser = set()
        self.initial_message = None
        self.board_message = None

    async def set_rule(self, ctx, rule, membercount):
        if(rule == Rule.User_Once and membercount < self.tries ):
            self.tries = membercount - 1
            await ctx.send( 'Anzahl der Versuche angepasst auf: ' + str(self.tries))
        elif(rule == Rule.User_Once and membercount == 1):
            return False # geht nicht mit nur 1 Spieler
        
        self.__rule = rule
        return True

    def get_rule(self):
        return self.__rule
    
    def add_guess(self, uid, guess):
        self.guesser.add(uid)
        self.lastguesser = uid
        self.guesses.append(guess)
    
    def user_meets_rule(self, ctx):
        match self.__rule:
            case Rule.User_Once:
                return ctx.author.id not in self.guesser
            case Rule.Once_In_A_Row:
                return ctx.author.id != self.lastguesser
            case Rule.Default:
                return True
                
    def restart(self):
        super().restart()
        self.guesser.clear()
        self.lastguesser = 0

    def create_board(self, path, image_name):
        margin = 2
        lettersize = 45                   # Größe eines Buchstabenfeldes
        blocksize = lettersize + margin*2 # Größe eines Buchstabenfeldes mit Abstand

        width = 5 * blocksize
        height = len(self.guesses) * blocksize
        
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0)) # transparenter Hintergrund
        draw = ImageDraw.Draw(img)

        for row, guess in enumerate(self.guesses):      # Guesses durchgehen, zeilenweise
            matches = self.compare_words_wordle(guess)
            for col, match_type in enumerate(matches):  # Buchstaben durchgehen, spaltenweise
                col_offset = col * blocksize + margin
                row_offset = row * blocksize + margin
                match match_type:
                    case LetterComparison.Exact_Match:
                        draw.rectangle((col_offset, row_offset, col_offset + lettersize, row_offset + lettersize), fill='#6aaa64', outline='#538d4e') # green
                    case LetterComparison.Match:
                        draw.rectangle((col_offset, row_offset, col_offset + lettersize, row_offset + lettersize), fill='#c9b458', outline='#b59f3b') # yellow
                    case LetterComparison.No_Match:
                        draw.rectangle((col_offset, row_offset, col_offset + lettersize, row_offset + lettersize), fill='#86888a', outline='#121213') # grey
                
                textfont = ImageFont.truetype(PROJECT_PATH + 'Arial_Bold.ttf', 25)
                text = guess[col].upper()
                textwidth, textheight = draw.textsize(text, font=textfont)
                draw.text((col_offset + lettersize/2 - textwidth/2, row_offset + lettersize/2 - textheight/2), text, fill='#FFF', font=textfont)
                
        if(os.path.isdir(path) == False):
            os.mkdir(path)
            
        img.save(path + '\\' + image_name, 'PNG')