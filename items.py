from collections import deque
import status
from champion import Stat
class Item(object):
    def __init__(self, name, hp=0, ad=0, ap=0, 
                 aspd=0, armor=0, mr=0, crit=0,
                 dodge=0, mana=0, phases=None):
        self.name = name
        self.hp = hp
        self.ad = ad
        self.ap = ap
        self.aspd = aspd
        self.armor = armor
        self.mr = mr
        self.crit = crit
        self.dodge = dodge
        self.mana = mana
        self.phases = phases

    def performAbility(self, phases, time, champion, input=0):
        raise NotImplementedError("Please Implement this method")       

    def ability(self, phase, time, champion, input=0):
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input)
        return input

class GA(Item):
    def __init__(self):
        super().__init__("Guardian Angel", ad=10, armor=20, phases=None)


class NoItem(Item):
    def __init__(self):
        super().__init__("NoItem", phases=None)

class Rab(Item):
    def __init__(self):
        super().__init__("Rabadon's Deathcap", ap=70, phases=None)


class Rageblade(Item):
    def __init__(self):
        super().__init__("Guinsoo's Rageblade", aspd=15, ap=10, phases=["postAttack"])

    def performAbility(self, phase, time, champion, input=0):
        if champion.aspd.stat <= 5:
            champion.aspd.add += 6
        return 0

class cursedRageblade(Item):
    def __init__(self):
        super().__init__("Guinsoo's Sacrificial Rageblade", aspd=15, ap=10, phases=["postAttack"])

    def performAbility(self, phase, time, champion, input=0):
        if champion.aspd.stat <= 5:
            champion.aspd.add += 9
        return 0

class Archangels(Item):
    def __init__(self):
        super().__init__("Archangels", mana=15, ap=10, phases=["preAbility"])

    def performAbility(self, phase, time, champion, input=0):
        champion.ap.add += champion.fullMana * .45
        return 0

class HoJ(Item):
    def __init__(self):
        super().__init__("Hand of Justice", mana=10, crit=.15, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input=0):
        champion.atk.add += 45
        champion.ap.add += 45
        return 0

class IE(Item):
    def __init__(self):
        super().__init__("Infinity Edge", ad=10, crit=0, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input=0):
        if not champion.ie:
            champion.ie = True
            champion.crit.add += .75
        return 0

class CursedIE(Item):
    def __init__(self):
        super().__init__("Infinity Edge", ad=10, crit=0.75, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input=0):
        champion.ie = True
        return 0

class LW(Item):
    def __init__(self):
        super().__init__("Last Whisper", aspd=0.1, crit=0.15, phases=["onCrit"])

    def performAbility(self, phase, time, champion, target):
        # change this to debuff later
        target.armor.mult = .3
        return 0

class FW(Item):
    def __init__(self):
        super().__init__("Final Whisper", aspd=0.1, crit=0.15, phases=["onCrit"])

    def performAbility(self, phase, time, champion, target):
        # change this to debuff later
        target.armor.mult = .3
        target.armor.mult = .3
        return 0


class Shojin(Item):
    def __init__(self):
        super().__init__("Spear of Shojin", ad=10, mana=15, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input=0):
        champion.manaPerAttack.add += 8
        return 0

class cursedShojin(Item):
    def __init__(self):
        super().__init__("Spectral Spear of Shojin", ad=10, mana=15, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input=0):
        champion.manaPerAttack.add += 14
        champion.dmgMultiplier.add -= 0.15
        return 0

