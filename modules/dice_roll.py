import secrets
import re
import discord
from typing import List, Dict, Any

class DiceRoll:
    def __init__(self, dice_input: str):
        self.error_message: str = None  
        self.rolls: List[Dict[str, Any]] = []
        self.plot_bonus: int = 0  # Tracks the bonus to apply to d20 pools
        self._input_str = dice_input
        self._process_input()

    def _process_input(self) -> None:
        parts = [p.strip() for p in self._input_str.split(",")]
        for part in parts:
            match = re.match(r"([a-z]+)?(\d+)d(\d+)([+-]\d+)?", part.lower())
            if not match:
                self.error_message = f"Invalid format: '{part}'"
                return
            
            tags_str, count_str, sides_str, mod_str = match.groups()
            count, sides, mod = int(count_str), int(sides_str), int(mod_str or 0)
            tags = list(tags_str) if tags_str else []
            
            # SRE Guardrail: Prevent CPU exhaustion
            if count > 20:
                self.error_message = f"Pool size too large ({count}). Max is 20 dice."
                return

            if len(tags) > count:
                self.error_message = f"Too many tags ({len(tags)}) for {count} dice."
                return
                
            self._execute_roll(count, sides, mod, tags)

    def _execute_roll(self, count: int, sides: int, mod: int, tags: list) -> None:
        final_results = []
        calc_values = []
        is_plot = 'p' in tags
        
        for i in range(count):
            tag = tags[i] if i < len(tags) else None
            
            if tag == 'p':  # Plot Die Logic
                r = secrets.randbelow(6) + 1
                bonus = 2 if r == 1 else (4 if r == 2 else 0)
                lbl = "!!(T)" if r <= 2 else ("**(O)**" if r >= 5 else "")
                final_results.append(f"[{r}{lbl}]")
                calc_values.append(bonus)
                self.plot_bonus = bonus # Store for Cog to apply to d20s
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

        # Modifiers apply to standard pools, but not plot buckets
        pool_total = sum(calc_values) + (0 if is_plot else mod)
        
        self.rolls.append({
            "sides": sides,
            "label": f"{count}d{sides}{f'{mod:+}' if mod != 0 and not is_plot else ''}",
            "display": "".join(final_results),
            "total": pool_total
        })

    async def send_result_message(self, interaction: discord.Interaction, embed: discord.Embed, view: discord.ui.View) -> None:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed, view=view)
