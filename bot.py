import discord
from discord.ext import commands

from discord_wordle import DiscordWordle, Rule
from wordle import PROJECT_PATH
from discord.ext.commands import has_permissions # https://discordpy.readthedocs.io/en/stable/api.html#discord.Permissions

bot = commands.Bot(command_prefix='!', description='!help')

current_games = {}

### Checks ###

def game_running():
    async def predicate(ctx):
        if( ctx.channel.id not in current_games.keys() ):
            await send_error(ctx, 'In diesem Channel läuft derzeit kein Spiel. Du kannst eins mit ``' + bot.command_prefix + 'newgame`` erstellen.')
            return False
        return True
    return commands.check(predicate)


### Help functions ###
async def send_success(ctx, msg, delete_after=3):
        embed=discord.Embed(title=msg, color=discord.Color.green())
        return await ctx.send(embed=embed, delete_after=delete_after)
        
async def send_error(ctx, msg, delete_after=3):
        embed=discord.Embed(title=msg, color=discord.Color.red())
        return await ctx.send(embed=embed, delete_after=delete_after)

async def set_status():
    count = len(current_games)
    if(count > 0):
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name= str(count) + (' Runden' if count > 1 else ' Runde') + ' Wordle'))
    else:
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=" nach Spielen!"))


### Commands ###

@bot.command()
#@commands.has_role('gamemaster')      # Name der Rolle
@has_permissions(administrator=True)
async def newgame(ctx, tries = 6, rule = ""):
    await ctx.message.delete()
    if( ctx.channel.id in current_games.keys() ): # Existiert bereits
        await send_error(ctx, 'Es läuft noch ein Spiel. Bitte beende es zuerst mit ``' + bot.command_prefix + 'endgame`` das laufende Spiel.')
        return
    
    if(tries <= 0):
        await send_error(ctx, 'Bitte geben Sie eine gültige Anzahl an Versuchen an.')
        return
    
    game = DiscordWordle(tries)
    current_games[ctx.channel.id] = game

    if( len(rule) > 0 ):
        await setrule( ctx, rule )

    game.initial_message = await send_success(ctx, 'Spiel erstellt. Du kannst ein 5-Buchstaben Wort mit ``' + bot.command_prefix + 'guess <word>`` raten.', None)

    await set_status()

@bot.command()
@game_running()
@has_permissions(administrator=True)
async def setrule(ctx, rule = ""):
    await ctx.message.delete()
    if(len(rule) == 0):
        await ctx.send('``once`` -> Jeder Spieler darf nur 1x raten\n``once_row`` -> Es darf nicht 2x in Folge geraten werden')
        return

    game = current_games[ctx.channel.id]
    valid = False

    channel = bot.get_channel(ctx.channel.id)
    members = channel.members
    membercount = sum(x is not x.bot for x in members)

    if(rule.lower() == "once"):
        valid = await game.set_rule(ctx, Rule.User_Once, membercount)
    elif(rule.lower() == "once_row"):
        valid = await game.set_rule(ctx, Rule.Once_In_A_Row, membercount)
    else:
        await send_error(ctx, 'Keine gültige Regel. Gültig sind:')
        await setrule(ctx)
        return

    if(valid == False):
        await send_error(ctx, 'Diese Regel kann hier nicht angewandt werden.')
    else:
        await send_success(ctx, 'Regel gesetzt.')

@bot.command()
@game_running()
async def guess(ctx, guess):
    await ctx.message.delete()
    game = current_games[ctx.channel.id]

    if len(guess) != 5 or guess.isalpha() == False:
        await send_error(ctx, 'Das geratene Wort muss aus 5 Buchstaben bestehen.')
        return

    if(game.user_meets_rule(ctx) == False):
        match game.get_rule():
            case Rule.User_Once:
                await send_error(ctx, 'Jeder Spieler hat nur einen Versuch.')
            case Rule.Once_In_A_Row:
                await send_error(ctx, 'Warten Sie, bis jemand anderes geraten hat.')
        return

    game.add_guess(ctx.author.id, guess.lower())
    
    await guesses(ctx, False)

    if(game.check_win(guess)):
        await send_success(ctx, 'Juhuu, gewonnen!', None)
    elif(game.tries_left() == 0):
        await send_error(ctx, 'Die maximale Anzahl an Versuchen wurde erreicht.', None)
    else:
        return
    
    # In beiden Fällen oben wird das Spiel beendet (endgame() geht nur als Admin, kann daher hier nicht aufgerufen werden)
    if(game.initial_message):
        await game.initial_message.delete()
    current_games.pop(ctx.channel.id)
    await set_status()

@bot.command()
@game_running()
async def guesses(ctx, delete_message=True):
    if(delete_message):
        await ctx.message.delete()

    game = current_games[ctx.channel.id]
    guesses = game.get_guesses()
    if(len(guesses) == 0):
        await send_error(ctx, 'Es wurde noch kein Wort geraten. Du kannst eins mit ``' + bot.command_prefix + 'guess <word>`` raten.')
        return
    
    triesleft = game.tries_left()
    tries = game.get_tries()
    
    path = PROJECT_PATH + 'boards'
    filename = str(ctx.channel.id) + '.png'
    game.create_board(path, filename)

    if(game.board_message != None):
        await game.board_message.delete()

    game.board_message = await ctx.send(file = discord.File(path + '\\' + filename), content = '**Versuche: ' + str(tries - triesleft) + '/' + str(tries) + '**')


@bot.command()
@game_running()
@has_permissions(administrator=True)
async def word(ctx):
    await ctx.message.delete()
    dm_channel = await ctx.author.create_dm()
    await dm_channel.send('Das Wort lautet **||' + current_games[ctx.channel.id].get_word() + '||**')

@bot.command()
@game_running()
@has_permissions(administrator=True)
async def restart(ctx):
    await ctx.message.delete()
    game = current_games[ctx.channel.id]
    game.restart()
    await send_success(ctx, 'Das Spiel wurde neu gestartet.')

@bot.command()
@game_running()
@has_permissions(administrator=True)
async def endgame(ctx):
    await ctx.message.delete()
    game = current_games[ctx.channel.id]
    if(game.initial_message):
        await game.initial_message.delete()
    current_games.pop(ctx.channel.id)
    await set_status()
    await send_success(ctx, 'Das Spiel wurde manuell beendet.', None)


### Events ###

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await send_error(ctx, 'Diesen Befehl gibt es nicht.')
    elif isinstance(error, commands.MissingRequiredArgument):
        await send_error(ctx, 'Es fehlen noch Angaben bei diesem Befehl.')
    elif isinstance(error, commands.MissingPermissions):
        await send_error(ctx, 'Du hast nicht die nötigen Berechtigungen zum Ausführen dieses Befehls')
    else:
        await send_error(ctx, 'Ein unerwarteter Fehler ist aufgetreten: ' + error.args[0])


    # Gibt auch commands.errors.CheckFailure für alle allgemein

@bot.event
async def on_ready():
    await set_status()
    print('Bot gestarted.')

#@bot.listen()
#async def on_message(message):
    #await message.channel.send('A reply.. somehow.')
    #await bot.process_commands(message)

bot.run('TOKEN HERE')