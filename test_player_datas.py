from managers.valorant_api import henrik

import sys
import asyncio
import json

sys.stdout.reconfigure(encoding="utf-8")

async def main():
    
    test = await henrik.get_matches("rico", "mdc", 2)

    with open("matches.json", "w", encoding="utf-8") as f:
        json.dump(test, f, indent=4, ensure_ascii=False)

    map = test[1]["metadata"]["map"]["name"]
    print(map)
    players = test[1]["players"]
    for player in players:
        print (player["name"])

if __name__ == "__main__":
    asyncio.run(main())