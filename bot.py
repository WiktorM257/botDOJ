import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import requests
import os
from datetime import datetime

# =============================
# KONFIGURACJA
# =============================
TOKEN = os.getenv("TOKEN")
API_ADD = "https://doj-backend-ac2o.onrender.com/api/add_schedule"
API_GET = "https://doj-backend-ac2o.onrender.com/schedule.json"
API_DELETE = "https://doj-backend-ac2o.onrender.com/api/delete_schedule"
API_ARCHIVE = "https://doj-backend-ac2o.onrender.com/api/archive_case"

intents = nextcord.Intents.default()
bot = commands.Bot(intents=intents)


# =============================
# BOT START
# =============================
@bot.event
async def on_ready():
    print(f"DOJ BOT online jako {bot.user}")
    try:
        await bot.sync_all_application_commands()
        print("Slash commands zsynchronizowane.")
    except Exception as e:
        print("Błąd sync:", e)


# =============================
#  /rozprawa — dodawanie
# =============================
@bot.slash_command(
    name="rozprawa",
    description="Dodaj rozprawę do wokandy DOJ."
)
async def rozprawa(
    inter: Interaction,
    sedzia: str,
    prokurator: str,
    sala: str,
    oskarzony: str,
    adwokat: str,
    data: str,         # format: 28.11.2025
    godzina: str,      # format: 14:30
    strony: str,
    swiadkowie: str = "",
    opis: str = ""
):

    await inter.response.send_message("⏳ Dodawanie rozprawy...", ephemeral=True)

    # 🔥 Konwersja daty na format SQL YYYY-MM-DD
    try:
        sql_date = datetime.strptime(data, "%d.%m.%Y").strftime("%Y-%m-%d")
    except:
        return await inter.edit_original_message("❌ Błędny format daty! Użyj DD.MM.YYYY")

    payload = {
        "name": f"{oskarzony} - {adwokat}",
        "judge": sedzia,
        "prosecutor": prokurator,
        "defendant": oskarzony,
        "lawyer": adwokat,
        "witnesses": swiadkowie,
        "room": sala,
        "date": sql_date,
        "time": godzina,
        "parties": strony,
        "description": opis
    }

    try:
        r = requests.post(API_ADD, json=payload)

        if r.status_code == 200:
            await inter.edit_original_message(
                f"✔ **Dodano rozprawę**\n"
                f"**{strony}**\n"
                f"Sala: **{sala}**, godzina: **{godzina}**\n"
                f"Sędzia: **{sedzia}**\n"
                f"Świadkowie: **{swiadkowie or 'brak'}**"
            )
        else:
            await inter.edit_original_message(f"❌ Błąd API: {r.status_code}")

    except Exception as e:
        await inter.edit_original_message(f"❌ Błąd połączenia z API: {e}")


# =============================
#  /usun_rozprawe — usuwanie
# =============================
@bot.slash_command(
    name="usun_rozprawe",
    description="Usuń rozprawę z wokandy po ID."
)
async def usun_rozprawe(
    inter: Interaction,
    id_rozprawy: str = SlashOption(description="ID rozprawy (np. SA-2025-0001)")
):
    await inter.response.send_message("⏳ Szukam rozprawy...", ephemeral=True)

    # Pobierz listę z SQL
    try:
        data = requests.get(API_GET).json()
    except:
        return await inter.edit_original_message("❌ Błąd pobierania danych API.")

    # 🔥 Poprawne porównanie ID jako string
    znalezione = next((t for t in data if t["id"] == id_rozprawy), None)

    if not znalezione:
        return await inter.edit_original_message(f"❌ Nie znaleziono rozprawy o ID **{id_rozprawy}**.")

    # Usuń
    try:
        r = requests.post(API_DELETE, json={"id": id_rozprawy})
    except Exception as e:
        return await inter.edit_original_message(f"❌ Błąd API: {e}")

    if r.status_code == 200:
        await inter.edit_original_message(f"✔ Usunięto rozprawę o ID **{id_rozprawy}**.")
    else:
        await inter.edit_original_message(f"❌ Błąd API: {r.status_code}")


# =============================
#  /archiwizuj — archiwizacja
# =============================
@bot.slash_command(
    name="archiwizuj",
    description="Przenosi sprawę do archiwum z wynikiem i wyrokiem."
)
async def archiwizuj(
    inter,
    id: str,
    wynik: str = nextcord.SlashOption(
        name="wynik",
        description="Wynik rozprawy",
        choices=["winny", "niewinny", "ugoda"]
    ),
    wyrok: str = nextcord.SlashOption(name="wyrok", description="Treść wyroku"),
    dokument: str = nextcord.SlashOption(name="dokument", description="Link do PDF")
):
    await inter.response.defer()

    payload = {
        "id": id,
        "result": wynik,
        "verdict": wyrok,
        "document": dokument
    }

    r = requests.post(API_ARCHIVE, json=payload)

    if r.status_code == 200:
        await inter.followup.send(f"📁 Sprawa **{id}** została zarchiwizowana.")
    elif r.status_code == 404:
        await inter.followup.send(f"❌ Nie znaleziono sprawy o ID **{id}**.")
    else:
        await inter.followup.send("❌ Błąd API podczas archiwizacji.")


# =============================
# START BOT
# =============================
bot.run(TOKEN)
