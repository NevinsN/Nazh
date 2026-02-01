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
        """Formats and sends the final results to the user."""
        output = []
        for roll in self.rolls:
            mod_str = f"{roll['mod']:+}" if roll['mod'] != 0 else ""
            results = ", ".join(map(str, roll['individual']))
            output.append(f"🎲 **{roll['count']}d{roll['sides']}{mod_str}**: `{results}` | **Total: {roll['total']}**")
        
        final_msg = "\n".join(output)
        if interaction.response.is_done():
            await interaction.followup.send(final_msg)
        else:
            await interaction.response.send_message(final_msg)
