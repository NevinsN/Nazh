import secrets  # import to handle secure dice rolls

# generates a cryptographically secure dice roll
def roll(numDice, numSides):
    dieResults = []

    for i in range(numDice):
        if numSides < 1:  # check to ensure that numSides is valid
            raise ValueError("A die must have at least one side.")
        # roll for current iteration of numDice
        dieResults.append(secrets.randbelow(numSides) + 1)

    return dieResults  # returns the results of the rolls
