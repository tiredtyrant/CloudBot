from cloudbot import hook
import emoji
from cloudbot.util import database
from sqlalchemy import Column, String, Table, select

table = Table(
    'emoji_aliases',
    database.metadata,
    Column('alias', String, primary_key=True),
    Column('emoji_name', String)
)

emoji_names_en = [x['en'] for x in emoji.EMOJI_DATA.values()]
emoji_names_pt = [x['pt'] for x in emoji.EMOJI_DATA.values() if 'pt' in x]

def allWordsInName(word_list, name):
    result = [word in name for word in word_list]
    return all(result)

def getNameByAlias(alias, db):
    result = db.execute(
        select(table).where(table.c.alias == alias
        )
    ).fetchone()

    if result:
        return result[0]
    else:
        return None

def getSimilar(name):
    similar = [emoji_name for emoji_name in emoji_names_en if allWordsInName(name.split(), emoji_name)]

    if similar:
        similar.sort(key = lambda i: len(i))
        return ('en', similar[0])

    similar = [x for x in emoji_names_pt if allWordsInName(name.split(), x)]

    if similar:
        similar.sort(key = lambda i: len(i))
        return ('pt', similar[0])
    
    return ('en','?')

def getEmoji(name, db = None):
    # Look at aliases before all else
    if db:
        aliasName = getNameByAlias(name, db)
        if aliasName:
            name = aliasName
    
    maybeEmoji = emoji.emojize(':{}:'.format(name.replace(' ','_')))
    
    if emoji.is_emoji(maybeEmoji):
        return maybeEmoji
    else:
        emojiTuple = getSimilar(name)
        return emoji.emojize(emojiTuple[1], language=emojiTuple[0])

@hook.command("emoji")
def emojiHook(text, db):
    """<string> [, string] - Returns an emoji from python emoji package. List of valid names: https://carpedm20.github.io/emoji/"""
    inputs = text.split(',')
    output = ''

    for input in inputs:
        output += getEmoji(input.strip(), db)

    return output

#@hook.command("alias",permissions=["botcontrol"])
@hook.command("alias")
def aliasHook(text, notice, db):
    """set <alias> <emoji name>|del <alias> - Sets an alias for an emoji name"""

    args = text.split(' ', 1)
    if len(args) < 2:
        notice("Not enough arguments.")
        return
    
    command, commandArgs = args

    if command == 'set':
        addArgs = commandArgs.split(' ',1)
        if len(addArgs) < 2:
            notice("Not enough arguments for '{}' command.",format(command))
            return
        
        alias, emoji_name = addArgs

        # Checks if 'name' returns an emoji
        if getEmoji(emoji_name) == '?':
            notice("Invalid emoji name")
            return
        
        if getNameByAlias(alias, db):
            db.execute(table.update().where(table.c.alias == alias).values(emoji_name=emoji_name))
            db.commit()
        else:
            db.execute(table.insert().values(alias=alias, emoji_name=emoji_name))
            db.commit()

        notice("Alias set")

    elif command == 'del':
        if getNameByAlias(commandArgs, db):
            db.execute(table.delete().where(table.c.alias == commandArgs))
            db.commit()
            notice("Alias removed")
        else:
            notice("No such alias")

    else:
        notice("Unknown command '{}'".format(command))

    return

