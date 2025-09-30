import secrets  # import to handle secure dice rolls


class DiceRoll():

    def __init__(self, dice_command):
        self.ErrorMessage = "none"
        tempHolder = self.parseDiceCommand(dice_command)
        self.rolls = []

        if self.ErrorMessage == "none":
            self.setRolls(tempHolder)
        
    def setErrorMessage(self, errorMessage):
        self.ErrorMessage = errorMessage

    def getErrorMessage(self):
        return self.ErrorMessage
    
    def setNumDiceByIndex(self, index, numDice):
        self.rolls[index]["numDice"] = numDice

    def getNumDiceByIndex(self, index):
        return self.rolls[index].get("numDice")
    
    def setNumSidesByIndex(self, index, numSides):
        self.rolls[index]["numSides"] = numSides

    def getNumSidesByIndex(self, index):
        return self.rolls[index].get("numSides")
    
    def setModifiersByIndex(self, index, modifiers):
        self.rolls[index]["modifiers"] = modifiers

    def getModifiersByIndex(self, index):
        return self.rolls[index]["modifiers"]
    
    def setRolls(self, rolls):
        self.rolls = rolls

    def getRolls(self):
        return self.rolls

    # generates a cryptographically secure dice roll
    def roll(self, dicePool):
        dieResults = []

        for i in range(dicePool["numDice"]):
            # roll for current iteration of numDice
            dieResults.append(secrets.randbelow(dicePool["numSides"]) + 1)

        return dieResults  # returns the results of the rolls

    # parses self.dice_command into seperate parts
    def parseDiceCommand(self, dice_command):
        returnStrings = []
        commaCommands = [command.strip() for command in dice_command.lower().split(",")]
        
        for command in commaCommands:
            preCodes = ""

            if (command == 'p' or 
                command == "plot" or 
                command == "ap" or 
                command == "dp" or 
                command == "aplot" or 
                command == "dplot"):
                for char in command:
                    if char == 'a' or char == 'd':
                        preCodes += char
                returnStrings.append({"preCodes": preCodes, 
                                      "numDice": 1, 
                                      "numSides" : 6, 
                                      "modifiers" : 0,
                                      "plot" : True})
                continue

            for char in command:
                if char == 'a' or char == 'd':
                    preCodes += char
                elif char.isdigit() == True:
                    break
                else:
                    self.setErrorMessage("Invalid leading command. Only 'a', 'd', or 'plot' may be used")
                    return

            command = command[len(preCodes):]

            splitCommands = command.lower().split('d')

            if len(splitCommands) <= 1:
                self.setErrorMessage("Invalid dice notation. Please use XdY format")
                return

            numDice = splitCommands[0]
            sidesAndModifiers = splitCommands[1]

            if len(preCodes) > int(numDice):
                self.setErrorMessage("Too many leading modifiers. Advantage and disadvantage cannot exceed number of dice")
                return

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
                
            returnStrings.append({"preCodes": preCodes, 
                                  "numDice": numDice, 
                                  "numSides" : numSides, 
                                  "modifiers" : modifiers,
                                  "plot" : False})
        
        return returnStrings

    async def getAndSendResultMessage(self, ctx):
        allRolls = []
        
        for roll in self.getRolls():
            currentRolls = {}
            currentRolls["code"] = f"""{roll["preCodes"]}{roll["numDice"]}d{roll["numSides"]}{roll["modifiers"] if roll["modifiers"] < 0 else ("+" + str(roll["modifiers"]) if roll["modifiers"] > 0 else "")}"""
            currentRolls["preCodes"] = roll["preCodes"]
            currentRolls["plot"] = roll["plot"]

            if roll["preCodes"] == "":
                currentRolls["roll"] = self.roll(roll)
                currentRolls["total"] = sum(currentRolls["roll"]) + roll["modifiers"]
            else:
                currentRolls["roll"] = self.roll({"numDice": roll["numDice"] + len(roll["preCodes"]), "numSides": roll["numSides"]})
                
                testCodes = roll["preCodes"]
                testRolls = currentRolls["roll"]
                currentRolls["total"] = 0

                while len(testCodes) > 0:
                    if testCodes[0] == "a":
                        currentRolls["total"] += max(testRolls[0], testRolls[1])
                        testCodes = testCodes[1:]
                        testRolls = testRolls[2:]
                    else:
                        currentRolls["total"] += min(testRolls[0], testRolls[1])
                        testCodes = testCodes[1:]
                        testRolls = testRolls[2:]
                
                if len(testRolls) > 0:
                    currentRolls["total"] += sum(testRolls) + roll["modifiers"]
                else:
                    currentRolls["total"] += roll["modifiers"]
                
                if roll["plot"] == True:
                    currentRolls["preCodes"] += "Plot"

            allRolls.append(currentRolls)

        message = f"""{ctx.author.mention}\n**Rolling:**\n* """
            
        for index, roll in enumerate(allRolls):
            if index == len(allRolls) - 1:
                if roll["plot"] == True:
                    if roll["preCodes"] != "":
                        message += f"{roll["preCodes"]}, \n**Results:**\n"
                    else:
                        message += "Plot, \n**Results:**\n"
                else:
                    message += roll["code"] + "\n**Results:**\n"
            else:
                if roll["plot"] == True:
                    
                    if roll["preCodes"] != "":
                        message += f"{roll["preCodes"]}, "
                    else:
                        message += "Plot, "
                else:
                    message += roll["code"] + ", "

        for roll in allRolls:
            if roll["preCodes"] == "":
                message += f"""> =**{"Plot" if roll["plot"] else str(roll["code"])}**==[**{"**][**".join(map(str, roll["roll"]))}**]==**{{{str(roll["total"])}}}**\n"""
            else:
                testCodes = roll["preCodes"]
                testRolls = roll["roll"]

                message += f"> =**{testCodes if roll["plot"] == True else str(roll["code"])}**=="

                while len(testCodes) > 0:
                    if testCodes[0] == "a":
                        if testRolls[0] >= testRolls[1]:
                            message += f"[**{testRolls[0]}**][~~{testRolls[1]}~~]"
                        else:
                            message += f"[~~{testRolls[0]}~~][**{testRolls[1]}**]"
                        testCodes = testCodes[1:]
                        testRolls = testRolls[2:]
                    elif testCodes[0] == "d":
                        if testRolls[0] < testRolls[1]:
                            message += f"[**{testRolls[0]}**][~~{testRolls[1]}~~]"
                        else:
                            message += f"[~~{testRolls[0]}~~][**{testRolls[1]}**]"
                        testCodes = testCodes[1:]
                        testRolls = testRolls[2:]
                    else:
                        break
                
                if len(testRolls) > 0:
                    message += f"[**{"**][**".join(map(str, testRolls))}**]==**{{ {str(roll["total"])} }}**\n"
                else:
                    message += f"==**{{ {str(roll["total"])} }}**\n"

        await ctx.send(message)
                   