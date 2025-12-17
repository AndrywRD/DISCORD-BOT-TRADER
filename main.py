import random
import os
import json
import time
import asyncio
from pathlib import Path
import discord
from discord.ext import commands
from typing import List, Dict, Any, Optional

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_DIR = Path(__file__).parent
BALANCES_FILE = DATA_DIR / "balances.json"
LAST_CLAIM_FILE = DATA_DIR / "last_claims.json"
CARDS_FILE = DATA_DIR / "cards.json"
JOIN_TIMES_FILE = DATA_DIR / "join_times.json"
WINS_FILE = DATA_DIR / "wins.json"
SPENT_FILE = DATA_DIR / "spent_coins.json"

def get_spent(user_id: str) -> int:
    data = _load_json(SPENT_FILE)
    return int(data.get(user_id, 0))

def add_spent(user_id: str, amount: int):
    data = _load_json(SPENT_FILE)
    data[user_id] = int(data.get(user_id, 0)) + int(amount)
    _save_json(SPENT_FILE, data)


def _load_json(path: Path):
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json(path: Path, data):
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def get_wins(user_id: str) -> int:
    data = _load_json(WINS_FILE)
    return int(data.get(user_id, 0))

def add_win(user_id: str):
    data = _load_json(WINS_FILE)
    data[user_id] = int(data.get(user_id, 0)) + 1
    _save_json(WINS_FILE, data)


def _load_join_times():
    return _load_json(JOIN_TIMES_FILE)


def _save_join_times(data):
    _save_json(JOIN_TIMES_FILE, data)


def get_balance(user_id: str) -> int:
    data = _load_json(BALANCES_FILE)
    return int(data.get(user_id, 0))


def add_balance(user_id: str, amount: int):
    data = _load_json(BALANCES_FILE)
    data[user_id] = int(data.get(user_id, 0)) + int(amount)
    _save_json(BALANCES_FILE, data)


def deduct_balance(user_id: str, amount: int) -> bool:
    data = _load_json(BALANCES_FILE)
    current = int(data.get(user_id, 0))
    if current < amount:
        return False
    data[user_id] = current - int(amount)
    _save_json(BALANCES_FILE, data)
    return True


def can_claim_daily(user_id: str, cooldown_seconds: int = 24 * 60 * 60):
    data = _load_json(LAST_CLAIM_FILE)
    last = float(data.get(user_id, 0))
    now = time.time()
    if now - last >= cooldown_seconds:
        return True, 0
    return False, int(cooldown_seconds - (now - last))


def set_claim_time(user_id: str):
    data = _load_json(LAST_CLAIM_FILE)
    data[user_id] = time.time()
    _save_json(LAST_CLAIM_FILE, data)


def get_user_cards(user_id: str):
    data = _load_json(CARDS_FILE)
    return data.get(user_id, [])


def add_card_to_user(user_id: str, carta: dict, raridade: str):
    data = _load_json(CARDS_FILE)
    user_cards = data.get(user_id, [])
    entry = dict(carta)
    entry["raridade"] = raridade
    user_cards.append(entry)
    data[user_id] = user_cards
    _save_json(CARDS_FILE, data)


def card_already_exists(user_id: str, carta: dict, raridade: str) -> bool:
    user_cards = get_user_cards(user_id)
    for card in user_cards:
        if (card.get("nome") == carta.get("nome") and
            card.get("ataque") == carta.get("ataque") and
            card.get("vida") == carta.get("vida") and
            card.get("raridade") == raridade):
            return True
    return False

def escolher_5_aleatorias(lista):
    if len(lista) <= 5:
        return lista  # se tiver 5 ou menos cartas, usa todas
    return random.sample(lista, 5)

# CARGOS DO SERVIDOR PARA O SISTEMA DE RANKINGS

ROLE_TOP_WINS = "👑 Campeão Supremo"
ROLE_TOP_SPENT = "💰 Magnata do Servidor"

EMOJI_RARITY = {
    "Comum": "⚪",
    "Rara": "🔵",
    "Épica": "🟣",
    "Lendária": "🌟"
}

