
# TFT Bronze For Life — Team Finder

A tool for discovering the best early-game team compositions in Teamfight Tactics (TFT) that maximize bronze-tier trait activations.

Teamfight Tactics (TFT) is an auto-battler strategy game by Riot Games where players draft and position a team of champions that then fight automatically each round. Players manage gold, level (board size), and champion selection while building synergies called **traits** (origins/classes) that grant bonuses when multiple champions of the same trait are fielded.

**Bronze traits** are the lowest activation threshold for any trait—hitting these early enables stable, low-cost compositions that synergize well and prepare you for mid-game transitions. "Bronze For Life" is a playstyle that focuses on early consistency and hitting these baseline synergies.

## What This Project Does

This project consists of two parts:

1. **[BronzeTeams.py](BronzeTeams.py)** — A Python script that:
   - Scrapes champion data from Mobalytics
   - Filters legal champions by cost for each player level
   - Exhaustively enumerates all possible team combinations
   - Ranks teams by how many bronze-tier traits they activate
   - Outputs the best compositions as JSON

2. **Web Interface** — An interactive HTML/CSS/JavaScript frontend that:
   - Loads pre-computed best teams (from `best_levels_2_5.json`)
   - Lets you filter by player level
   - Search for champions you already own
   - Displays teams ranked by how close you are to completing them
   - Sort results by overlap or trait count

## Project Structure

- [BronzeTeams.py](BronzeTeams.py) — Main Python script for finding best team compositions
- [app.js](app.js) — Frontend JavaScript for the web interface
- [index.html](index.html) — Web interface markup
- [styles.css](styles.css) — Web interface styling
- [best_levels_2_5.json](best_levels_2_5.json) — Pre-computed best teams for levels 2–5

## Quick Start

### Using the Web Interface

Simply open `index.html` in your browser. The interface loads pre-computed team data and lets you:
- Select your player level
- Search for champions you own
- See which teams you can complete with your current board
- Sort by overlap or trait activation count

### Running the Python Script

To generate fresh team data:

```bash
pip install requests beautifulsoup4
python BronzeTeams.py
```

The script will scrape current champion data and output the best teams for each level.

## Features

- **Fast lookups** — Pre-computed JSON makes the web interface instant
- **Flexible filtering** — Search champions and see only relevant teams
- **Smart ranking** — Teams are ranked by how close you already are to completing them
- **Live scraping** — Python script pulls current champion data from Mobalytics
- **Exhaustive search** — Finds the absolute best teams, not heuristic approximations

## Customization

### Adjusting Trait Thresholds

Edit the `traits` dictionary in [BronzeTeams.py](BronzeTeams.py) to change what counts as a "bronze" activation:

```python
traits['Bruiser'] = [2, 4, 6]  # bronze=2, next=4, next=6
traits['Gunslinger'] = [2, 4]  # bronze=2, next=4
```

### Filtering by Level

Open [BronzeTeams.py](BronzeTeams.py) and modify the parameters at the bottom of the script:

```python
level = 4  # player level
team_size = 4  # team size (defaults to level)
top_n = 1000  # how many top teams to output
```
## Limitations & Notes

- The Python script scrapes a live website; it may break if Mobalytics changes their HTML structure
- This is an exhaustive combinatorial search — for high levels with large champion pools, runtime grows quickly
- Results are only as accurate as the champion data being scraped; ensure trait names match your game version

## Wanna use it?
It's currently on my [website](https://yousefedd.in/tft-team-search/)! Stop by!
## License

See [LICENSE](LICENSE) for terms.

