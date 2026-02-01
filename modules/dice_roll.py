import secrets
import re
from typing import List, Dict, Any, Union
import discord

class DiceRoll:
    """
    Logic engine for parsing dice strings and generating secure results.
    """
    def __init__(self, dice_input: str):
        self.error_message: str = "none"
        self.rolls: List[Dict[str, Any]] = []
        self._input_str = dice_input
        self._process_input()

    def _process_input(self) -> None:
        """Internal orchestrator for parsing and rolling."""
        # Clean the string and split by commas for multiple pools
        parts = [p.strip() for p in self._input_str.split(",")]
        for part in parts:
            match = re.match(r"(\d+)d(\d+)([+-]\d+)?", part.lower())
            if not match:
                self.error_message = f"Invalid format: '{part}'"
                return
            
            count, sides, mod = match.groups()
            self._execute_roll(int(count), int(sides), int(mod or 0))

    def _execute_roll(self, count: int, sides: int, mod: int) -> None:
        """Generates CSPRNG rolls for a specific die set."""
        if count > 100 or sides > 1000:
            self.error_message = "Dice count or sides too high (Limit: 100d1000)"
            return

        individual_rolls = [secrets.randbelow(sides) + 1 for _ in range(count)]
        total = sum(individual_rolls) + mod
        
        self.rolls.append({
            "count": count,
            "sides": sides,
            "mod": mod,
            "individual": individual_rolls,
            "total": total
        })

    async def send_result_message(self, interaction: discord.Interaction) -> None:
        """Correctly indented logic to fix the Extension Error."""
        output = [f"**Rolling:**\n• {self._input_str}\n\n**Results:**"]
        
        for roll in self.rolls:
            # Reconstruct the dice string (e.g., 2d100-8)
            mod_str = f"{roll['mod']:+}" if roll['mod'] != 0 else ""
            dice_str = f"{roll['count']}d{roll['sides']}{mod_str}"
            
            # Build the bracketed individual results: [71][2][29][78]
            bracketed_rolls = "".join([f"[{r}]" for r in roll['individual']])
            
            # Combine into your signature format: =1d12+4==[8]=={12}
            line = f"=`{dice_str}`=={bracketed_rolls}==**{{ {roll['total']} }}**"
            output.append(line)
        
        final_msg = "\n".join(output)
        
        # Check if we need to reply or followup (crucial for slash commands)
        if interaction.response.is_done():
            await interaction.followup.send(final_msg)
        else:
            await interaction.response.send_message(final_msg)
