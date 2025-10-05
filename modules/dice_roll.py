import secrets  # import to handle secure dice rolls


class DiceRoll():
    # Constructor, takes dice_command and processes it via 
    # parseDiceCommand and sets it up for the bot to function
    def __init__(self, dice_command):
        self.ErrorMessage = "none" # holds any error messages. "none" is default
        # breaks up the command string and holds it in temporary variable
        tempHolder = self.parseDiceCommand(dice_command) 
        self.rolls = [] # initialize variable to hold all the rolls parsed from command string
        
        # ensures there are no errors thrown
        if self.ErrorMessage == "none":
            self.setRolls(tempHolder) # assigns tempHolder to rolls

    # Setter for errorMessage    
    def setErrorMessage(self, errorMessage):
        self.ErrorMessage = errorMessage

    # Getter for errorMessage
    def getErrorMessage(self):
        return self.ErrorMessage
    
    # Setter for numDice utilizing an index
    def setNumDiceByIndex(self, index, numDice):
        self.rolls[index]["numDice"] = numDice

    # Getter for numDice utilizing an index
    def getNumDiceByIndex(self, index):
        return self.rolls[index].get("numDice")
    
    # Setter for numSides utilizing an index
    def setNumSidesByIndex(self, index, numSides):
        self.rolls[index]["numSides"] = numSides

    # Getter for numSides utilizing an index
    def getNumSidesByIndex(self, index):
        return self.rolls[index].get("numSides")
    
    # Setter for modifiers utilizing an index
    def setModifiersByIndex(self, index, modifiers):
        self.rolls[index]["modifiers"] = modifiers

    # Getter for modifiers utilizing an index
    def getModifiersByIndex(self, index):
        return self.rolls[index]["modifiers"]
    
    # Setter for rolls
    def setRolls(self, rolls):
        self.rolls = rolls

    # Getter for rolls
    def getRolls(self):
        return self.rolls

    # generates a cryptographically secure dice roll
    def roll(self, dicePool):
        dieResults = [] # holds results after rolling the dice in dicePool

        # Rolls each die in the dicePool
        for i in range(dicePool["numDice"]):
            # roll for current iteration of numDice and appends to dieResults
            dieResults.append(secrets.randbelow(dicePool["numSides"]) + 1)

        return dieResults  # returns the results of the rolls

    # parses self.dice_command into seperate parts
    def parseDiceCommand(self, dice_command):
        returnStrings = [] # Array of strings to return
        # Initial split for each individual die command
        commaCommands = [command.strip() for command in dice_command.lower().split(",")]
        
        # Loops through and processes all commands in commaCommands
        for command in commaCommands:
            preCodes = "" # initiates preCodes to hold various precodes
                          # a precode in this application is something that 
                          # preceeds to the roll to modify how it is handled

            # Checks for plot dice
            if (command == 'p' or    # 
                command == "plot" or # these two are for unmodified plot dice
                command == "ap" or    # 
                command == "aplot" or # these two are for plot dice with advantage
                command == "dp" or    # 
                command == "dplot"):  # these two are for plot dice with disadvantage  
                # loops through each character in command to check for a or d
                for char in command:
                    if char == 'a' or char == 'd': # if a or d, these are added to preCodes
                        preCodes += char
                # populates the appropriate data for a plot die and appends it to returnStrings
                returnStrings.append({"preCodes": preCodes, 
                                      "numDice": 1, 
                                      "numSides" : 6, 
                                      "modifiers" : 0,
                                      "plot" : True})
                continue # continues the loop fo rolls

            # loops through each character in command to check for a or d
            for char in command:
                if char == 'a' or char == 'd': # if a or d, these are added to preCodes
                    preCodes += char
                elif char.isdigit() == True: # if isdigit, continues on with processing
                    break
                else: # There is an error in the precodes submitted
                    self.setErrorMessage("Invalid leading command. Only 'a', 'd', or 'plot' may be used")
                    return

            command = command[len(preCodes):] # strips precodes and leaves just dice and modifiers

            splitCommands = command.lower().split('d') # splits commands at the 'd' for dice

            # Error check making sure that a proper split occured
            if len(splitCommands) <= 1:
                self.setErrorMessage("Invalid dice notation. Please use XdY format")
                return

            # pulls numDice and sidesAndModifiers from splitCommands
            numDice = splitCommands[0]
            sidesAndModifiers = splitCommands[1]

            # error check to ensure no more preCodes were given than dice
            if len(preCodes) > int(numDice):
                self.setErrorMessage("Too many leading modifiers. Advantage and disadvantage cannot exceed number of dice")
                return

            # loop to check for modifiers
            for i in sidesAndModifiers:
                if i == "+" or i == "-": # checks if a character in sidesAndModifiers is + or -
                    try: # try/catch command to split at i
                        numSides, modifiers = map(int, sidesAndModifiers.lower().split(i))
                    except ValueError:
                        self.setErrorMessage("Modifiers must be an integer")
                        return
                
                    modifiers = modifiers * int(i + "1") # sets modifier to modifier * i+1
                                                         # i+1 will give us either +1 or -1
                                                         # therefor modifier will become positive 
                                                         # or negative, depending on if it's being
                                                         # added or subtracted

                    break
                else: # handles having no modifiers by setting modifier to 0
                    numSides = sidesAndModifiers
                    modifiers = 0

            # try/catch statement to check that numDice is an integer
            try:
                numDice = int(numDice)
            except ValueError:
                self.setErrorMessage("Number of dice must be an integer")
                return
        
            # try/catch statement to check that numSides is an integer
            try:
                numSides = int(numSides)
            except ValueError:
                self.setErrorMessage("Number of sides must be an integer")
                return
        
            # try/catch statement to check that numDice and numSides are both positive
            if numDice <= 0 or numSides <= 0:
                self.setErrorMessage("Number of dice and sides must be above 0.")
                return

            # builds the string to append to returnStrings    
            returnStrings.append({"preCodes": preCodes, 
                                  "numDice": numDice, 
                                  "numSides" : numSides, 
                                  "modifiers" : modifiers,
                                  "plot" : False})
        
        return returnStrings # returns

    # Function to handle the actual roll logic and returns it to be passed to user
    async def getAndSendResultMessage(self, ctx):
        allRolls = [] # array of dictionaries for the roll results
        
        # goes through each roll in self.rolls
        for roll in self.getRolls():
            currentRolls = {} # variable to hold all rolls in current roll code
            # sets "code", the visual roll command. EX: a1d20+4
            # there is logic to handle 0 modifiers
            currentRolls["code"] = f"""{roll["preCodes"]}{roll["numDice"]}d{roll["numSides"]}{roll["modifiers"] if roll["modifiers"] < 0 else ("+" + str(roll["modifiers"]) if roll["modifiers"] > 0 else "")}"""
            currentRolls["preCodes"] = roll["preCodes"] # sets "preCodes", a or d for advantage or disadvantage
            currentRolls["plot"] = roll["plot"] # sets "plot", a bool that indicates if it's a plot die or not

            # checks if there are precodes
            if roll["preCodes"] == "": # if not, roll each die and build a total, set both
                currentRolls["roll"] = self.roll(roll)
                currentRolls["total"] = sum(currentRolls["roll"]) + roll["modifiers"]
            else: # if there's a precode, roll for each die including extra dice for each precode
                currentRolls["roll"] = self.roll({"numDice": roll["numDice"] + len(roll["preCodes"]), "numSides": roll["numSides"]})
                
                # variables to process rolls with advantage and/or disadvantage
                # will change preCodes and roll, which is why we use temp variables
                testCodes = roll["preCodes"]
                testRolls = currentRolls["roll"]
                currentRolls["total"] = 0

                # loops while there are still preCodes to check in testCodes
                while len(testCodes) > 0:
                    if testCodes[0] == "a": # if 'a', adds the max of the first 2 rolls in testRolls
                                            # then, removes the first char in testCodes and first
                                            # ints in testRolls to prep for the next check
                        currentRolls["total"] += max(testRolls[0], testRolls[1])
                        testCodes = testCodes[1:]
                        testRolls = testRolls[2:]
                    else: # does the same, but for 'd', so takes the min
                        currentRolls["total"] += min(testRolls[0], testRolls[1])
                        testCodes = testCodes[1:]
                        testRolls = testRolls[2:]
                
                # if there are still rolls to process, do so and add modifiers
                if len(testRolls) > 0:
                    currentRolls["total"] += sum(testRolls) + roll["modifiers"]
                else: # otherwise, add modifiers
                    currentRolls["total"] += roll["modifiers"]
                
                if roll["plot"] == True:
                    currentRolls["preCodes"] += "Plot"

            allRolls.append(currentRolls) # add to allRolls

        # Builds the return message so the bot can communicate results
        message = f"""{ctx.author.mention}\n**Rolling:**\n* """ # begins message
            
        # loops through allRolls to add them to message for printing
        for index, roll in enumerate(allRolls):
            if index == len(allRolls) - 1: # checks if it's the last roll in the array
                if roll["plot"] == True: # checks if it's a plot die and displays that
                    if roll["preCodes"] != "":
                        message += f"{roll["preCodes"]}, \n**Results:**\n"
                    else:
                        message += "Plot, \n**Results:**\n"
                else: # else, adds the current roll's "code" and ends this portion of the message
                    message += roll["code"] + "\n**Results:**\n"
            else: # handles if there's more dice to check
                if roll["plot"] == True: # checks if it's a plot die and displays that
                    
                    # checks for and processes possible preCodes
                    if roll["preCodes"] != "":
                        message += f"{roll["preCodes"]}, "
                    else:
                        message += "Plot, "
                else: # if not plot, simply includes the "code"
                    message += roll["code"] + ", "

        # will loop through allRolls and display results
        for roll in allRolls:
            # checks for and processes precodes
            if roll["preCodes"] == "": # builds and adds rolls (without preCodes) and results to message
                message += f"""> =**{"Plot" if roll["plot"] else str(roll["code"])}**==[**{"**][**".join(map(str, roll["roll"]))}**]==**{{{str(roll["total"])}}}**\n"""
            else: # handles rolls with preCodes
                # variables to process rolls with advantage and/or disadvantage
                # will change preCodes and roll, which is why we use temp variables
                testCodes = roll["preCodes"]
                testRolls = roll["roll"]

                # sets up the start of the message
                message += f"> =**{testCodes if roll["plot"] == True else str(roll["code"])}**=="

                # loops while there are still preCodes to check in testCodes
                while len(testCodes) > 0:
                    if testCodes[0] == "a": # if 'a', marks kept die in first 2 rolls in testRolls
                                            # then, removes the first char in testCodes and first
                                            # ints in testRolls to prep for the next check
                        if testRolls[0] >= testRolls[1]:
                            message += f"[**{testRolls[0]}**][~~{testRolls[1]}~~]"
                        else:
                            message += f"[~~{testRolls[0]}~~][**{testRolls[1]}**]"
                        testCodes = testCodes[1:]
                        testRolls = testRolls[2:]
                    elif testCodes[0] == "d": # does the same, but for 'd', so takes the mins
                        if testRolls[0] < testRolls[1]:
                            message += f"[**{testRolls[0]}**][~~{testRolls[1]}~~]"
                        else:
                            message += f"[~~{testRolls[0]}~~][**{testRolls[1]}**]"
                        testCodes = testCodes[1:]
                        testRolls = testRolls[2:]
                    else:
                        break
                
                # if there are still rolls to process, do so and add modifiers
                if len(testRolls) > 0:
                    message += f"[**{"**][**".join(map(str, testRolls))}**]==**{{ {str(roll["total"])} }}**\n"
                else: # otherwise, add modifiers
                    message += f"==**{{ {str(roll["total"])} }}**\n"

        await ctx.send(message) # sends message via discord
                   