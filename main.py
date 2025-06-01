import sys
import subprocess
import json
import time
import logging
import os
import asyncio
from datetime import datetime
from colorama import init, Fore, Style
os.system("Title discord.gg/driizzyyboosts")
init(autoreset=True)
UNINSTALL_LIST = ["discord.py"]
REQUIRED_PACKAGES = ["discord.py-self", "colorama"]
def uninstall_conflicts():
    print(Fore.YELLOW + "[*] Uninstalling conflicting packages...")
    for pkg in UNINSTALL_LIST:
        subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", pkg])
        print(Fore.GREEN + f"  ✅ Uninstalled: {pkg}")
def install_requirements():
    print(Fore.YELLOW + "[*] Installing required packages...")
    for pkg in REQUIRED_PACKAGES:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", pkg])
        print(Fore.GREEN + f"  ✅ Installed: {pkg}")
uninstall_conflicts()
install_requirements()
import os
os.system("cls" if os.name == "nt" else "clear")
try:
    import discord
    for name in logging.root.manager.loggerDict:
        if name.startswith("discord"):
            logger = logging.getLogger(name)
            logger.setLevel(logging.CRITICAL)
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
except ImportError as e:
    print(Fore.RED + f"[ERROR] Failed to import discord.py-self: {e}")
    sys.exit(1)
input(Fore.CYAN + "[*] Press ENTER to start the guild tag rotator...")
os.system("cls" if os.name == "nt" else "clear")
print(Fore.WHITE + "Starting rotator, please wait")
try:
    with open("config.json", "r") as f:
        config = json.load(f)
except Exception as e:
    print(Fore.RED + f"[ERROR] Failed to load config.json: {e}")
    sys.exit(1)
TOKEN = config.get("token")
EXACT_TAG_TIME = config.get("rotation_interval", 30)
GUILD_TAGS = config.get("guild_tags", [])
if not TOKEN or not GUILD_TAGS:
    print(Fore.RED + "[ERROR] 'token' or 'guild_tags' missing in config.json")
    sys.exit(1)
class SimpleSelfBot(discord.Client):
    async def on_ready(self):
        print(Fore.GREEN + f"[READY] Logged in as {self.user}")
        self.loop.create_task(tag_changer_loop(self))
async def change_to_tag(client, tag_id, tag_name):
    try:
        await client.http.request(
            discord.http.Route('PUT', "/users/@me/clan"),
            json={"identity_guild_id": tag_id, "identity_enabled": True},
            headers={"Content-Type": "application/json"}
        )
        guild = client.get_guild(int(tag_id))
        server_name = guild.name if guild else f"Unknown Guild ({tag_id})"
        now = datetime.now().strftime("[%H:%M:%S]")
        print(Fore.GREEN + f"{now} Guild Tag changed to '{tag_name}' in '{server_name}'")
        return True
    except discord.HTTPException as e:
        print(Fore.RED + f"[ERROR] Failed to set guild tag '{tag_name}' for {tag_id}: {e}")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Unexpected error for {tag_id}: {e}")
    return False
async def tag_changer_loop(client):
    index = 0
    start_time = time.time()
    next_change_time = start_time + EXACT_TAG_TIME
    if GUILD_TAGS:
        first = GUILD_TAGS[0]
        await change_to_tag(client, first["id"], first["name"])
    while True:
        try:
            now = time.time()
            if now < next_change_time:
                await asyncio.sleep(1)
                continue
            index = (index + 1) % len(GUILD_TAGS)
            current = GUILD_TAGS[index]
            for attempt in range(3):
                if await change_to_tag(client, current["id"], current["name"]):
                    break
                await asyncio.sleep(0.5)
            next_change_time = time.time() + EXACT_TAG_TIME
        except Exception as e:
            print(Fore.YELLOW + f"[WARNING] Loop issue: {e}")
            await asyncio.sleep(5)
client = SimpleSelfBot()
client.run(TOKEN)