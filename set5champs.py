from champion import Champion, Stat
from collections import deque
import random
import buffs
import status
class Aphelios(Champion):
    def __init__(self, level):
        hp = 650
        atk = 75
        curMana = 10
        fullMana = 90
        aspd = .85
        armor = 25
        mr = 25
        super().__init__('Aphelios', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5

    def abilityScaling(self, level, AD, AP):
        adPercent = [1.4,1.5, 1.8]
        abilityScale = [150, 200, 400]
        return abilityScale[level-1] * (1+AP) + adPercent[level-1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetAttack(opponents, items, time, 4, self.abilityScaling)

class DummyTank(Champion):
    def __init__(self, level):
        hp = 650
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = .85
        armor = 100
        mr = 100
        super().__init__('Tank', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5

    def abilityScaling(self, level, AD, AP):
        adPercent = [1.4,1.5, 1.8]
        abilityScale = [100, 150, 300]
        return abilityScale[level-1] * (1+AP) + adPercent[level-1] * AD

    def performAbility(self, opponents, items, time):
        return 0

class Jax(Champion):
    def __init__(self, level):
        hp = 900
        atk = 80
        curMana = 0
        fullMana = 20
        aspd = .85
        armor = 50
        mr = 50
        super().__init__('Jax', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0

    def abilityScaling(self, level, AD, AP):
        adPercent = [2, 2.2, 3]
        return adPercent[level-1] * AD

    def asBonus(self):
        asScaling = [30,35,100]
        self.aspd.add += asScaling[self.level - 1] * (1+self.ap.stat)

    def performAbility(self, opponents, items, time):
        # self.castTime = self.aspd.stat
        self.multiTargetAttack(opponents, items, time, 1, self.abilityScaling)
        self.asBonus()

class Pantheon(Champion):
    def __init__(self, level):
        hp = 800
        atk = 75
        curMana = 30
        fullMana = 60
        aspd = .75
        armor = 45
        mr = 45
        super().__init__('Pantheon', hp, atk, curMana, fullMana, aspd, armor, mr, level)

    def abilityScaling(self, level, AD, AP):
        adPercent = [3,5, 4, 4.5]
        return adPercent[level-1] * AD

    def asBonus(self):
        asScaling = [30,35,50]
        self.aspd.add += asScaling[self.level - 1] * self.ap.stat

    def performAbility(self, opponents, items, time):
        self.multiTargetAttack(opponents, items, time, 1, self.abilityScaling)
        self.asBonus()



class Kalista(Champion):
    def __init__(self, level):
        hp = 500
        atk = 60
        curMana = 0
        fullMana = 120
        aspd = .75
        armor = 15
        mr = 15
        super().__init__('Kalista', hp, atk, curMana, fullMana, aspd, armor, mr, level)

    def abilityScaling(self, level, AD, AP):
        adPercent = [1.8,2, 2.4]
        abilityScale = [350, 600, 1000]
        return adPercent[level-1] * (1+AP) * AD + abilityScale[level-1]

    def performAbility(self, opponents, items, time):
        self.multiTargetAttack(opponents, items, time, 1, self.abilityScaling)

class Draven(Champion):
    def __init__(self, level):
        hp = 700
        atk = 90
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 30
        mr = 30
        self.axeReturnTime = 1

        super().__init__('Draven', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.axes = 0
        self.axeQueue = deque()
        self.castTime = 0
        self.items = [buffs.DravenAxes()]

    def abilityScaling(self, level, AD, AP):
        adPercent = [1.6,1.7, 3.4]
        abilityScale = [150, 200, 800]
        return adPercent[level-1] * AD + abilityScale[level-1] * (1 + AP)

    def performAbility(self, opponents, items, time):
        self.axeQueue.append(time + self.axeReturnTime)

    def consumeAxe(self, level, AD, AP, time):
        if self.axes > 0:
            self.axes -= 1
            adPercent = [1.8,2, 2.6]
            abilityScale = [150, 200, 500]
            self.performAbility([], [], time)
            return Stat(0, adPercent[level - 1], abilityScale[level - 1] * (1 + AP))
        else:
            return Stat(0, 1, 0)

    def performAttack(self, opponents, items, time, multiplier=Stat(0,1,0)):
            for item in items:
                item.ability("preAttack", time, self)
            multiplier = self.consumeAxe(self.level, self.atk.stat, self.ap.stat, time)
            # doAttack
            self.doAttack(opponents[0], items, time, multiplier)
            if self.manalockTime <= time:
                self.curMana += self.manaPerAttack.stat
            for item in items:
                item.ability("postAttack", time, self)

class Riven(Champion):
    def __init__(self, level):
        hp = 800
        atk = 90
        curMana = 0
        fullMana = 40
        aspd = .8
        armor = 35
        mr = 35
        super().__init__('Riven', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.manalockDuration = 8
        self.castTime = 0.3
  

    def abilityScaling(self, level, AD, AP):
        abilityScale = [100,200, 500]
        return abilityScale[self.level-1] * (1+AP)

    def adBonus(self, time):
        adScaling = [.9,1,1.5]
        self.applyStatus(status.ADModifier(8), self, time, 8, Stat(0,adScaling[self.level-1], 0))

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 2, self.abilityScaling)
        self.adBonus(time)

class Yasuo(Champion):
    def __init__(self, level):
        hp = 800
        atk = 60
        curMana = 0
        fullMana = 40
        aspd = 1
        armor = 35
        mr = 35
        super().__init__('Yasuo', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.stacks = 0
        self.items = [buffs.YasuoStacks()]
        self.castTime = 1

    def getStacks(self, level, AD, AP):
         return self.stacks

    def abilityScaling(self, level, AD, AP):
        abilityScale = [300,400, 750]
        return abilityScale[level-1] * (1+AP)

    def stackScaling(self, level, AD, AP):
        stackScale = [30, 40, 75]
        return stackScale[level-1] * (1+AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling)
        self.stacks += self.stackScaling(self.level, self.atk.stat, self.ap.stat)

class Udyr(Champion):
    def __init__(self, level):
        hp = 700
        atk = 55
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Udyr', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.tigerStance = False
        self.castTime = 0


    def abilityScaling(self, level, AD, AP):
        abilityScale = [1.2,1.3,1.8]
        return abilityScale[level-1] * AD * 3

    def performAbility(self, opponents, items, time):
        if self.tigerStance:
            self.multiTargetAttack(opponents, items, time, 1, self.abilityScaling)
            self.castTime = 0
            self.tigerStance = False
        else:
            self.tigerStance = True
            self.castTime = 0.5


class Viktor(Champion):
    def __init__(self, level):
        hp = 500
        atk = 55
        curMana = 30
        fullMana = 70
        aspd = .65
        armor = 20
        mr = 20
        super().__init__('Viktor', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5

    def abilityScaling(self, level, AD, AP):
        abilityScale = [300,500,850]
        return abilityScale[level-1] * (1+AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling)

class Vayne(Champion):
    def __init__(self, level):
        hp = 500
        atk = 30
        curMana = 0
        fullMana = 0
        aspd = .8
        armor = 15
        mr = 15
        super().__init__('Vayne', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.items.append(buffs.VayneBolts())
        # she gets an onattack buff
    def abilityScaling(self, level, AD, AP):

        abilityScale = [65, 90, 140]
        return abilityScale[level-1] * (1+AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, 'true')

class Varus(Champion):
    def __init__(self, level):
        hp = 550
        atk = 65
        curMana = 0
        fullMana = 60
        aspd = .8
        armor = 20
        mr = 20
        super().__init__('Varus', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.items.append(buffs.VarusBolts())
        self.boltsActive = False
        self.castTime = 0.5
        # he gets an onattack buff
    def abilityScaling(self, level, AD, AP):
        abilityScale = [1.5, 1.6, 1.8]
        return abilityScale[level-1] * (1 + AD)

    def getStacks(self, level, AD, AP):
        stackScale = [40, 60, 90]
        return stackScale[level-1] * (1+AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 3, self.abilityScaling, 'physical')
        # self.applyStatus(status.VarusBolts(6), self, time, 6, 0)
        self.boltsActive = True



class Karma(Champion):
    def __init__(self, level):
        hp = 700
        atk = 45
        curMana = 0
        fullMana = 50
        aspd = .7
        armor = 25
        mr = 25
        super().__init__('Karma', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.ultStacks = 0
        self.manalockDuration = 1.5
        self.castTime = 0.5

    def abilityScaling(self, level, AD, AP):
        abilityScale = [240, 300, 700]
        return abilityScale[level-1]*(1 + AP)

    def performAbility(self, opponents, items, time):
        if self.ultStacks != 3:
            self.multiTargetSpell(opponents, items, time, 2, self.abilityScaling)
        else:
            self.multiTargetSpell(opponents, items, time, 6, self.abilityScaling)
            self.ultStacks = 0
        self.fullMana = max(self.fullMana - 15, 10)
        self.ultStacks += 1
                

class Ryze(Champion):
    def __init__(self, level):
        hp = 800
        atk = 50
        curMana = 20
        fullMana = 50
        aspd = .75
        armor = 30
        mr = 30
        super().__init__('Ryze', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.ultStun = False

    def abilityScaling(self, level, AD, AP):
        abilityScale = [200, 250, 800]
        return abilityScale[level-1]*(1 + AP)

    def performAbility(self, opponents, items, time):
        if self.ultStun:
            self.multiTargetSpell(opponents, items, time, 4, self.abilityScaling)
            self.ultStun = False
        else:
            self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling)
            self.ultStun = True


class Syndra(Champion):
    def __init__(self, level):
        hp = 550
        atk = 40
        curMana = 50
        fullMana = 90
        aspd = .65
        armor = 20
        mr = 20
        super().__init__('Syndra', hp, atk, curMana, fullMana, aspd, armor, mr, level)

    def abilityScaling(self, level, AD, AP):
        abilityScale = [300, 400, 600]
        return abilityScale[level-1]*(1 + AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 2, self.abilityScaling)

class Ziggs(Champion):
    def __init__(self, level):
        hp = 500
        atk = 40
        curMana = 0
        fullMana = 40
        aspd = .75
        armor = 15
        mr = 15
        super().__init__('Ziggs', hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5

    def abilityScaling(self, level, AD, AP):
        abilityScale = [250, 350, 450]
        return abilityScale[level-1]*(1 + AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling)

class Zyra(Champion):
    def __init__(self, level):
        hp = 600
        atk = 40
        curMana = 60
        fullMana = 120
        aspd = .7  
        armor = 20
        mr = 20
        super().__init__('Zyra', hp, atk, curMana, fullMana, aspd, armor, mr, level)

    def abilityScaling(self, level, AD, AP):
        abilityScale = [250, 350, 600]
        return abilityScale[level-1]*(1 + AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 3, self.abilityScaling)

class Soraka(Champion):
    def __init__(self, level):
        hp = 550
        atk = 40
        curMana = 30
        fullMana = 70
        aspd = .6
        armor = 25
        mr = 25
        super().__init__('Soraka', hp, atk, curMana, fullMana, aspd, armor, mr, level)

    def abilityScaling(self, level):
        abilityScale = [150, 225, 350]
        return abilityScale[level-1]

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 2, self.abilityScaling)

class Lissandra(Champion):
    def __init__(self, level):
        hp = 550
        atk = 40
        curMana = 0
        fullMana = 50
        aspd = .65
        armor = 20
        mr = 20
        super().__init__('Soraka', hp, atk, curMana, fullMana, aspd, armor, mr, level)

    def abilityScaling(self, level):
        abilityScale = [250, 350, 450]
        return abilityScale[level-1]

    def abilityScaling2(self, level):
        abilityScale = [125, 175, 225, abilityScaling]
        return abilityScale[level-1]

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling)
        self.multiTargetSpell(opponents, items, time, 2, self.abilityScaling2)