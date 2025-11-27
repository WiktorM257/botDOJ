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
# START BOT
# =============================
bot.run(TOKEN)
