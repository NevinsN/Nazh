import secrets
import re
import discord
from typing import List, Dict, Any

class DiceRoll:
    def __init__(self, dice_input: str):
        self.error_message: str = "none"
        self.rolls: List[Dict[str, Any]] = []
        self._input_str = dice_input
        self._process_input()

    def _process_input(self) -> None:
        parts = [p.strip() for p in self._input_str.split(",")]
        for part in parts:
            match = re.match(r"([a-z]+)?(\d+)d(\d+)([+-]\d+)?", part.lower())
            if not match:
                self.error_message = f"Invalid format: '{part}'"
                return
            
            tags_str, count, sides, mod = match.groups()
            tags = list(tags_str) if tags_str else []
            
            if len(tags) > int(count):
                self.error_message = f"Too many tags ({len(tags)}) for {count} dice."
                return
                
            self._execute_roll(int(count), int(sides), int(mod or 0), tags)

    def _execute_roll(self, count: int, sides: int, mod: int, tags: list) -> None:
        final_results = []
        calc_values = []
        
        for i in range(count):
            tag = tags[i] if i < len(tags) else None
            
            if tag == 'p':  # Plot Die Logic
                r = secrets.randbelow(6) + 1
                if r == 1: val, lbl = 2, "!!(T)"
                elif r == 2: val, lbl = 4, "!!(T)"
                elif r >= 5: val, lbl = 0, "**(O)**"
                else: val, lbl = 0, ""
                final_results.append(f"[{r}{lbl}]")
                calc_values.append(val)
            elif tag in ['a', 'd']: # Advantage/Disadvantage
                d1, d2 = secrets.randbelow(sides) + 1, secrets.randbelow(sides) + 1
                kept = max(d1, d2) if tag == 'a' else min(d1, d2)
                drop = min(d1, d2) if tag == 'a' else max(d1, d2)
                sym = "↑" if tag == 'a' else "↓"
                final_results.append(f"[{kept}{sym}({drop})]")
                calc_values.append(kept)
            else: # Standard Die
                d = secrets.randbelow(sides) + 1
                final_results.append(f"[{d}]")
                calc_values.append(d)

        self.rolls.append({
            "count": count, "sides": sides, "mod": mod,
            "display": "".join(final_results),
            "total": sum(calc_values) + mod
        })

    async def send_result_message(self, interaction: discord.Interaction, view: discord.ui.View = None) -> None:
        output = [f"**Rolling:**\n• `{self._input_str}`\n\n**Results:**"]
        for r in self.rolls:
            m = f"{r['mod']:+}" if r['mod'] != 0 else ""
            output.append(f"=`{r['count']}d{r['sides']}{m}`=={r['display']}==**{{ {r['total']} }}**")
        
        content = "\n".join(output)
        if interaction.response.is_done():
            await interaction.followup.send(content=content, view=view)
        else:
            await interaction.response.send_message(content=content, view=view)