class RH(Item):
    def __init__(self):
        super().__init__("Runaan's Hurricane", aspd=.1, phases="preAttack")

    def performAbility(self, phase, time, champion, input=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        if len(champion.opponents) > 1:
            champion.doAttack(champion.opponents[1], champion.items, time, multiplier=Stat(0, 0.75, 0))
        return 0
class cursedRH(Item):
    def __init__(self):
        super().__init__("Runaan's Untamed Hurricane", aspd=.1, phases="preAttack")

    def performAbility(self, phase, time, champion, input=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        if len(champion.opponents) > 1:
            champion.doAttack(champion.opponents[1], [], time, multiplier=Stat(0, 0.5, 0))
        if len(champion.opponents) > 2:
            champion.doAttack(champion.opponents[2], [], time, multiplier=Stat(0, 0.5, 0))
        return 0


class DB(Item):
    def __init__(self, DBqueue):
        super().__init__("Deathblade", ad=60, phases="onUpdate")
        self.DBqueue = DBqueue

    def performAbility(self, phase, time, champion, input=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        if self.DBqueue and self.DBqueue[0] < time:
            self.DBqueue.pop(0)
            champion.atk.add += 10
        return 0

class cursedDB(Item):
    def __init__(self, DBqueue):
        super().__init__("Deathblade", ad=80, phases="preAttack")
        self.DBqueue = DBqueue

    def performAbility(self, phase, time, champion, input=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        if self.DBqueue and self.DBqueue[0] < time:
            self.DBqueue.pop(0)
            champion.atk += 15
            print(champion.atk)
        return 0

class cursedJG(Item):
    def __init__(self):
        super().__init__("Sacrificial Gauntlet", crit=0.35, ap=10, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input=0):
        champion.canSpellCrit = True
        champion.critDmg.add += 0.4
        return 0

class JG(Item):
    def __init__(self):
        super().__init__("Jeweled Gauntlet", crit=0.15, ap=10, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input=0):
        champion.canSpellCrit = True
        champion.critDmg.add += 0.4
        return 0

class RFC(Item):
    def __init__(self):
        super().__init__("Rapid Firecannon", aspd=40, phases=None)

class Shiv(Item):
    def __init__(self):
        super().__init__("Statikk Shiv", aspd=10, mana=15, phases=["preAttack"])
        self.shivDmg = 70
        self.shivTargets = 4
        self.counter = 0

    def performAbility(self, phase, time, champion, input=0):
        # here, we'll just preset certain times where you get the deathblade stacks.
        self.counter += 1
        if self.counter == 3:
            self.counter = 0
            baseDmg = self.shivDmg
            for opponent in champion.opponents[0:self.shivTargets]:
                champion.doDamage(opponent, [], 0, baseDmg, baseDmg,'magical', time)
                opponent.applyStatus(status.MRReduction(6), champion, time, 6, .5)
        return 0

class cursedShiv(Item):
    def __init__(self):
        super().__init__("Statikk Stiletto", aspd=10, mana=15, phases=["preCombat", "preAttack"])
        self.shivDmg = 70
        self.shivTargets = 4
        self.counter = 0

    def performAbility(self, phase, time, champion, input=0):
        if phase == "preCombat":
            champion.atk.mult -= 1/3
        if phase == "preAttack":
            self.counter += 1
            if self.counter == 2:
                self.counter = 0
                baseDmg = self.shivDmg
                for opponent in champion.opponents[0:self.shivTargets]:
                    champion.doDamage(opponent, [], 0, baseDmg, baseDmg,'magical', time)
                    opponent.applyStatus(status.MRReduction(6), champion, time, 6, .5)
        return 0        
class GS(Item):
    # needs reworking
    def __init__(self):
        super().__init__("Giant Slayer", aspd=10, ad=10, phases="preCombat")

    def performAbility(self, phase, time, champion, input):
        # input is target
        vsGiants = True
        if vsGiants:
            champion.dmgMultiplier += .7
        else:
            champion.dmgMultiplier += .1
        return 0

class cursedGS(Item):
    # needs reworking
    def __init__(self):
        super().__init__("Spectral Giant Slayer", aspd=10, ad=10, phases="preCombat")

    def performAbility(self, phase, time, champion, input):
        # input is target
        vsGiants = True
        if vsGiants:
            champion.dmgMultiplier.add += .5
        return 0

class MageCap(Item):
    def __init__(self):
        super().__init__("Mage Cap", mana=15, phases="preCombat")

    def performAbility(self, phase, time, champion, input=0):
        champion.abilityDamage *= 2
        champion.APMultiplier = 1.6
        return 0

class Zekes(Item):
    def __init__(self):
        super().__init__("Zekes Herald", aspd = 30, phases=None)

class cursedZekes(Item):
    def __init__(self):
        super().__init__("Zeke's Bleak Herald", aspd = 80, ad = 10, phases=None)


class Chalice(Item):
    def __init__(self):
        super().__init__("Chalice of Harmony", ap = 30, phases=None)


class Blue(Item):
    def __init__(self):
        super().__init__("Blue Buff", mana=30, phases="preCombat")

    def performAbility(self, phase, time, champion, input=0):
        champion.startingMana = 20
        return 0
