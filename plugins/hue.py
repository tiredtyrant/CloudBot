from cloudbot import hook
import random
import re
import emoji

nick_re = re.compile("^[A-Za-z0-9_|.\-\]\[\{\}]*$", re.I)


def is_valid(target):
    """ Checks if a string is a valid IRC nick. """
    if nick_re.match(target):
        return True
    else:
        return False

flexface = [
    u'\u1559\u0028\u2580\u033f\u033f\u0139\u032f\u033f\u033f\u2580\u033f \u033f\u0029 \u1557',
    u'\u1566\u0f3c \u007e \u2022\u0301 \u2092 \u2022\u0300 \u007e \u0f3d\u1564',
    u'\u1559\u0f3c\u0e88\u0644\u035c\u0e88\u0f3d\u1557',
    u'\u1559\u0028 \u0361\u25c9 \u035c \u0296 \u0361\u25c9\u0029\u1557',
    u'\u1559\u0028\u21c0\u2038\u21bc\u2036\u0029\u1557',
    u'\u1559\u0f3c\u25d5 \u1d25 \u25d5\u0f3d\u1557',
    u'\u1566\u0f3c\u0e88\u0644\u035c\u0e88\u0f3d\u1564',
    u'\u1559\u0028 \u0361\u00b0 \u035c\u0296 \u0361\u00b0\u0029\u1557',
    u'\u1566\u0028\u00f2\u005f\u00f3\u02c7\u0029\u1564',
    u'\u1566\u0f3c \u2022\u0301 \u2038 \u2022\u0300 \u0f3d\u1564'
]

@hook.command("flex","malhei","malhou",autohelp=False)
def flex(message, conn):
    message(random.choice(flexface))

#case insensitive marker: (?i)
#https://stackoverflow.com/questions/500864/case-insensitive-regular-expression-without-re-compile
@hook.regex(r'(?i)malhei')
def rflex(message, conn):
    #if random.randint(1,10) <= 5:
    message(random.choice(flexface))

@hook.regex(r'(?i)nadei')
def rnadei(message, conn):
    message(random.choice(flexface) + ' glub')

@hook.regex(r'(?i)caminhei')
def rcaminhei(message, conn):
    return emoji.emojize(':man_walking:')

@hook.regex(r'(?i)corri')
def rcorri(message, conn):
    return emoji.emojize(':person_running:')

#disabled because there's an 'official' one already
#@hook.command("shrug")
#def shrug(message,conn):
#    message(u'\u00af\u005c\u005f\u0028\u30c4\u0029\u005f\u002f\u00af')

@hook.regex("shit swap")
def shitswap(message,conn):
    if random.randint(1,10) <= 4:
        message(u'))<>((')

@hook.regex("bo+rk")
def bork(message,conn):
    if random.randint(1,10) <= 4:
        message(u'stop it son, you are doing me a frighten')

@hook.command("dis")
def disapproval(text,conn):
    user = text.strip()
    if is_valid(user):
        return u'{} : \u0ca0\u005f\u0ca0'.format(user)
    else:
        return u'\u0ca0\u005f\u0ca0'

ayyregex = re.compile('^ayy$', re.IGNORECASE)

@hook.regex(ayyregex)
def ayy(message,conn):
    num = random.randint(1,10)
    if num <= 4:
        if num % 2:
            message(u'lmao')
        else:
            message(u'macarena')
