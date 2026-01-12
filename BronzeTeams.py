import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}
def get_html(URL:str):
    return requests.get(URL, headers=headers).text

soup = BeautifulSoup(get_html('https://mobalytics.gg/tft/champions'), 'html.parser')

champions = {}

for card in soup.select('.m-2ni1l0'):
    name_tag = card.select_one('.m-1xvjosc')
    if not name_tag:
        continue

    champion_name = name_tag.get_text(strip=True)

    cost_img = card.select_one('.m-13xip9')
    cost = cost_img.find_next_sibling(text=True).strip() 
    attributes = [
        div.get_text(strip=True)
        for div in card.select('.m-1jj7hqe')
    ]

    champions[champion_name] = {
        "cost": cost,
        "attributes": attributes
    }


excluded_champions = ['Galio', 'Baron Nashor', 'Brock', 'Sylas', 'Aurelion Sol', 'Tahm Kench', 'T-Hex', 'Ziggs']
traits = {}



# Attributes
traits['Bruiser'] = [2,4,6]
traits['Defender'] = [2,4,6]
traits['Gunslinger'] = [2,4]
traits['Invoker'] = [2,4]
traits['Juggernaut'] = [2,4,6]
traits['Longshot'] = [2,3,4,5]
traits['Disruptor'] = [2,4]
traits['Quickstriker'] = [2,3,4,5]
traits['Slayer'] = [2,4,6]
traits['Arcanist'] = [2,4,6]
traits['Vanquisher'] = [2,3,4,5]
# Region
traits['Warden'] = [2,3,4.5]
traits['Demacia'] = [3,5,7,11]
traits['Ixtal'] = [3,5,7]
traits['Freljord'] = [3,5,7]
traits['Ionia'] = [3,5,7,10]
traits['Noxus'] = [3,5,7,10]
traits['Piltover'] = [2,4,6]
traits['Shadow Isles'] = [2,3,4,5]
traits['Shurima'] = [2,3,4]
traits['Targon'] = 1
traits['Void'] = [2,4,6,9]
traits['Yordle'] = [2,4,6,8,10]
traits['Zaun'] = [3,5,7]

from itertools import combinations
from collections import Counter
import math

excluded_champions = ['Rift Herald', 'Kennen', 'Kobuko & Yuumi', 'Diana','Galio', 'Baron Nashor', 'Brock', 'Sylas', 'Aurelion Sol', 'Tahm Kench', 'T-Hex', 'Ziggs', "Kai'Sa"]

LEVEL_MAX_COST = {
    1: 1,
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 4,
    7: 5,
    8: 5,
    9: 5,
    10: 5,
    11: 5,
}

def _bronze_threshold(traits, trait_name):
    req = traits[trait_name]
    if isinstance(req, (list, tuple)):
        return int(math.ceil(req[0]))
    return int(math.ceil(req))

def bronze_traits_for_team(team, champions, traits):
    trait_counts = Counter()
    for champ in team:
        champ_data = champions[champ]
        for t in champ_data.get("attributes", []):
            trait_counts[t] += 1

    active_bronze = {
        t for t, c in trait_counts.items()
        if t in traits and c >= _bronze_threshold(traits, t)
    }
    return len(active_bronze), active_bronze, trait_counts

def best_bronze_team_legal(
    champions,
    traits,
    level,
    team_size=None,
    top_n=10,
    progress_step=1,
    excluded=None
):

    if level not in LEVEL_MAX_COST:
        raise ValueError(f"Unsupported level={level}. Supported: {sorted(LEVEL_MAX_COST)}")

    if team_size is None:
        team_size = level

    if team_size > level:
        raise ValueError(f"Illegal team_size={team_size} at level={level}. Board cap is {level}.")

    excluded_set = set(excluded_champions)
    if excluded:
        excluded_set |= set(excluded)

    max_cost = LEVEL_MAX_COST[level]

    champ_names = [
        name for name, data in champions.items()
        if name not in excluded_set and int(data.get("cost", 0)) <= max_cost
    ]

    if team_size > len(champ_names):
        raise ValueError(
            f"team_size={team_size} is larger than available legal champions "
            f"({len(champ_names)}) at level={level} after exclusions."
        )

    total = math.comb(len(champ_names), team_size)
    next_progress = progress_step
    processed = 0

    best = []
    best_score = -1

    for team in combinations(champ_names, team_size):
        processed += 1

        pct_done = (processed / total) * 100
        if pct_done >= next_progress:
            print(f"{pct_done:.1f}% done ({processed}/{total})")
            next_progress += progress_step

        score, bronze_set, counts = bronze_traits_for_team(team, champions, traits)

        if score > best_score:
            best_score = score
            best = [(score, team, bronze_set, counts)]
        elif score == best_score:
            best.append((score, team, bronze_set, counts))

    def secondary_key(item):
        score, team, bronze_set, counts = item
        distinct_present = len(counts)
        return (-score, -distinct_present, team)

    best.sort(key=secondary_key)

    results = []
    for score, team, bronze_set, counts in best[:top_n]:
        results.append({
            "level": level,
            "team_size": team_size,
            "max_cost_allowed": max_cost,
            "team": team,
            "bronze_count": score,
            "bronze_traits": sorted(bronze_set),
            "trait_counts": dict(counts),
        })

    return results



import json
from datetime import datetime, timezone

def export_best_teams_levels_2_to_5(
    champions,
    traits,
    out_path="best_teams_levels_2_to_5.json",
    top_n=20,
    excluded=None,
):
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "top_n": top_n,
        "levels": {}
    }

    for level in range(2, 6):  # 2,3,4,5
        results = best_bronze_team_legal(
            champions,
            traits,
            level=level,
            top_n=top_n,
            excluded=excluded,
        )

        # Make JSON shape explicit/consistent (optional but recommended)
        for r in results:
            r["team"] = list(r["team"])  # tuple -> list

        payload["levels"][str(level)] = results

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return out_path

# Usage
path = export_best_teams_levels_2_to_5(champions, traits, out_path="best_levels_2_5.json", top_n=20)
print("Wrote:", path)