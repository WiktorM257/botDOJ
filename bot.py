import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import requests
import os

# =============================
# KONFIGURACJA
# =============================
TOKEN = os.getenv("TOKEN")
API_ADD = "https://doj-backend-ac2o.onrender.com/api/add_schedule"
API_GET = "https://doj-backend-ac2o.onrender.com/schedule.json"
API_DELETE = "https://doj-backend-ac2o.onrender.com/api/delete_schedule"

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
# /rozprawa — dodawanie sprawy
# =============================
@bot.slash_command(
    name="rozprawa",
    description="Dodaj rozprawę do wokandy DOJ."
)
async def rozprawa(
    inter: Interaction,
    sedzia: str = SlashOption(description="Sędzia prowadzący"),
    prokurator: str = SlashOption(description="Prokurator"),
    sala: str = SlashOption(description="Numer sali sądowej"),
    oskarzony: str = SlashOption(description="Oskarżony / pozwany"),
    adwokat: str = SlashOption(description="Adwokat"),
    data: str = SlashOption(description="Data (np. 28.11.2025)"),
    godzina: str = SlashOption(description="Godzina (np. 14:30)"),
    strony: str = SlashOption(description="Strony sprawy (np. SA vs Kowalski)"),
    swiadkowie: str = SlashOption(description="Świadkowie (oddzieleni przecinkami)", required=False),
    opis: str = SlashOption(description="Krótki opis sprawy",required=False)
):

    await inter.response.send_message("⏳ Dodawanie rozprawy...", ephemeral=True)

    swiadkowie = swiadkowie or ""

    payload = {
        "name": f"{oskarzony} - {adwokat}",
        "judge": sedzia,
        "prosecutor": prokurator,
        "defendant": oskarzony,
        "lawyer": adwokat,
        "witnesses": swiadkowie,
        "room": sala,
        "date": data,
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
# /usun_rozprawe — usuwanie sprawy
# =============================
@bot.slash_command(
    name="usun_rozprawe",
    description="Usuń rozprawę z wokandy po ID."
)
async def usun_rozprawe(
    inter: Interaction,
    id_rozprawy: int = SlashOption(description="ID rozprawy do usunięcia")
):
    await inter.response.send_message("⏳ Szukam rozprawy...", ephemeral=True)

    # pobierz listę
    try:
        data = requests.get(API_GET).json()
    except:
        return await inter.edit_original_message("❌ Błąd pobierania danych API.")

    # znajdź
    znalezione = next((t for t in data if t["id"] == id_rozprawe), None)

    if not znalezione:
        return await inter.edit_original_message("❌ Nie znaleziono rozprawy o podanym ID.")

    # usuń
    try:
        r = requests.post(API_DELETE, json={"id": id_rozprawe})
    except Exception as e:
        return await inter.edit_original_message(f"❌ Błąd API: {e}")

    if r.status_code == 200:
        await inter.edit_original_message(f"✔ Usunięto rozprawę o ID **{id_rozprawe}**.")
    else:
        await inter.edit_original_message(f"❌ Błąd API: {r.status_code}")

# =============================
# Archiwizacja  Rozprawy
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
    wyrok: str = nextcord.SlashOption(
        name="wyrok",
        description="Treść wyroku"
    ),
    dokument: str = nextcord.SlashOption(
        name="dokument",
        description="Link do uzasadnienia (PDF)"
    )
):
    await inter.response.defer()

    payload = {
        "id": id,
        "result": wynik,
        "verdict": wyrok,
        "document": dokument
    }

    try:
        r = requests.post("https://doj-backend-ac2o.onrender.com/api/archive_case", json=payload)

        if r.status_code == 200:
            await inter.followup.send(f"📁 Sprawa **{id}** została zarchiwizowana.\nWynik: **{wynik}**")
        elif r.status_code == 404:
            await inter.followup.send(f"❌ Nie znaleziono sprawy o ID **{id}**.")
        else:
            await inter.followup.send("❌ Błąd API podczas archiwizacji.")

    except Exception as e:
        await inter.followup.send(f"❌ Błąd serwera: {e}")


# =============================
# START BOT
# =============================
bot.run(TOKEN)

