# IMPORTAÇÕES
# Utilizar Python3.9
import random
# WebSocket do OBS Studio 27
import simpleobsws # <--- Versão 0.0.7 para ter suporte ao 4.9.* do plugin do OBS
import discord # <--- toda mágica do bot
from discord.ext import commands
import asyncio # <--- assincronismo

# VARIÁVEIS
loop = asyncio.get_event_loop()
ws = simpleobsws.obsws(host = '127.0.0.1', port=4444, password = 'solidos', loop=loop) # <---mudar ip do host caso usar em outro pc!
bot = commands.Bot(command_prefix='!') # <--- prefixo de comando do bot

# DEFINIÇÕES
async def make_request(Rolagem='1d20'):
    # conectar ao OBS
    await ws.connect() 
    # mostrar o site na cena 'Cena'
    await ws.call(
        'CreateSource', {
            'sourceName':'SolidosAleatorios', # <--- coloquei o nome do bot
            'sourceKind':'browser_source', 
            'sceneName':'Cena', # <--- colocar o nome da cena que está no OBS
            'setVisible':True
        }
    )
    # configurações para a cena
    # a sintaxe mudou na versão 5.*
    # baseado no https://andylawton.com/home/bee-dice-roller
    await ws.call(
        'SetSourceSettings', {
            'sourceName':'SolidosAleatorios', 
            'sourceSettings': {
                'css': '',
                'height': 1080, # <--- resolução/altura no OBS
                'shutdown': True, 
                'url': 'dice.bee.ac/?noresult&dicehex=990099&labelchex= FF8000&chromahex=00ff00&roll&d='+Rolagem, 
                'width': 1920 # <--- resolução/largura no OBS
            }
        }
    )
    # adicionar o chroma key na fonte do bot
    await ws.call(
        'AddFilterToSource', {
            'sourceName':'SolidosAleatorios',
            'filterName':'Chroma Key',
            'filterType': 'chroma_key_filter', 
            'filterSettings':{
            }
        }
    )
    # tem em segundos da duração da fonte
    await asyncio.sleep(10)
    # deletar a fonte da cena
    await ws.call(
        'DeleteSceneItem', {
            'scene':'Cena', # <--- sempre lembrar do nome da cena
            'item':{
                'name':'SolidosAleatorios'
            }
        }
    )
    # desconectar do OBS
    await ws.disconnect()

# COMANDOS  
# comandos de rolagens básicas          
@bot.command(name='r', help='Simule a rolagens de dados. Utilize d. ex. 3d6')
async def Rolagem(ctx, rolagem):
    rolagem = rolagem.split('d')
    n_de_dados = int(rolagem[0])
    n_de_lados = int(rolagem[1])
    dados = [
        str(random.choice(range(1, n_de_lados + 1)))
        for _ in range(n_de_dados)
    ]
    await ctx.send(', '.join(dados))
    r = 1
    resultados = '@' + str(dados[0]) 
    for x in dados[1:]:
        resultados = resultados + '%2' + str(dados[r]).zfill(2)
        r = r+1
    await make_request(str(n_de_dados)+'d'+str(n_de_lados)+resultados)

# Rodando o bot
bot.run('TOKEN') # <--- TOKEN DO BOT DO DISCORD ATENÇÃO MÁXIMA