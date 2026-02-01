import secrets
import re
from typing import List, Dict, Any

class DiceRoll:
    def __init__(self, dice_input: str):
        self.error_message: str = None  # None object, not "none" string
        self.rolls: List[Dict[str, Any]] = []
        self.plot_bonus: int = 0
        self._input_str = dice_input
        self._process_input()

    def _process_input(self) -> None:
        if not self._input_str:
            return

        # Split by comma and clean whitespace
        parts = [p.strip() for p in self._input_str.split(",") if p.strip()]
        for part in parts:
            # Regex: tags (optional), count, d, sides, mod (optional)
            match = re.match(r"([a-z]+)?(\d+)d(\d+)([+-]\d+)?", part.lower())
            if not match:
                self.error_message = f"Invalid format: '{part}'"
                return
            
            tags_str, count_str, sides_str, mod_str = match.groups()
            count, sides, mod = int(count_str), int(sides_str), int(mod_str or 0)
            tags = list(tags_str) if tags_str else []
            
            # SRE Guardrail: Prevent excessive loops
            if count > 20:
                self.error_message = f"Pool size too large ({count}). Max 20."
                return
                
            self._execute_roll(count, sides, mod, tags, part)

    def _execute_roll(self, count: int, sides: int, mod: int, tags: list, original_input: str) -> None:
        final_results = []
        calc_values = []
        is_plot = 'p' in tags

        # Helper for Natural 1/Max formatting
        def format_die(val, s):
            if val == 1:
                return f"*{val}*" # Italicize Nat 1
            if val == s:
                return f"**{val}**" # Bold Nat Max
            return str(val)

        for i in range(count):
            tag = tags[i] if i < len(tags) else None
            
            if tag == 'p':  # Plot Die Logic (1d6)
                r = secrets.randbelow(6) + 1
                bonus = 2 if r <= 2 else (4 if r >= 5 else 0) # Nazh Plot Rules
                lbl = "!!(T)" if r <= 2 else ("**(O)**" if r >= 5 else "")
                
                r_formatted = format_die(r, 6)
                final_results.append(f"[{r_formatted}{lbl}]")
                calc_values.append(0) # Plot dice don't add to sum, they provide bonus
                self.plot_bonus = bonus
                
            elif tag in ['a', 'd']: # Adv / Disadv
                d1, d2 = secrets.randbelow(sides) + 1, secrets.randbelow(sides) + 1
                kept = max(d1, d2) if tag == 'a' else min(d1, d2)
                drop = min(d1, d2) if tag == 'a' else max(d1, d2)
                sym = "↑" if tag == 'a' else "↓"
                
                final_results.append(f"[{format_die(kept, sides)}{sym}({format_die(drop, sides)})]")
                calc_values.append(kept)
                
            else: # Standard Die
                d = secrets.randbelow(sides) + 1
                final_results.append(f"[{format_die(d, sides)}]")
                calc_values.append(d)

        # Apply Modifiers and enforce "Minimum 1" rule
        # Plot dice usually don't take modifiers in this engine
        raw_total = sum(calc_values) + (0 if is_plot else mod)
        pool_total = max(1, raw_total) 
        
        # Track if we had to floor the result to 1
        was_floored = pool_total > raw_total and not is_plot

        self.rolls.append({
            "sides": sides,
            "label": original_input,
            "display": "".join(final_results),
            "total": pool_total,
            "was_floored": was_floored
        })
