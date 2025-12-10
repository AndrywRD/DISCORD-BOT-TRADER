import random
import os
import json
import time
import asyncio
from pathlib import Path
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_DIR = Path(__file__).parent
BALANCES_FILE = DATA_DIR / "balances.json"
LAST_CLAIM_FILE = DATA_DIR / "last_claims.json"
CARDS_FILE = DATA_DIR / "cards.json"
JOIN_TIMES_FILE = DATA_DIR / "join_times.json"


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
    

raridades = {
    "Comum": 0.6,
    "Rara": 0.3,
    "Épica": 0.95,
    "Lendária": 0.03
}

EMOJI_RARITY = {
    "Comum": "⚪",
    "Rara": "🔵",
    "Épica": "🟣",
    "Lendária": "🌟"
}

cartas = {
    "Comum": [
        {"nome": "andryw", "imagem": "imagens/ANDRYW_RUHAN.jpeg", "ataque": 500, "vida": -500},
        {"nome": "É MAFIA FAMILIA", "imagem": "imagens/MAFIA.PNG", "ataque": 500, "vida": 1000},
        {"nome": "EVOLUCAO", "imagem": "imagens/EVOLUCAO.PNG", "ataque": 666, "vida": 999},
        {"nome": "BOT DJ CLEITON RASTA", "imagem": "imagens/CLEITONRASTA.png", "ataque": 0, "vida": 0},
        {"nome": "PUNHETAÇO", "imagem": "imagens/HORADOPUNHETAO.png"},
        {"nome": "CACHORRO DESCONFIADO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448395325948825752/CACHORRO_DESCONFIADO.jpeg?ex=693b1ac3&is=6939c943&hm=33132e639440c34df4067123dc016aed3efcec9934ab05dc44887d1d16d3da4c&"},
        {"nome": "VAMO PRA LUA GRU", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448390676873085109/VAMO_PRA_LUA_GRU.jpeg?ex=693b166f&is=6939c4ef&hm=46729310369cd3e1b268dd2c312037f8723ddf7bd2c174f275eb68fd8a94ef7d&","ataque": 1750 ,"vida": 2200},
        {"nome": "FooooOOOooOoOlha", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448396099768553542/fooooOOOooOoOlha.jpeg?ex=693b1b7c&is=6939c9fc&hm=509c9595b61a329e8d85d56dba9829af94919dd09dd08fd70dde335ff76fb7a6&","ataque": 350 ,"vida": 1300}
    ],
    "Rara": [
        {"nome": "DOUTOR BUGIGANGA", "imagem": "imagens/DOUTORBUGIGANGA.png", "ataque": 1000, "vida": 1500},
        {"nome": "BERINHEAD", "imagem": "imagens/cabecao.jpg", "ataque": 899, "vida": 0},
        {"nome": "VEIO DA CORONA", "imagem": "imagens/veiodacorona.png", "ataque": 500, "vida": 2100},
        {"nome": "SMURF RABUDO ATIÇANDO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448392918514536448/SMURF_RABUDO_ATICANDO.jpeg?ex=693b1885&is=6939c705&hm=28717eada1f7f14ba02c7c5648a1b7ff86c9de76539bf355806a67f29e1ad45e&","ataque": 1000 ,"vida": 1669}
    ],
    "Épica": [
        {"nome": "ROGERIO", "imagem": "imagens/ROGERIO.jpg", "ataque": 2000, "vida": 2000},
        {"nome": "CHIQUINHA CABELUDA", "imagem": "imagens/chiquinha.png", "ataque": 250, "vida": 4000},
        {"nome": "NOIA DO K9", "imagem": "imagens/noiak9.png"},
        {"nome": "TECNICO EM ELETRONICA", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448393964989452298/TECNICO_EM_ELETRONICA_1.jpeg?ex=693b197f&is=6939c7ff&hm=e8d2f2ca612a9ab31fe531680db7f81fd0ceefd8032611f42de8bb3880d5c9e0&", "ataque": 3.14, "vida": 2200}
    ],
    "Lendária": [
        {"nome": "NARUTO MACONHEIRO", "imagem": "imagens/NARUTOMACONHEIRO.png", "ataque": 2100, "vida": 1800},
        {"nome": "CR7 AURA+EGO", "imagem": "imagens/cr7.png", "ataque": 3500, "vida": 0},
        {"nome": "MACONHESCO", "imagem": "https://cdn.discordapp.com/attachments/1448120749738037341/1448394810347229296/MACONHESCO.jpeg?ex=693b1a48&is=6939c8c8&hm=5de3e6f91a975e8c434b53c333048d8ab937af028092030d56788af595ee88d4&", "ataque": 1420, "vida": 3333}
    ]
}


def sortear_carta():
    sorteio = random.random()
    probabilidade_acumulada = 0
    for raridade, probabilidade in raridades.items():
        probabilidade_acumulada += probabilidade
        if sorteio <= probabilidade_acumulada:
            carta = random.choice(cartas[raridade])
            return carta, raridade
    return None, None


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
async def abrirpack(ctx):
    user_id = str(ctx.author.id)
    COST = 50

    if not deduct_balance(user_id, COST):
        saldo = get_balance(user_id)
        await ctx.send(f"{ctx.author.mention} Saldo insuficiente. Você precisa de {COST} moedas. Saldo: {saldo} moedas.")
        return

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
    AWARD_SECONDS = 60 * 30
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
                            add_balance(uid, 100)
                            try:
                                await member.send("Parabéns — você recebeu 100 moedas por ficar 30 minutos no servidor!")
                            except Exception:
                                pass
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

    counts = {}
    for c in cards:
        nome = c.get("nome", "Desconhecida")
        counts[nome] = counts.get(nome, 0) + 1

    lines = [f"{nome} x{qt}" for nome, qt in counts.items()]
    chunk_size = 30
    for i in range(0, len(lines), chunk_size):
        chunk = lines[i:i+chunk_size]
        await ctx.send(f"{ctx.author.mention} Sua coleção:\n" + "\n".join(chunk))


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


if __name__ == "__main__":
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        print("ERRO: Token do Discord não encontrado. Configure a variável DISCORD_BOT_TOKEN.")
    else:
        bot.run(token)