cartas = {
    "Comum": [
        {"nome": "andryw", "imagem": "https://cdn.discordapp.com/attachments/785317706274308117/1448844425160556586/ANDRYW_RUHAN.jpeg", "ataque": 500, "vida": -500},
        {"nome": "É MAFIA FAMILIA", "imagem": "https://cdn.discordapp.com/attachments/785317706274308117/1448844530081337567/MAFIA.PNG", "ataque": 500, "vida": 1000},
        {"nome": "EVOLUCAO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448857631098929202/EVOLUCAO.jpeg", "ataque": 666, "vida": 999},
        {"nome": "BOT DJ CLEITON RASTA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448842573824135320/BOT_DJ_CLEITON_RASTA.jpeg", "ataque": 0, "vida": 0},
        {"nome": "PUNHETAÇO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448837360572825681/HORADOPUNHETAO.png", "ataque": 1000, "vida": 270},
        {"nome": "CACHORRO DESCONFIADO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448395325948825752/CACHORRO_DESCONFIADO.jpeg", "ataque": 780, "vida": 1340},
        {"nome": "VAMO PRA LUA GRU", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448390676873085109/VAMO_PRA_LUA_GRU.jpeg","ataque": 1750,"vida": 2200},
        {"nome": "ABROBA COM LEITE", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448495068653551658/ABROBA_COM_LEITE.jpeg","ataque": 1324,"vida": 900},
        {"nome": "BEBE", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450938745707823286/BEBE.jpeg","ataque": 1200,"vida": 650},
        {"nome": "FooooOOOooOoOlha", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448396099768553542/fooooOOOooOoOlha.jpeg","ataque": 350 ,"vida": 1300},
        {"nome": "CHAPADO PRATEADO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448496992887242923/CHAPADO_PRATEADO.jpeg", "ataque": 1800, "vida": 1892},
        {"nome": "ESPERMATOCHAPA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448501186855567381/ESPERMATOCHAPA.jpeg", "ataque": 100, "vida": 450},
        {"nome": "MC BRINQUEDO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448860449260175460/MC_BRINQUEDO.jpeg", "ataque": 500, "vida": 1500},
        {"nome": "DJ ANDRE MARQUES", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448861400993632427/DJ_ANDRE_MARQUES.jpeg", "ataque": 1675, "vida": 1827},
        {"nome": "CE ENTENDEU VEI?", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448866317020037352/ce_entendeu_vei_.jpeg", "ataque": 1249, "vida": 1233},
        {"nome": "DIGIMON AGIOTA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450931276763889758/DIGIMON_AGIOTA.jpeg", "ataque": 1548, "vida": 765},
        {"nome": "M M SAFADO KKKKKK", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448862042571407371/M_M_SAFADO_KKKKKK.jpeg", "ataque": 1892, "vida": 760},
        {"nome": "BEBE CHAPADO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448497494173679789/BEBE_CHAPADO_.jpeg?", "ataque": 420, "vida": 420}
    ],
    "Rara": [
        {"nome": "DOUTOR BUGIGANGA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448837175507554315/DOUTORBUGIGANGA.png", "ataque": 1000, "vida": 1500},
        {"nome": "BOLOLOHAHAHA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448861006267814081/BOLOLOHAHA.jpeg", "ataque": 2109, "vida": 1082},
        {"nome": "BERINHEAD", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448826182496682097/BERINHEAD.jpeg", "ataque": 899, "vida": 0},
        {"nome": "FODEU KKKKKKK", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448499429832130672/FODEU_KKKKK.jpeg", "ataque": 1200, "vida": 879},
        {"nome": "VEIO DA CORONA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448836977259450388/veiodacorona.png", "ataque": 500, "vida": 2100},
        {"nome": "EU QUE FIZ", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450936750238339326/EU_QUE_FIZ_1.jpeg", "ataque": 1762, "vida": 1203},
        {"nome": "GRAGUINHAS", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450934719196954685/GRAGRINHAS_.jpeg", "ataque": 1760, "vida": 1305},
        {"nome": "SMURF RABUDO ATIÇANDO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448392918514536448/SMURF_RABUDO_ATICANDO.jpeg","ataque": 1000 ,"vida": 1669},
        {"nome": "PERDOA O PAI", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448494096351232191/PERDOA_O_PAI.jpeg","ataque": 859,"vida": 1911},
        {"nome": "CARECA VIAJANTE", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450931868764737617/CARECA_VIAJANTE.jpeg","ataque": 2500,"vida": 1900},
        {"nome": "FRED MERCURY PRATEADO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448865899162636444/FRED_MERCURY_PRATEADO.jpeg","ataque": 1283,"vida": 2304},
        {"nome": "MANUAL IMUNDO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448858951683674132/MANUAL_IMUNDO.jpeg","ataque": 3255,"vida": 1},
        {"nome": "FEIJAO COM FARINHA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448496138998255798/FEIJAO_COM_FARINHA.jpeg","ataque": 90,"vida": 2005}
    ],
    "Épica": [
        {"nome": "ROGERIO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448836870959005797/ROGERIO.jpg", "ataque": 2000, "vida": 2000},
        {"nome": "CHIQUINHA CABELUDA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448827135870369832/CHIQUINHA_CABELUDA.jpeg", "ataque": 250, "vida": 3000},
        {"nome": "PUNHETAO POCANDO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448500084345016390/PUNHETAO_POCANDO.jpeg", "ataque": 2090, "vida": 602},
        {"nome": "MARIO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450935326930636860/MARIO.jpeg", "ataque": 570, "vida": 3100},
        {"nome": "PELO AMOR MAN", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450932800738955394/PELO_AMOR_MAN.jpeg", "ataque": 2100, "vida": 2300},
        {"nome": "RASTA DO ROBLOX", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450937547428593725/RASTA_DO_ROBLOX.jpeg", "ataque": 2014, "vida": 2103},
        {"nome": "FESTA DO BOLO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450937547428593725/RASTA_DO_ROBLOX.jpeg", "ataque": 3200, "vida": 2000},
        {"nome": "NOIA DO K9", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448836448001331265/noiak9.png", "ataque": 1870, "vida": 1850},
        {"nome": "DESCANSAR NE", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450938305196855306/DESCANSAR_NE.jpeg", "ataque": 1750, "vida": 2301},
        {"nome": "PASSARO FARMADOR DE AURA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1450933552639250483/PASSARO_FARMADOR_DE_AURA.jpeg", "ataque": 3100, "vida": 1290},
        {"nome": "SR. DEMERVALDO BATISTA DA SILVA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448862567089963098/sr._demervaldo_batista_da_silva.jpeg", "ataque": 1209, "vida": 2105},
        {"nome": "TECNICO EM ELETRONICA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448393964989452298/TECNICO_EM_ELETRONICA_1.jpeg", "ataque": 3.14, "vida": 2400},
        {"nome": "VOU PRO CEARA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448859508649754715/vou_pro_ceara.jpeg", "ataque": 1578, "vida": 2100},
        {"nome": "PRIME BELO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448498026921594990/PRIME_BELO.jpeg", "ataque": 2100, "vida": 1720}
    ],
    "Lendária": [
        {"nome": "NARUTO MACONHEIRO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448836302781943878/NARUTOMACONHEIRO.png", "ataque": 2100, "vida": 1800},
        {"nome": "BRUNO HENRIQUE", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448500673829277757/BRUNO_HENRIQUE.jpeg", "ataque": 3100, "vida": 2100},
        {"nome": "CR7 AURA+EGO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448835533206720727/cr7.png", "ataque": 3500, "vida": 500},
        {"nome": "REALRICH", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448858439509086389/REALRICH.jpeg", "ataque": 7777, "vida": 1},
        {"nome": "ROCK PORRAAAAA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448860061912006877/ROCK_PORRAAAAAA.jpeg", "ataque": 6666, "vida": 1000},
        {"nome": "MACONHESCO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448394810347229296/MACONHESCO.jpeg", "ataque": 1420, "vida": 3333}
    ]
}


async def atualizar_cargo_top(guild: discord.Guild, role_name: str, user_id: int):
    role = discord.utils.get(guild.roles, name=role_name)
    if not role:
        return  # cargo não existe

    # Remove o cargo de todos que têm
    for member in role.members:
        if member.id != user_id:
            try:
                await member.remove_roles(role)
            except Exception:
                pass

    # Dá o cargo ao novo TOP
    member = guild.get_member(user_id)
    if member and role not in member.roles:
        try:
            await member.add_roles(role)
        except Exception:
            pass

def sortear_carta():
    raridade = random.choices(
        population=["Comum", "Rara", "Épica", "Lendária"],
        weights=[60, 30, 9, 1],
        k=1
    )[0]

    carta = random.choice(cartas[raridade])
    return carta, raridade


async def enviar_embed_com_imagem(ctx, embed, imagem):
    if imagem.startswith("http"):
        embed.set_image(url=imagem)
        return await ctx.send(embed=embed)

    else:
        try:
            file = discord.File(imagem, filename=os.path.basename(imagem))
            embed.set_image(url=f"attachment://{os.path.basename(imagem)}")
            return await ctx.send(embed=embed, file=file)
        except Exception as e:
            embed.add_field(name="⚠ Erro", value=f"Imagem local não encontrada:\n`{imagem}`")
            return await ctx.send(embed=embed)


async def paginate_embeds(ctx, embed_items, timeout: int = 120):
    if not embed_items:
        return

    current = 0

    first_embed, first_image = embed_items[current]
    if isinstance(first_image, str) and first_image.startswith(("http://", "https://")):
        message = await ctx.send(embed=first_embed)
    else:
        message = await enviar_embed_com_imagem(ctx, first_embed, first_image)

    if len(embed_items) == 1:
        return

    LEFT = "⬅️"
    RIGHT = "➡️"
    STOP = "⏹️"

    async def add_nav_reactions(msg):
        for emoji in (LEFT, RIGHT, STOP):
            try:
                await msg.add_reaction(emoji)
            except Exception:
                pass

    await add_nav_reactions(message)

    def check(reaction, user):
        return user == ctx.author and reaction.message.id == message.id and str(reaction.emoji) in (LEFT, RIGHT, STOP)

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=timeout, check=check)
        except Exception:
            try:
                await message.delete()
            except Exception:
                pass
            break

        emoji = str(reaction.emoji)
        try:
            await message.remove_reaction(reaction.emoji, user)
        except Exception:
            pass

        if emoji == STOP:
            try:
                await message.delete()
            except Exception:
                pass
            break

        if emoji == RIGHT:
            current = (current + 1) % len(embed_items)
        elif emoji == LEFT:
            current = (current - 1) % len(embed_items)

        try:
            await message.delete()
        except Exception:
            pass

        next_embed, next_image = embed_items[current]
        if isinstance(next_image, str) and next_image.startswith(("http://", "https://")):
            message = await ctx.send(embed=next_embed)
        else:
            message = await enviar_embed_com_imagem(ctx, next_embed, next_image)

        await add_nav_reactions(message)


@bot.command()
@commands.is_owner()
async def testdrop(ctx, tentativas: int = 10000):
    from collections import Counter

    resultado = Counter()

    for _ in range(tentativas):
        _, raridade = sortear_carta()
        resultado[raridade] += 1

    linhas = []
    for r in ["Comum", "Rara", "Épica", "Lendária"]:
        qtd = resultado[r]
        linhas.append(f"{r}: {qtd} ({qtd/tentativas*100:.2f}%)")

    await ctx.send("📊 **Teste de Drop**\n" + "\n".join(linhas))


@bot.command()
async def abrirpack(ctx):
    user_id = str(ctx.author.id)
    COST = 50

    if not deduct_balance(user_id, COST):
        saldo = get_balance(user_id)
        await ctx.send(f"{ctx.author.mention} Saldo insuficiente. Você precisa de {COST} moedas. Saldo: {saldo} moedas.")
        return

    add_spent(user_id, COST)

    carta, raridade = sortear_carta()

    if not carta:
        return await ctx.send("Erro ao sortear carta.")

    imagem = carta["imagem"]

    nome_card = carta.get('nome', 'Desconhecida')
    atk_val = carta.get('ataque', '—')
    vida_val = carta.get('vida', '—')
    emoji = EMOJI_RARITY.get(raridade, '')
    embed = discord.Embed(
        title=f"{emoji} {nome_card} - {raridade}",
        description=(
            f"**Nome:** {nome_card}\n"
            f"**Ataque:** {atk_val}    **Vida:** {vida_val}"
        ),
        color=discord.Color.blue()
    )

    if card_already_exists(user_id, carta, raridade):
        add_balance(user_id, 32)
        dup_emoji = EMOJI_RARITY.get(raridade, '')
        embed_dup = discord.Embed(
            title=f"{dup_emoji} Carta Duplicada - {raridade}",
            description=(
                f"**Nome:** {nome_card}\n"
                f"{ctx.author.mention} Você já possui esta carta!\n\n**Bonus:** +32 moedas"
            ),
            color=discord.Color.gold()
        )
        await enviar_embed_com_imagem(ctx, embed_dup, imagem)
        saldo_atual = get_balance(user_id)
        await ctx.send(f"{ctx.author.mention} Saldo atual: {saldo_atual} moedas.")
        return

    add_card_to_user(user_id, carta, raridade)
    await enviar_embed_com_imagem(ctx, embed, imagem)
    saldo = get_balance(user_id)
    await ctx.send(f"Carta adicionada! Saldo atual: {saldo} moedas.")


@bot.event
async def on_ready():
    print(f"{bot.user} está online!")
    try:
        if not hasattr(bot, "join_times_marked"):
            data = _load_join_times()
            now = time.time()
            changed = False
            for guild in bot.guilds:
                gid = str(guild.id)
                if gid not in data:
                    data[gid] = {}
                for member in guild.members:
                    if member.bot:
                        continue
                    uid = str(member.id)
                    if uid not in data[gid]:
                        data[gid][uid] = now
                        changed = True
            if changed:
                _save_join_times(data)
            bot.join_times_marked = True
    except Exception:
        pass

    if not hasattr(bot, "join_awards_task"):
        bot.join_awards_task = asyncio.create_task(_process_join_awards())


@bot.event
async def on_member_join(member):
    try:
        data = _load_join_times()
        gid = str(member.guild.id)
        uid = str(member.id)
        if gid not in data:
            data[gid] = {}
        data[gid][uid] = time.time()
        _save_join_times(data)
    except Exception:
        pass


async def _process_join_awards():
    CHECK_INTERVAL = 60
    AWARD_SECONDS = 60 * 60
    while True:
        try:
            now = time.time()
            data = _load_join_times()
            changed = False
            for gid, users in list(data.items()):
                guild = bot.get_guild(int(gid))
                if guild is None:
                    del data[gid]
                    changed = True
                    continue
                for uid, ts in list(users.items()):
                    try:
                        if now - float(ts) >= AWARD_SECONDS:
                            member = guild.get_member(int(uid))
                            if member is None:
                                del data[gid][uid]
                                changed = True
                                continue

                            # Da recompensa
                            add_balance(uid, 100)

                            data[gid][uid] = now
                            changed = True
                    except Exception:
                        try:
                            del data[gid][uid]
                            changed = True
                        except Exception:
                            pass
                if gid in data and not data[gid]:
                    del data[gid]
                    changed = True
            if changed:
                _save_join_times(data)
        except Exception:
            pass
        await asyncio.sleep(CHECK_INTERVAL)



@bot.command()
async def kitdiario(ctx):
    user_id = str(ctx.author.id)
    COINS = 125
    can_claim, wait = can_claim_daily(user_id)
    if not can_claim:
        hrs = wait // 3600
        mins = (wait % 3600) // 60
        secs = wait % 60
        await ctx.send(f"{ctx.author.mention} Você já reivindicou o kit diário! Aguarde {hrs}h {mins}m {secs}s para reclamar novamente.")
        return

    add_balance(user_id, COINS)
    set_claim_time(user_id)
    saldo = get_balance(user_id)
    await ctx.send(f"{ctx.author.mention} Você recebeu {COINS} moedas do kit diário! Saldo atual: {saldo} moedas.")


@bot.command()
async def minhacolecao(ctx):
    user_id = str(ctx.author.id)
    cards = get_user_cards(user_id)

    if not cards:
        await ctx.send(f"{ctx.author.mention} Você ainda não possui cartas em sua coleção.")
        return

    # Agrupar cartas por nome + raridade
    colecao = {}

    for c in cards:
        chave = (c.get("nome"), c.get("raridade"))
        if chave not in colecao:
            colecao[chave] = {
                "quantidade": 0,
                "ataque": c.get("ataque", "—"),
                "vida": c.get("vida", "—"),
                "raridade": c.get("raridade", "Comum")
            }
        colecao[chave]["quantidade"] += 1

    ordem_raridade = ["Lendária", "Épica", "Rara", "Comum"]

    embed = discord.Embed(
        title=f"📚 Coleção de {ctx.author.display_name}",
        color=discord.Color.blurple()
    )

    for rar in ordem_raridade:
        linhas = []

        for (nome, r), dados in colecao.items():
            if r != rar:
                continue

            linhas.append(
                f"**{nome}** x{dados['quantidade']}\n"
                f"└ ⚔️ {dados['ataque']} | ❤️ {dados['vida']}"
            )

        if linhas:
            emoji = EMOJI_RARITY.get(rar, "")
            embed.add_field(
                name=f"{rar.upper()} {emoji}",
                value="\n".join(linhas),
                inline=False
            )

    embed.set_thumbnail(
        url=ctx.author.avatar.url if ctx.author.avatar else None
    )

    embed.set_footer(
        text=f"Total de cartas: {len(cards)}"
    )

    await ctx.send(embed=embed)


@bot.command()
async def meuscards(ctx):
    user_id = str(ctx.author.id)
    cards = get_user_cards(user_id)
    if not cards:
        await ctx.send(f"{ctx.author.mention} Você ainda não possui cartas em sua coleção.")
        return

    def rarity_color(r):
        return {
            "Comum": discord.Color.light_grey(),
            "Rara": discord.Color.blue(),
            "Épica": discord.Color.purple(),
            "Lendária": discord.Color.gold()
        }.get(r, discord.Color.default())

    embed_items = []
    for c in cards:
        nome = c.get("nome", "Desconhecida")
        rar = c.get("raridade", "Desconhecida")
        atk = c.get("ataque", "-")
        vida = c.get("vida", "-")
        imagem = c.get("imagem")

        emoji = EMOJI_RARITY.get(rar, '')
        embed = discord.Embed(
            title=f"{emoji} {nome} - {rar}",
            description=f"**Ataque:** {atk}\n**Vida:** {vida}",
            color=rarity_color(rar)
        )

        if isinstance(imagem, str) and imagem.startswith(("http://", "https://")):
            embed.set_image(url=imagem)
        else:
            if isinstance(imagem, str):
                embed.set_footer(text=f"Imagem local: {os.path.basename(imagem)}")

        embed_items.append((embed, imagem))

    await paginate_embeds(ctx, embed_items)


@bot.command()
async def saldo(ctx):
    user_id = str(ctx.author.id)
    saldo_atual = get_balance(user_id)
    await ctx.send(f"{ctx.author.mention}, seu saldo atual é: {saldo_atual} moedas.")

# ---------------------------------------------------------
# SISTEMA DE DUELOS
# ---------------------------------------------------------
duelos_pendentes = {}   # {desafiado_id: desafiante_id}
duelos_em_andamento = {}  # {user_id: {"oponente": id, "cartas": []}}

def calcular_total(cartas_escolhidas):
    total_atk = 0
    total_vida = 0
    for c in cartas_escolhidas:
        total_atk += int(c.get("ataque", 0))
        total_vida += int(c.get("vida", 0))
    return total_atk, total_vida, total_atk + total_vida


@bot.command()
async def duelar(ctx, oponente: discord.Member):
    if oponente.bot:
        return await ctx.send("❌ Você não pode duelar contra bots!")

    if oponente.id == ctx.author.id:
        return await ctx.send("❌ Você não pode se desafiar!")

    duelos_pendentes[oponente.id] = ctx.author.id

    embed = discord.Embed(
        title="⚔️ Novo Desafio de Duelo!",
        description=(
            f"{oponente.mention}, você foi desafiado por **{ctx.author.mention}**!\n\n"
            f"Para aceitar, use:\n👉 **!aceitar @{ctx.author.display_name}**"
        ),
        color=discord.Color.orange()
    )

    embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else None)

    await ctx.send(embed=embed)


@bot.command()
async def aceitar(ctx, desafiante: discord.Member):
    user_id = ctx.author.id

    if user_id not in duelos_pendentes:
        return await ctx.send("❌ Você não foi desafiado ou o duelo expirou.")

    if duelos_pendentes[user_id] != desafiante.id:
        return await ctx.send("❌ Este desafio não é para você.")

    del duelos_pendentes[user_id]

    # Verifica moedas
    if get_balance(str(ctx.author.id)) < 10:
        return await ctx.send(f"💸 {ctx.author.mention} não tem moedas suficientes (mínimo 10).")

    if get_balance(str(desafiante.id)) < 10:
        return await ctx.send(f"💸 {desafiante.mention} não tem moedas suficientes (mínimo 10).")

    deduct_balance(str(ctx.author.id), 10)
    deduct_balance(str(desafiante.id), 10)

    add_spent(str(ctx.author.id), 10)
    add_spent(str(desafiante.id), 10)

    cartas_desafiante = get_user_cards(str(desafiante.id))
    cartas_desafiado = get_user_cards(str(ctx.author.id))


    if len(cartas_desafiante) == 0:
        return await ctx.send(f"{desafiante.mention} não possui cartas!")
    if len(cartas_desafiado) == 0:
        return await ctx.send(f"{ctx.author.mention} não possui cartas!")

    escolhidas_desafiante = escolher_5_aleatorias(cartas_desafiante)
    escolhidas_desafiado = escolher_5_aleatorias(cartas_desafiado)

    atk_a, vida_a, total_a = calcular_total(escolhidas_desafiante)
    atk_b, vida_b, total_b = calcular_total(escolhidas_desafiado)

    # Determina vencedor
    if total_a > total_b:
        vencedor = desafiante.id
        perdedor = ctx.author.id
    elif total_b > total_a:
        vencedor = ctx.author.id
        perdedor = desafiante.id
    else:
        vencedor = None

    # Empate
    if vencedor is None:
        embed = discord.Embed(
            title="⚔️ Duelo Finalizado!",
            description="O duelo terminou em **EMPATE**! Nenhum jogador ganhou moedas.",
            color=discord.Color.greyple()
        )
        return await ctx.send(embed=embed)

    # Premiação
    add_balance(str(vencedor), 20)
    add_win(str(vencedor))

    jogadorA = desafiante
    jogadorB = ctx.author

    def formatar_cartas(lista):
        return "\n".join([f"• {c.get('nome')} ({c.get('ataque','?')} ATK / {c.get('vida','?')} VIDA)" for c in lista])

    embed = discord.Embed(
        title="🏆 Resultado do Duelo",
        color=discord.Color.gold()
    )

    embed.add_field(
        name=f"🟥 {jogadorA.display_name} — **{total_a} pontos**",
        value=formatar_cartas(escolhidas_desafiante),
        inline=False
    )

    embed.add_field(
        name=f"🟦 {jogadorB.display_name} — **{total_b} pontos**",
        value=formatar_cartas(escolhidas_desafiado),
        inline=False
    )

    embed.add_field(
        name="🥇 **Vencedor**",
        value=f"{bot.get_user(vencedor).mention} ganhou **20 moedas!** 💰",
        inline=False
    )

    embed.set_thumbnail(url=bot.get_user(vencedor).avatar.url if bot.get_user(vencedor).avatar else None)

    await ctx.send(embed=embed)


@bot.command()
async def vitorias(ctx):
    wins = get_wins(str(ctx.author.id))
    await ctx.send(f"{ctx.author.mention}, você possui **{wins} vitórias** em duelos!")

@bot.command()
async def ranking(ctx):
    wins_data = _load_json(WINS_FILE)
    spent_data = _load_json(SPENT_FILE)

    if not wins_data and not spent_data:
        await ctx.send("Nenhum dado de ranking disponível ainda.")
        return

    # Ordenações
    ranking_wins = sorted(wins_data.items(), key=lambda x: x[1], reverse=True)[:10]
    ranking_spent = sorted(spent_data.items(), key=lambda x: x[1], reverse=True)[:10]

    medalhas = {1: "🥇", 2: "🥈", 3: "🥉"}

    def formatar_linhas(lista, sufixo):
        linhas = []
        for pos, (user_id, valor) in enumerate(lista, start=1):
            user = bot.get_user(int(user_id))
            nome = user.display_name if user else f"Usuário {user_id}"
            medalha = medalhas.get(pos, f"`#{pos}`")
            linhas.append(f"{medalha} **{nome}** — {valor} {sufixo}")
        return linhas

    embed = discord.Embed(
        title="🏆 Ranking Geral",
        color=discord.Color.gold()
    )

    if ranking_wins:
        embed.add_field(
            name="⚔️ Vitórias em Duelos",
            value="\n".join(formatar_linhas(ranking_wins, "vitória(s)")),
            inline=False
        )

    if ranking_spent:
        embed.add_field(
            name="💸 Moedas Gastas",
            value="\n".join(formatar_linhas(ranking_spent, "moedas")),
            inline=False
        )

    # Thumbnail do maior vencedor
    if ranking_wins:
        top_user = bot.get_user(int(ranking_wins[0][0]))
        if top_user and top_user.avatar:
            embed.set_thumbnail(url=top_user.avatar.url)

    embed.set_footer(text="Top 10 • Histórico total do servidor")
    # Atualiza cargos automáticos
    guild = ctx.guild
    
    if ranking_wins:
        await atualizar_cargo_top(
            guild,
            ROLE_TOP_WINS,
            int(ranking_wins[0][0])
        )
    
    if ranking_spent:
        await atualizar_cargo_top(
            guild,
            ROLE_TOP_SPENT,
            int(ranking_spent[0][0])
        )
        
    await ctx.send(embed=embed)


CUSTO_FUSAO = 10
RECOMPENSA_DUPLICATA = 50
RARIDADES_ORDENADAS = ["Comum", "Rara", "Épica", "Lendária"]

probabilidades_fusao = {
    ("Comum", "Comum"): 0.45,
    ("Rara", "Rara"): 0.35,
    ("Épica", "Épica"): 0.15,
}

def obter_raridade_superior(raridade: str) -> Optional[str]:
    if raridade not in RARIDADES_ORDENADAS:
        return None
    idx = RARIDADES_ORDENADAS.index(raridade)
    if idx + 1 < len(RARIDADES_ORDENADAS):
        return RARIDADES_ORDENADAS[idx + 1]
    return None

def escolher_cartas_raridade(cartas_usuario, raridade):
    filtradas = [c for c in cartas_usuario if c.get("raridade") == raridade]
    if len(filtradas) < 2:
        return None
    return random.sample(filtradas, 2)

def possui_carta(inventario, carta):
    return any(
        c["nome"] == carta["nome"] and c["raridade"] == carta["raridade"]
        for c in inventario
    )


# ================================================
#              FUNÇÃO DE FUSÃO
# ================================================
def fusao(user_id: str, raridade: str):
    raridade = raridade.capitalize()

    if raridade not in ["Comum", "Rara", "Épica"]:
        return {"erro": True, "msg": "❌ Raridade inválida. Use: Comum, Rara ou Épica."}

    # carregar dados
    saldos = _load_json(BALANCES_FILE)
    inventarios = _load_json(CARDS_FILE)

    saldo = saldos.get(user_id, 0)
    cartas_usuario = inventarios.get(user_id, [])

    if saldo < CUSTO_FUSAO:
        return {"erro": True, "msg": f"❌ Você precisa de {CUSTO_FUSAO} moedas para fundir."}

    escolhidas = escolher_cartas_raridade(cartas_usuario, raridade)

    if not escolhidas:
        return {"erro": True, "msg": f"❌ Você precisa de **2 cartas {raridade}** para fundir."}

    carta1, carta2 = escolhidas

    saldo -= CUSTO_FUSAO
    add_spent(user_id, CUSTO_FUSAO)

    prob = probabilidades_fusao.get((raridade, raridade), 0)
    sucesso = random.random() < prob

    if not sucesso:
        # destrói cartas
        cartas_usuario.remove(carta1)
        cartas_usuario.remove(carta2)

        inventarios[user_id] = cartas_usuario
        saldos[user_id] = saldo
        _save_json(CARDS_FILE, inventarios)
        _save_json(BALANCES_FILE, saldos)

        return {
            "erro": False,
            "sucesso": False,
            "msg": "💥 **FUSÃO FALHOU!** As cartas foram destruídas."
        }

    # SUCESSO
    nova_raridade = obter_raridade_superior(raridade)
    carta_base = random.choice(cartas[nova_raridade])
    nova_carta = dict(carta_base)
    nova_carta["raridade"] = nova_raridade

    # duplicata
    duplicata = False
    if possui_carta(cartas_usuario, nova_carta):
        duplicata = True
        saldo += RECOMPENSA_DUPLICATA
    else:
        cartas_usuario.remove(carta1)
        cartas_usuario.remove(carta2)
        cartas_usuario.append(nova_carta)

    inventarios[user_id] = cartas_usuario
    saldos[user_id] = saldo

    _save_json(CARDS_FILE, inventarios)
    _save_json(BALANCES_FILE, saldos)

    return {
        "erro": False,
        "sucesso": True,
        "carta": nova_carta,
        "duplicata": duplicata,
        "saldo": saldo
    }
    

@bot.command(name="fusao")
async def fusao_cmd(ctx, raridade: str = None):
    if raridade is None:
        await ctx.send("Use: `!fusao comum`, `!fusao rara`, `!fusao épica`")
        return

    user_id = str(ctx.author.id)
    resultado = fusao(user_id, raridade)

    if "erro" in resultado and resultado["erro"]:
        await ctx.send(resultado["msg"])
        return

    # Se falhou
    if not resultado.get("sucesso"):
        await ctx.send(resultado["msg"])
        return

    carta = resultado["carta"]

    embed = discord.Embed(
        title=f"✨ FUSÃO BEM-SUCEDIDA!",
        description=f"Você recebeu **{carta['nome']}**!\nRaridade: **{carta['raridade']}**",
        color=discord.Color.purple()
    )

    embed.set_thumbnail(url=carta["imagem"])

    atk = carta.get("ataque", "❓")
    vida = carta.get("vida", "❓")

    embed.add_field(name="Ataque", value=str(atk))
    embed.add_field(name="Vida", value=str(vida))

    if resultado["duplicata"]:
        embed.add_field(
            name="Duplicata",
            value=f"Você já tinha essa carta! Recebeu **+{RECOMPENSA_DUPLICATA} moedas!**",
            inline=False
        )

    await ctx.send(embed=embed)

if __name__ == "__main__":
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("ERRO: Token do Discord não encontrado. Configure a variável DISCORD_BOT_TOKEN.")
    else:
        bot.run(token)
