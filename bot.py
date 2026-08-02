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
# CONFIGURACIÓN GENERAL
# ============================================================

# Cantidad de mobs que mata por hora por defecto
DEFAULT_MOBS_PER_HOUR = 2100

# Sin boosters se necesitan 4 veces los mobs
# equivalentes al cálculo de boosters
MOBS_MULTIPLIER = 4


# ============================================================
# BOOSTERS NECESARIOS CON DUNGEON 50%
# ============================================================
#
# Dungeon 50%:
#
# Ascension 1 → 2 = 3.985
# Ascension 2 → 3 = 7.970
# Ascension 3 → 4 = 11.955
# Ascension 4 → 5 = 19.128
# Ascension 5 → 6 = 95.639
# Ascension 6 → 7 = 159.398
#
# ============================================================

boosters_50 = {
    1: 3985,
    2: 7970,
    3: 11955,
    4: 19128,
    5: 95639,
    6: 159398
}


# ============================================================
# CALCULAR BOOSTERS SEGÚN DUNGEON
# ============================================================

def calculate_boosters(base_boosters, dungeon_percent):

    # Los valores base corresponden a Dungeon 50%
    base_dungeon_multiplier = 1 + (50 / 100)

    # Multiplicador del nuevo Dungeon
    new_dungeon_multiplier = 1 + (dungeon_percent / 100)

    # Fórmula
    result = (
        base_boosters
        * base_dungeon_multiplier
        / new_dungeon_multiplier
    )

    return result


# ============================================================
# FORMATEAR TIEMPO
# ============================================================

def format_hours(hours):

    total_minutes = round(hours * 60)

    days = total_minutes // (24 * 60)

    remaining_minutes = total_minutes % (24 * 60)

    final_hours = remaining_minutes // 60

    minutes = remaining_minutes % 60

    if days > 0:

        return (
            f"{days} días, "
            f"{final_hours} horas y "
            f"{minutes} minutos"
        )

    elif final_hours > 0:

        return (
            f"{final_hours} horas y "
            f"{minutes} minutos"
        )

    else:

        return f"{minutes} minutos"


# ============================================================
# COMANDO DUNGEON
# ============================================================
#
# !dungeon 130
#
# Muestra todas las ascensiones.
#
# !dungeon 130 5
#
# Muestra 5 → 6.
#
# !dungeon 130 5 6
#
# Muestra 5 → 6.
#
# ============================================================

@bot.command(name="dungeon")
async def dungeon(
    ctx,
    dungeon_percent: float,
    start_level: int = None,
    end_level: int = None
):

    # ========================================================
    # VALIDAR DUNGEON
    # ========================================================

    if dungeon_percent < 0:

        await ctx.send(
            "❌ El porcentaje de Dungeon no puede ser negativo."
        )

        return


    # ========================================================
    # MOSTRAR TODAS LAS ASCENSIONES
    # ========================================================

    if start_level is None:

        response = (
            f"🏰 **Cálculo de Dungeon {dungeon_percent:.0f}%**\n\n"
            f"📌 Valores calculados tomando como referencia "
            f"**Dungeon 50%**.\n\n"
        )

        for level, base_value in boosters_50.items():

            result = calculate_boosters(
                base_value,
                dungeon_percent
            )

            response += (
                f"🔹 Ascension **{level} → {level + 1}**\n"
                f"📦 Dungeon 50%: **{base_value:,} Boosters**\n"
                f"🔥 Dungeon {dungeon_percent:.0f}%: "
                f"**{result:,.2f} Boosters**\n\n"
            )

        await ctx.send(response)

        return


    # ========================================================
    # SI SOLO SE INDICA START_LEVEL
    # ========================================================

    if end_level is None:

        end_level = start_level + 1


    # ========================================================
    # VALIDAR RANGO
    # ========================================================

    if start_level >= end_level:

        await ctx.send(
            "❌ El nivel inicial debe ser menor que el nivel final.\n\n"
            "Ejemplo:\n"
            "`!dungeon 130 5 6`"
        )

        return


    # ========================================================
    # VALIDAR NIVELES
    # ========================================================

    missing_levels = []

    for level in range(start_level, end_level):

        if level not in boosters_50:

            missing_levels.append(level)


    if missing_levels:

        await ctx.send(
            "❌ No tengo datos para las siguientes ascensiones: "
            + ", ".join(
                f"{x} → {x + 1}"
                for x in missing_levels
            )
        )

        return


    # ========================================================
    # CALCULAR
    # ========================================================

    response = (
        f"🏰 **Cálculo de Dungeon {dungeon_percent:.0f}%**\n\n"
    )

    total_base = 0

    for level in range(start_level, end_level):

        base_value = boosters_50[level]

        result = calculate_boosters(
            base_value,
            dungeon_percent
        )

        total_base += base_value

        response += (
            f"🔹 Ascension **{level} → {level + 1}**\n"
            f"📦 Dungeon 50%: **{base_value:,} Boosters**\n"
            f"🔥 Dungeon {dungeon_percent:.0f}%: "
            f"**{result:,.2f} Boosters**\n\n"
        )


    # ========================================================
    # TOTAL
    # ========================================================

    if end_level - start_level > 1:

        total_calculated = calculate_boosters(
            total_base,
            dungeon_percent
        )

        response += (
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"📊 **TOTAL**\n"
            f"📦 Dungeon 50%: **{total_base:,} Boosters**\n"
            f"🔥 Dungeon {dungeon_percent:.0f}%: "
            f"**{total_calculated:,.2f} Boosters**"
        )


    await ctx.send(response)


