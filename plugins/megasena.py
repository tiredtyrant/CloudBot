import json
import urllib.request
import locale
from cloudbot import hook

@hook.command("megasena", autohelp=False)
def mega(message, bot):
    """Returns Mega Sena results"""
    request = urllib.request.Request(bot.config.get("api_keys", {}).get("megasena_url", None), headers={'Cookie': 'security=true; path=/'})
    megasena = json.loads(urllib.request.urlopen(request).read().decode('utf8'))

    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    if megasena['acumulado'] == 'true':
        message('(Concurso {} - {}) {} Acumulou: {}'.format(megasena['numero'],
                                                            megasena['dataApuracao'],
                                                            [int(s)for s in megasena['listaDezenas']],
                                                            locale.currency(megasena['valorAcumuladoProximoConcurso'], grouping=True)))
    else:
        message('(Concurso {} - {}) {} Ganhado{}: {} - Prêmio: {}'.format(megasena['numero'],
                                                                          megasena['dataApuracao'],
                                                                          [int(s) for s in megasena['listaDezenas']],
                                                                          'rxs' if len(megasena['listaMunicipioUFGanhadores']) > 1 else 'r(x)',
                                                                          len(megasena['listaMunicipioUFGanhadores']),
                                                                          locale.currency(megasena['listaRateioPremio'][0]['valorPremio'], grouping=True)))
