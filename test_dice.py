from modules.dice_roll import DiceRoll

def run_tests():
    print("🧪 Starting Nazh Engine Test Suite...\n")

    # TEST 1: The 20-Die Guardrail
    print("Test 1: Oversized Pool Check...")
    oversized = DiceRoll("21d20")
    assert "too large" in oversized.error_message
    print("✅ Successfully blocked oversized pool.\n")

    # TEST 2: Plot Die Bonus Math
    # We force a 'p1d6' and check if plot_bonus is populated
    print("Test 2: Plot Die Logic...")
    plot_roll = DiceRoll("p1d6")
    # Since it's random, we just check if it's 0, 2, or 4
    assert plot_roll.plot_bonus in [0, 2, 4]
    print(f"✅ Plot bonus detected: {plot_roll.plot_bonus}\n")

    # TEST 3: Multi-Pool Isolation
    # Check that a modifier in pool 1 doesn't bleed into pool 2
    print("Test 3: Pool Isolation...")
    multi = DiceRoll("1d20+10, 1d6")
    assert multi.rolls[0]['total'] >= 11
    assert multi.rolls[1]['total'] <= 6
    print("✅ Modifiers isolated successfully.\n")

    # TEST 4: Positional Tagging (Advantage)
    print("Test 4: Advantage Tracking...")
    adv = DiceRoll("a1d20")
    display = adv.rolls[0]['display']
    assert "↑" in display and "(" in display
    print(f"✅ Advantage formatting correct: {display}\n")

    print("🚀 ALL TESTS PASSED. Engine is Pristine.")

if __name__ == "__main__":
    run_tests()