# ============================================================
# COMANDO MOOOBS
# ============================================================
#
# Calcula cuántos mobs necesita matar SIN BOOSTERS.
#
# USO:
#
# !moobs 50 4 5
#
# Dungeon 50%
# Ascension 4 → 5
# 2100 mobs por hora
#
# ------------------------------------------------------------
#
# !moobs 50 5 6 1900
#
# Dungeon 50%
# Ascension 5 → 6
# 1900 mobs por hora
#
# ============================================================

@bot.command(name="moobs")
async def moobs(
    ctx,
    dungeon_percent: float,
    start_level: int,
    end_level: int,
    mobs_per_hour: int = DEFAULT_MOBS_PER_HOUR
):

    # ========================================================
    # VALIDACIONES
    # ========================================================

    if dungeon_percent < 0:

        await ctx.send(
            "❌ El porcentaje de Dungeon no puede ser negativo."
        )

        return


    if start_level >= end_level:

        await ctx.send(
            "❌ El nivel inicial debe ser menor que el nivel final.\n\n"
            "Ejemplo:\n"
            "`!moobs 50 4 5`"
        )

        return


    if mobs_per_hour <= 0:

        await ctx.send(
            "❌ Los mobs por hora deben ser mayores que 0."
        )

        return


    # ========================================================
    # VALIDAR ASCENSIONES
    # ========================================================

    missing_levels = []

    for level in range(start_level, end_level):

        if level not in boosters_50:

            missing_levels.append(level)


    if missing_levels:

        await ctx.send(
            "❌ No tengo datos para las siguientes ascensiones: "
            + ", ".join(
                f"{x} → {x + 1}"
                for x in missing_levels
            )
        )

        return


    # ========================================================
    # CALCULAR
    # ========================================================

    total_boosters = calculate_boosters(
        sum(
            boosters_50[level]
            for level in range(start_level, end_level)
        ),
        dungeon_percent
    )


    # Sin boosters se necesitan 4 veces los mobs
    total_mobs = total_boosters * MOBS_MULTIPLIER


    # Horas necesarias
    total_hours = total_mobs / mobs_per_hour


    # ========================================================
    # RESPUESTA
    # ========================================================

    response = (
        f"🐉 **Cálculo de Mobs — Dungeon {dungeon_percent:.0f}%**\n\n"
        f"🔹 Ascension: **{start_level} → {end_level}**\n"
        f"⚔️ Mobs necesarios: **{total_mobs:,.0f}**\n"
        f"📈 Mobs por hora: **{mobs_per_hour:,}**\n"
        f"⏱️ Horas necesarias: **{total_hours:,.2f} horas**\n"
        f"🕐 Tiempo aproximado: **{format_hours(total_hours)}**\n\n"
        f"📌 Cálculo basado en que sin boosters "
        f"se necesitan **4×** los mobs equivalentes al cálculo de boosters."
    )


    await ctx.send(response)


