import secrets
import re
from typing import List, Dict, Any

class DiceRoll:
    def __init__(self, dice_input: str):
        self.error_message: str = None
        self.rolls: List[Dict[str, Any]] = []
        self.plot_bonus: int = 0
        self._input_str = dice_input
        self._process_input()

    def _process_input(self) -> None:
        if not self._input_str: return
        parts = [p.strip() for p in self._input_str.split(",") if p.strip()]
        for part in parts:
            match = re.match(r"([a-z]+)?(\d+)d(\d+)([+-]\d+)?", part.lower())
            if not match:
                self.error_message = f"Invalid format: '{part}'"
                return
            tags_str, count_str, sides_str, mod_str = match.groups()
            count, sides, mod = int(count_str), int(sides_str), int(mod_str or 0)
            tags = list(tags_str) if tags_str else []
            if count > 20:
                self.error_message = f"Pool size too large. Max 20."
                return
            self._execute_roll(count, sides, mod, tags, part)

    def _execute_roll(self, count: int, sides: int, mod: int, tags: list, original_input: str) -> None:
        final_results, calc_values = [], []
        is_plot = 'p' in tags

        def format_die(val, s):
            if val == 1: return f"*{val}*"
            if val == s: return f"**{val}**"
            return str(val)

        for i in range(count):
            tag = tags[i] if i < len(tags) else None
            if tag == 'p': # Plot Die logic
                r = secrets.randbelow(6) + 1
                # 1 results in +2, 2 results in +4
                bonus = 2 if r == 1 else (4 if r == 2 else 0)
                lbl = "!!(T)" if r <= 2 else ("**(O)**" if r >= 5 else "")
                final_results.append(f"[{format_die(r, 6)}{lbl}]")
                calc_values.append(0) # Plot dice total to 0
                self.plot_bonus = bonus
            elif tag in ['a', 'd']:
                d1, d2 = secrets.randbelow(sides) + 1, secrets.randbelow(sides) + 1
                kept = (max(d1, d2) if tag == 'a' else min(d1, d2))
                drop = (min(d1, d2) if tag == 'a' else max(d1, d2))
                sym = "↑" if tag == 'a' else "↓"
                final_results.append(f"[{format_die(kept, sides)}{sym}({format_die(drop, sides)})]")
                calc_values.append(kept)
            else:
                d = secrets.randbelow(sides) + 1
                final_results.append(f"[{format_die(d, sides)}]")
                calc_values.append(d)

        # FIX: Unified indentation for the floor logic
        raw_total = sum(calc_values) + (0 if is_plot else mod)
        pool_total = max(1, raw_total)
        was_floored = pool_total > raw_total and not is_plot

        self.rolls.append({
            "label": original_input,
            "display": "".join(final_results),
            "total": pool_total,
            "was_floored": was_floored
        })
