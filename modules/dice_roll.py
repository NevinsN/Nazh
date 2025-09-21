import secrets  # import to handle secure dice rolls


class DiceRoll():

    def __init__(self, dice_command):
        self.ErrorMessage = "none"
        tempHolder = self.parseDiceCommand(dice_command)

        if self.ErrorMessage == "none":
            self.numDice = tempHolder[0]
            self.numSides = tempHolder[1]
            self.modifiers = tempHolder[2]
        
    def setErrorMessage(self, errorMessage):
        self.ErrorMessage = errorMessage

    def getErrorMessage(self):
        return self.ErrorMessage
    
    def setNumDice(self, numDice):
        self.numDice = numDice

    def getNumDice(self):
        return self.numDice
    
    def setNumSides(self, numSides):
        self.numSides = numSides

    def getNumSides(self):
        return self.numSides
    
    def setModifiers(self, modifiers):
        self.modifiers = modifiers

    def getModifiers(self):
        return self.modifiers
    
    # generates a cryptographically secure dice roll
    def roll(self):
        dieResults = []

        for i in range(self.getNumDice()):
            # roll for current iteration of numDice
            dieResults.append(secrets.randbelow(self.getNumSides()) + 1)

        return dieResults  # returns the results of the rolls

    # parses self.dice_command into seperate parts
    def parseDiceCommand(self, dice_command):
        splitCommands = dice_command.lower().split('d')
        if len(splitCommands) <= 1:
            self.setErrorMessage("Invalid dice notation. Please use XdY format")
            return
        
        numDice = splitCommands[0]
        sidesAndModifiers = splitCommands[1]

        for i in sidesAndModifiers:
            if i == "+" or i == "-":
                try:
                    numSides, modifiers = map(int, sidesAndModifiers.lower().split(i))
                except ValueError:
                    self.setErrorMessage("Modifiers must be an integer")
                    return
                
                modifiers = modifiers * int(i + "1")

                break
            else:
                numSides = sidesAndModifiers
                modifiers = 0

        try:
            numDice = int(numDice)
        except ValueError:
            self.setErrorMessage("Number of dice must be an integer")
            return
        
        try:
            numSides = int(numSides)
        except ValueError:
            self.setErrorMessage("Number of sides must be an integer")
            return
        
        if numDice is int and numSides is int:
            if numDice <= 0 or numSides <= 0:
                self.setErrorMessage("Number of dice and sides must be above 0.")
                return
        
        return [numDice, numSides, modifiers]