# ============================================================
# COMANDO BOOSTER
# ============================================================
#
# Calcula boosters + tiempo estimado.
#
# !booster 130 5 6
#
# Usa 2100 mobs por hora.
#
# ------------------------------------------------------------
#
# !booster 130 5 6 1900
#
# Usa 1900 mobs por hora.
#
# ============================================================

@bot.command(name="booster")
async def booster(
    ctx,
    dungeon_percent: float,
    start_level: int,
    end_level: int,
    mobs_per_hour: int = DEFAULT_MOBS_PER_HOUR
):

    # ========================================================
    # VALIDACIONES
    # ========================================================

    if dungeon_percent < 0:

        await ctx.send(
            "❌ El porcentaje de Dungeon no puede ser negativo."
        )

        return


    if start_level >= end_level:

        await ctx.send(
            "❌ El nivel inicial debe ser menor que el nivel final.\n\n"
            "Ejemplo:\n"
            "`!booster 130 5 6`"
        )

        return


    if mobs_per_hour <= 0:

        await ctx.send(
            "❌ Los mobs por hora deben ser mayores que 0."
        )

        return


    # ========================================================
    # VALIDAR ASCENSIONES
    # ========================================================

    missing_levels = []

    for level in range(start_level, end_level):

        if level not in boosters_50:

            missing_levels.append(level)


    if missing_levels:

        await ctx.send(
            "❌ No tengo datos para las siguientes ascensiones: "
            + ", ".join(
                f"{x} → {x + 1}"
                for x in missing_levels
            )
        )

        return


    # ========================================================
    # CALCULAR BOOSTERS
    # ========================================================

    total_base = sum(
        boosters_50[level]
        for level in range(start_level, end_level)
    )


    total_boosters = calculate_boosters(
        total_base,
        dungeon_percent
    )


    # ========================================================
    # CALCULAR HORAS
    # ========================================================

    total_hours = total_boosters / mobs_per_hour


    # ========================================================
    # RESPUESTA
    # ========================================================

    response = (
        f"⚡ **Cálculo de Boosters — Dungeon {dungeon_percent:.0f}%**\n\n"
        f"🔹 Ascension: **{start_level} → {end_level}**\n"
        f"📦 Boosters necesarios: **{total_boosters:,.2f}**\n"
        f"📈 Mobs por hora: **{mobs_per_hour:,}**\n"
        f"⏱️ Horas necesarias: **{total_hours:,.2f} horas**\n"
        f"🕐 Tiempo aproximado: **{format_hours(total_hours)}**"
    )


    await ctx.send(response)


# ============================================================
# HELP
# ============================================================

@bot.command(name="help")
async def custom_help(ctx):

    await ctx.send(
        "📖 **LastChaos EXP Calculator**\n\n"

        "🏰 **Calcular Dungeon:**\n"
        "`!dungeon 130`\n"
        "`!dungeon 130 5 6`\n\n"

        "🐉 **Calcular mobs sin boosters:**\n"
        "`!moobs 50 4 5`\n\n"

        "🐉 **Mobs con velocidad personalizada:**\n"
        "`!moobs 50 5 6 1900`\n\n"

        "⚡ **Calcular boosters + horas:**\n"
        "`!booster 130 5 6`\n\n"

        "⚡ **Boosters + horas con velocidad personalizada:**\n"
        "`!booster 130 5 6 1900`\n\n"

        "💡 Mobs por hora por defecto: **2.100**"
    )


# ============================================================
# ON READY
# ============================================================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"BOT CONECTADO: {bot.user}")
    print("=" * 50)
    print("Sistema de cálculo Dungeon activo.")
    print("Ejemplo: !dungeon 130 5 6")
    print("Ejemplo: !moobs 50 4 5")
    print("Ejemplo: !booster 130 5 6")


# ============================================================
# INICIAR BOT
# ============================================================

TOKEN = os.environ.get("DISCORD_TOKEN")

if not TOKEN:

    print("❌ ERROR: No se encontró DISCORD_TOKEN")

else:

    bot.run(TOKEN)
