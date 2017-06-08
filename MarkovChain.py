"""
Tabletop Game Simulator
@author: Brandon Rolston
"""
import numpy as np

"""
These are the variables for player stats
"""

# Health
Char1HP = 20
Char2HP = 21

# Armor Class (Average value is 10)
Char1AC = 11
Char2AC = 11

# Attack
Char1AT = 4
Char2AT = 4


"""
Create the "player" vector and the chain
"""
if Char1HP >= Char2HP:
    chainSize = Char1HP*Char1HP*2+2
    playerState = np.zeros(chainSize)
    playerState[(Char1HP-Char2HP)] = 1
    firstPosition = (Char1HP*Char1HP)
    chain = np.zeros((chainSize,chainSize))
    maxHP = Char1HP
else:
    chainSize = Char2HP*Char2HP*2+2
    playerState = np.zeros(chainSize)
    playerState[(Char2HP-Char1HP)*Char2HP] = 1
    firstPosition = (Char2HP*Char2HP)
    chain = np.zeros((chainSize,chainSize))
    maxHP = Char2HP

# Simulated Rounds (This value needs to be higher than approximately the higher of the two HPs squared to get a fair result)
Rounds = maxHP*10
"""
Fill the markov chain with the appropriate values
"""

ChanceToMiss1 = (Char1AC-1)/20  #Chance that player 2 misses player 1
ChanceToMiss2 = (Char2AC-1)/20  #Chance that player 1 misses player 2
Damage1 = (1-ChanceToMiss1)/Char2AT #Transitions from taking damage from player 1
Damage2 = (1-ChanceToMiss2)/Char1AT #Transitions from taking damage from player 2

# More friendly name for keeping tabs on where in the chain values are being placed
positionTracker1 = maxHP*maxHP
positionTracker2 = positionTracker1

# Add the "miss" states for player 1
for i in range(positionTracker1):
    chain[firstPosition+i,i] = ChanceToMiss2

# Add the "miss" states for player 2
for i in range(positionTracker2):
    chain[i,maxHP*maxHP+i] = ChanceToMiss1

# Put in the victory states
chain[chainSize-1,chainSize-1] = 1
chain[chainSize-2,chainSize-2] = 1

# Generate the "hit" states for player1
# This generates the shape needed for the chain
r=[]
for i in range(maxHP):
    for j in range(maxHP):
        r.extend([j])
r = r[::-1]
# Position Variables
shift = 0
vert = 1
for i in range(maxHP):
    for j in range(maxHP):
        if r[j+shift] >= Char1AT:
            for x in range(Char1AT):
                chain[firstPosition+vert+j+x,j+shift] = Damage2
        else:
            for x in range(r[j+shift]):
                chain[firstPosition+vert+j+x,j+shift] = Damage2
    shift = maxHP * (i+1)
    vert = vert+maxHP

# Generate the "hit" states for player2
# A new 'r' is needed here
q = []
for i in range(maxHP):
    for j in range(maxHP):
        q.extend([maxHP-i-1])

vert = 1
for i in range(positionTracker2):
    if q[i] >= Char2AT:
        for x in range(Char2AT):
            chain[(i+(1+x)*maxHP,positionTracker2+i)] = Damage1
    else:
        for x in range(q[i]):
            chain[(i+(1+x)*maxHP,positionTracker2+i)] = Damage1
        vert = vert + maxHP 
   
# Generate the victory conditions for Player 1
r = []
startingPoint = maxHP - Char1AT
for i in range(maxHP):
    for j in range(maxHP):
        if j < startingPoint:
            r.extend([0])
        else:
            r.extend([(j-startingPoint+1)*Damage2])

for i in range(positionTracker1):
    chain[chainSize-2,i] = r[i]
    
# Generate the victory conditions for Player 2
r = []
startingPoint = maxHP - Char2AT
for i in range(maxHP):
    for j in range(maxHP):
        if i < startingPoint:
            r.extend([0])
        else:
            r.extend([(i-startingPoint+1)*Damage1])

for i in range(positionTracker1):
    chain[chainSize-1,i+maxHP*maxHP] = r[i]
    
"""
The chain is generated, let's do some math to it!
"""
# Needed for the code, also the odds that a player wins in the first round
P = chain@playerState

#What happens after 5000 rounds? (It'll be the most likely victors)
for x in range(Rounds):
    P = chain@P

print("Player 1 wins", P[chainSize-2], "Percent of the time.")
print("Player 2 wins", P[chainSize-1], "Percent of the time.")

# Comment out the next line if you wish to save the chain to a format viewable in Excel
#np.savetxt('The_Chain.txt', chain, delimiter=',')    