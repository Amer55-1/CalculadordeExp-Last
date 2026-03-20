# EXP Combo Discord Bot

A Discord bot to calculate **EXP combinations** for LastChaos-like systems.  
It can recommend item combinations to reach 500% EXP, calculate totals with **boosters** and **dungeon bonuses**, and show how many EXP boosters are needed for leveling.

---

## Features

1. **Combo Calculation**
   - Command: `!combo <item1> + <item2> + ...`
   - Example: `!combo Blessed Iris + Snowman`
   - The bot:
     - Finds all valid combinations that include the specified items and reach 500% EXP.
     - Calculates:
       - Base total EXP  
       - Capped total at 500%  
       - Total with boosters  
       - Total with dungeon bonus  
       - Total with boosters + dungeon
     - Limits output to the first 10 valid combos to avoid spamming.

2. **Dungeon EXP Calculation**
   - Command: `!dungeon <percent> <items>`
   - Example: `!dungeon 150 Blessed Iris + Elixir`
   - Calculates EXP considering the dungeon bonus percentage and the items provided.

3. **EXP Boosters Needed**
   - Command: `!booster <start_level> <end_level>`
   - Example: `!booster 1 7`
   - Shows the total number of **EXP boosters (Seeds)** required to level up from `Ascension start_level` to `end_level` using predefined booster values.

---

## Supported Items & Multipliers

| Item                  | Multiplier |
|-----------------------|------------|
| Legendary Iris        | 5.0        |
| Platinum Iris         | 3.0        |
| Blessed Iris          | 2.0        |
| Experience Scroll     | 1.5        |
| Blessed Bottle        | 1.2        |
| Cake                  | 1.3        |
| Experience Elixir     | 1.3        |
| Snowman               | 2.0        |
| Double EXP Event      | 2.0        |

> The bot automatically considers any combination that includes your specified items.

---

## Installation

1. **Clone the repository** (or upload your files to Railway/GitHub):
   ```bash
   git clone <your-repo-url>
   cd <repo-folder>