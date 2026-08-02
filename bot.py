import discord
from discord.ext import commands
import os

# ============================================================
# CONFIGURACIÓN DEL BOT
# ============================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)


# ============================================================
# EXP POR ASCENSIÓN
# ============================================================

aufstieg_boosters = {
    1: 3985,
    2: 7970,
    3: 11955,
    4: 19128,
    5: 95639,
    6: 159398
}


# ============================================================
# COMANDO DUNGEON
# ============================================================
#
# USO:
#
# !dungeon 50 4 5
#
# Dungeon = 50%
# Desde Ascension 4 hasta Ascension 5
#
# También:
#
# !dungeon 130 4 5
#
# Dungeon = 130%
# Desde Ascension 4 hasta Ascension 5
#
# ============================================================

@bot.command(name="dungeon")
async def dungeon(ctx, dungeon_percent: float, start_level: int, end_level: int):

    # Comprobar que el nivel inicial sea menor
    if start_level >= end_level:
        await ctx.send(
            "❌ El nivel inicial debe ser menor que el nivel final.\n"
            "Ejemplo: `!dungeon 130 4 5`"
        )
        return

    # Comprobar que existan los niveles
    missing_levels = []

    for lvl in range(start_level, end_level):
        if lvl not in aufstieg_boosters:
            missing_levels.append(lvl)

    if missing_levels:
        await ctx.send(
            f"❌ No tengo datos de EXP para Ascension: "
            f"{', '.join(map(str, missing_levels))}"
        )
        return

    # ========================================================
    # CALCULAR EXP TOTAL
    # ========================================================

    total_exp = sum(
        aufstieg_boosters[lvl]
        for lvl in range(start_level, end_level)
    )

    # ========================================================
    # APLICAR DUNGEON
    # ========================================================

    dungeon_multiplier = 1 + (dungeon_percent / 100)

    total_exp_with_dungeon = total_exp * dungeon_multiplier

    # ========================================================
    # CALCULAR BOOSTERS
    # ========================================================

    # Cada booster representa 500% base × 4
    exp_per_booster = 5 * 4

    boosters_needed = (
        total_exp_with_dungeon / exp_per_booster
    )

    # ========================================================
    # RESPUESTA
    # ========================================================

    await ctx.send(
        f"🏰 **Cálculo de Dungeon**\n\n"
        f"📊 Dungeon: **{dungeon_percent:.0f}%**\n"
        f"📈 Ascension: **{start_level} → {end_level}**\n\n"
        f"💠 EXP base necesaria: **{total_exp:,.0f}**\n"
        f"🔥 EXP con Dungeon: **{total_exp_with_dungeon:,.0f}**\n\n"
        f"🚀 Boosters necesarios: **{boosters_needed:,.2f}**"
    )


# ============================================================
# BLOQUEAR COMANDO BOOSTER
# ============================================================
#
# Si alguien intenta usar !booster, el bot responderá
# indicando que el comando correcto es !dungeon.
#
# ============================================================

@bot.command(name="booster")
async def booster_removed(ctx, *args):

    await ctx.send(
        "❌ El comando `!booster` ya no está disponible.\n\n"
        "Usa:\n"
        "`!dungeon <dungeon%> <ascension_inicio> <ascension_final>`\n\n"
        "Ejemplo:\n"
        "`!dungeon 130 4 5`"
    )


# ============================================================
# COMANDO HELP
# ============================================================

@bot.command(name="help")
async def custom_help(ctx):

    await ctx.send(
        "📖 **LastChaos EXP Calculator**\n\n"
        "**Único comando de cálculo:**\n\n"
        "`!dungeon <dungeon%> <ascension_inicio> <ascension_final>`\n\n"
        "**Ejemplo:**\n"
        "`!dungeon 130 4 5`\n\n"
        "Esto calcula los Boosters necesarios desde Ascension "
        "4 hasta Ascension 5 con Dungeon 130%."
    )


# ============================================================
# ON READY
# ============================================================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"BOT CONECTADO: {bot.user}")
    print("=" * 50)

    print("Comandos disponibles:")
    print("!dungeon")
    print("!help")
    print("!booster -> redirige a !dungeon")


# ============================================================
# EJECUTAR BOT
# ============================================================

TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:
    print("ERROR: No se encontró DISCORD_TOKEN")
else:
    bot.run(TOKEN)
