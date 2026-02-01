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
            # Regex: (tags)(count)d(sides)(modifier)
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
        final_rolls = []
        for i in range(count):
            tag = tags[i] if i < len(tags) else None
            d1 = secrets.randbelow(sides) + 1
            
            if tag == 'a':
                d2 = secrets.randbelow(sides) + 1
                final_rolls.append(max(d1, d2))
            elif tag == 'd':
                d2 = secrets.randbelow(sides) + 1
                final_rolls.append(min(d1, d2))
            else:
                final_rolls.append(d1)

        self.rolls.append({
            "count": count, "sides": sides, "mod": mod,
            "individual": final_rolls, "total": sum(final_rolls) + mod,
            "tags": tags # Stored for visual output
        })

    async def send_result_message(self, interaction: discord.Interaction) -> None:
        output = [f"**Rolling:**\n• `{self._input_str}`\n\n**Results:**"]
        
        for roll in self.rolls:
            mod_str = f"{roll['mod']:+}" if roll['mod'] != 0 else ""
            dice_str = f"{roll['count']}d{roll['sides']}{mod_str}"
            
            # Format results: Bold modified dice, normal for others
            res_list = []
            for i, val in enumerate(roll['individual']):
                if i < len(roll['tags']):
                    tag_label = "↑" if roll['tags'][i] == 'a' else "↓"
                    res_list.append(f"[{val}{tag_label}]")
                else:
                    res_list.append(f"[{val}]")
            
            bracketed = "".join(res_list)
            output.append(f"=`{dice_str}`=={bracketed}==**{{ {roll['total']} }}**")
        
        msg = "\n".join(output)
        if interaction.response.is_done():
            await interaction.followup.send(msg)
        else:
            await interaction.response.send_message(msg)
