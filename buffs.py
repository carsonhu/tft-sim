from collections import deque, Counter
from items import Item
import status
class Buff(Item):
    def __init__(self, name, level, params, phases):
        super().__init__(name, phases = phases)
        self.level = level
        self.params = params

    def performAbility(self, phase, time, champion, input=0):
        raise NotImplementedError("Please Implement this method")       

    def ability(self, phase, time, champion, input=0):
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input)
        return input

class NoBuff(Buff):
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("NoItem", level, params, phases=None)

    def performAbility(self, phase, time, champion, input=0):
        return 0

class Forgotten(Buff):
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Forgotten " + str(level), level, params, phases=["preCombat"])
        self.scaling = {3: (30, 30), 6: (70, 70), 9: (140, 140)}
        self.stacks = min(params, 4)

    def performAbility(self, phase, time, champion, input=0):
        champion.atk.add+= self.scaling[self.level][0]*self.stacks*1.1
        champion.ap.add+= self.scaling[self.level][1]*self.stacks*1.1
        return 0

class VayneBolts(Buff):
    def __init__(self, level=0, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Silver Bolts", level, params, phases=["onAttack"])



    def performAbility(self, phase, time, champion, input=0):
        # input is opponent
        input.applyStatus(status.SilverBolts(), champion, time, 999, "")
        return 0

class VarusBolts(Buff):
    def __init__(self, level=0, params=0):
        super().__init__("Varus Arrows", level, params, phases=["onAttack"])
    def performAbility(self, phase, time, champion, input=0):
        # input is opponent
        if champion.boltsActive:
            champion.onHitSpell(input, champion.items, time, champion.getStacks, 'magical')        
        return 0



class YasuoStacks(Buff):
    def __init__(self, level=0, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Burning Blade", level, params, phases=["onAttack"])
    def performAbility(self, phase, time, champion, input=0):
        # input is opponent
        champion.onHitSpell(input, champion.items, time, champion.getStacks, 'true')        
        return 0

class DravenAxes(Buff):
    def __init__(self, level=0, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Spinning Axes", level, params, phases=["onUpdate"])
    def performAbility(self, phase, time, champion, input=0):
        # input is opponent
        if champion.axeQueue and time > champion.axeQueue[-1]:
            champion.axes = min(champion.axes + 1, 2)
            champion.axeQueue.pop()
        return 0


class Legionnaire(Buff):
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Legionnaire " + str(level), level, params, phases=["preCombat"])
        self.scaling = {2: 25, 4: 60, 6: 110, 8: 180}

    def performAbility(self, phase, time, champion, input=0):
        champion.aspd.add += self.scaling[self.level]
        return 0


class  Ranger(Buff):
    def __init__(self, level, params):
        # params is the time you get the stacks
        super().__init__("Ranger" + str(level), level, params, phases=["onUpdate"])
        self.baseBuff = {2: 70, 4: 180}
        self.lastSecond = 4

    def performAbility(self, phase, time, champion, input=0):
        if phase == "onUpdate":
            if time > self.lastSecond:
                self.lastSecond += 8
                champion.applyStatus(status.ASModifier(4), champion, time, 4, self.baseBuff[self.level])
        return 0

class Redeemed(Buff):
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Redeemed " + str(level), level, params, phases=["preCombat"])
        self.scaling = {3: 30, 6: 30, 9: 30}

    def performAbility(self, phase, time, champion, input=0):
        champion.ap.add+= self.scaling[self.level]
        return 0

class Invoker(Buff):
    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("Invoker " + str(level), level, params, phases=["preCombat"])
        self.scaling = {2: 3, 4: 6}

    def performAbility(self, phase, time, champion, input=0):
        champion.manaPerAttack.add += self.scaling[self.level]
        return 0


class Spellweaver(Buff):
    def __init__(self, level, params):
        # params is the time you get the stacks
        super().__init__("Spellweaver" + str(level), level, params, phases=["preCombat", "onUpdate"])
        self.baseBuff = {2: 20, 4: 50}
        self.stackingBuff = {2: 2, 4: 5}
        self.stacks = 0
        self.maxStacks = 10
        self.timeQueue = params


    def performAbility(self, phase, time, champion, input=0):
        if phase == "preCombat":
            champion.ap.add+= self.baseBuff[self.level]
        elif phase == "onUpdate":
            if self.timeQueue and time > self.timeQueue[0] and self.stacks < self.maxStacks:
                self.timeQueue.pop(0)
                champion.ap.add += self.stackingBuff[self.level]
                self.stacks += 1
        return 0



class Skirmisher(Buff):
    def __init__(self, level, params):
        # params is the time you get the stacks
        super().__init__("Skirmisher" + str(level), level, params, phases=["onUpdate"])
        self.baseBuff = {3: 3, 6: 6}
        self.lastSecond = 0

    def performAbility(self, phase, time, champion, input=0):
        if phase == "onUpdate":
            if time > self.lastSecond:
                self.lastSecond += 1
                champion.atk.add += self.baseBuff[self.level]
        return 0