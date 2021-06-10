import random
import status
# class Status(object):
#     """Holds champion status effects
#     """
#     def __init__(self):
#         self.vayneBolts = 0
#         self.divineActive = False

class Stat(object):
    def __init__(self, base, multModifier, addModifier):
        self.base = base
        self.mult = multModifier
        self.add = addModifier

    @property
    def stat(self):
        # ad: (base + add)* mult
        # i.e 15% AS is base AS * .15
        return self.mult * (self.base + self.add)
class Aspd(Stat):
    def __init__(self, base, multModifier, addModifier):
        super().__init__(base, multModifier, addModifier)

    @property
    def stat(self):
        return min(self.base * (1 + self.add/100), 5)

class AP(Stat):
    def __init__(self, base, multModifier, addModifier):
        super().__init__(base, multModifier, addModifier)

    @property
    def stat(self):
        return self.mult * (self.base + self.add / 100)


class Champion(object):
    def __init__(self, name, hp, atk, curMana, fullMana, aspd, armor, mr, level):
        self.name = name
        levels = [1, 1.8, 1.8**2, 1.8**3]
        self.hp = Stat(hp * levels[level - 1], 1, 0)
        self.atk = Stat(atk * levels[level - 1], 1, 0)
        self.curMana = curMana
        self.fullMana = fullMana
        self.startingMana = 0
        self.aspd = Aspd(aspd, 1, 0)
        self.ap = AP(0, 1, 0)
        self.armor = Stat(armor, 1, 0)
        self.mr = Stat(mr, 1, 0)
        self.manaPerAttack = Stat(10, 1, 0)
        self.level = level
        self.ability = ""
        self.dmgMultiplier = Stat(1, 1, 0)
        self.crit = Stat(.25, 1, 0)
        self.critDmg = Stat(1.3, 1, 0)
        self.canCrit = True
        self.canSpellCrit = False
        self.dodge = Stat(0, 1, 0)
        self.manalockTime = -1
        self.manalockDuration = 1
        self.castTime = 0
        self.items = []
        self.status = {}
        self.nextAttackTime = 0
        self.opponents = []
        self.dmgVector = []
        self.alive = True
        self.ie = False

        self.numAttacks = 0
        self.numCasts = 0

    def applyStatus(self, status, champion, time, duration, params):
        if status.name not in self.status:
            self.status[status.name] = status
            self.status[status.name].application(self, champion, time, duration, params)
        else:
            if not self.status[status.name].active:
                self.status[status.name].application(self, champion, time, duration, params)
            else:
                self.status[status.name].reapplication(self, champion,  time, duration, params)

    # get basic stats from items
    def addStats(self,item):
        self.hp.add += item.hp
        self.atk.add += item.ad
        self.ap.add += item.ap
        self.aspd.add += item.aspd
        self.curMana = min(self.curMana + item.mana, self.fullMana)
        self.armor.add += item.armor
        self.mr.add += item.mr
        self.crit.add += item.crit
        self.dodge.add += item.dodge

    def canCast(self, time):
        return self.curMana >= self.fullMana and self.fullMana > 0 and self.manalockTime <= time

    def canAttack(self, time):
        return time > self.nextAttackTime

    def abilityScaling(self, level):
        return 0

    def __str__(self):
        return ','.join( (str(p) for p in (self.hp.stat, self.atk.stat, self.aspd.stat, self.ap.stat)))

    def attackTime(self):
        return 1 / self.aspd.stat

    def performAttack(self, opponents, items, time, multiplier=Stat(0,1,0)):
        for item in items:
            item.ability("preAttack", time, self)
        # doAttack
        self.doAttack(opponents[0], items, time, multiplier)
        if self.manalockTime <= time + 0.1 : # there's some wiggle room since u get mana while it's in the air
            self.curMana += self.manaPerAttack.stat
        for item in items:
            item.ability("postAttack", time, self)
    
    def performAbility(self, opponents, items, time):
        return 0

    def update(self, opponents, items, time):
        for status in self.status.values():
            status.update(self, time)

        for item in items:
            item.ability("onUpdate", time, self)
        # dmg = []
        if self.canAttack(time):
            self.opponents = opponents
            if opponents:
                self.numAttacks += 1
                self.performAttack(opponents, items, time)
                self.nextAttackTime += self.attackTime()
        if self.canCast(time):
            self.numCasts += 1
            self.performAbility(opponents, items, time)
            for item in items:
                item.ability("postAbility", time, self)
            self.manalockTime = time + self.manalockDuration
            self.curMana = self.startingMana
            # self.nextAttackTime = time + self.attackTime() + self.castTime
            self.nextAttackTime = max(time + self.attackTime(), time + self.castTime)    
        
    def baseAtkDamage(self, multiplier):
        return (self.atk.stat + multiplier.add) * multiplier.mult

    def doAttack(self, opponent, items, time, multiplier=Stat(0,1,0)):
        for item in items:
            item.ability("onAttack", time, self, opponent)
        baseDmg = self.baseAtkDamage(multiplier)
        baseCritDmg = baseDmg
        for item in items:
            item.ability("onCrit", time, self, opponent)
        baseCritDmg *= self.critDamage()
        baseDmg *= self.dmgMultiplier.stat
        baseCritDmg *= self.dmgMultiplier.stat
        # print(baseCritDmg/baseDmg)
        self.doDamage(opponent, items, self.crit.stat, baseCritDmg, baseDmg,'physical', time)

    #def ability()

    def critDamage(self):
        if not self.ie:
            return self.critDmg.stat
        else:
            return (self.crit.stat - 1) + self.critDmg.stat


    def doDamage(self, opponent, items, critChance, damageIfCrit, damage, dtype, time):
        # actually doing damage
        critChance = min(1, critChance)
        preDmg = damage
        preCritDmg = damageIfCrit
        for item in items:
            preDmg = item.ability("onDoDamage", time, self, preDmg)
            preCritDmg = item.ability("onDoDamage", time, self, preCritDmg)
        dmg = self.damage(preDmg, dtype, opponent)
        critDmg = self.damage(preCritDmg, dtype, opponent)
        # print(damageIfCrit/damage)
        avgDmg = (dmg[0] * (1 - critChance) + critDmg[0] * critChance, dmg[1])
        if avgDmg:
            self.dmgVector.append((time,avgDmg))

    # def singleTargetSpell(self, opponents, items, time, scaling):
    #     for item in items:
    #         item.ability("preAbility", time, self)
    #     baseDmg = self.abilityScaling(self.level) * (1 + self.ap.stat)
    #     if random.random() < self.crit.stat and self.canSpellCrit:
    #         baseDmg *= self.critDamage()
    #     baseDmg *= self.dmgMultiplier.stat
    #     self.manalockTime = time + 1
    #     self.curMana = self.startingMana
    #     return self.doDamage(opponents[0], items, baseDmg, 'magical', time)

    def multiTargetAttack(self, opponents, items, time, targets, scaling, type='physical'):
        
        for item in items:
            item.ability("preAbility", time, self)
        baseDmg = scaling(self.level, self.atk.stat, self.ap.stat)
        baseCritDmg = baseDmg
        if self.canSpellCrit:
            baseCritDmg *= self.critDamage()
        baseDmg *= self.dmgMultiplier.stat
        baseCritDmg *= self.dmgMultiplier.stat
        for opponent in opponents[0:targets]:
            self.doDamage(opponent, items, self.crit.stat, baseCritDmg, baseDmg, type, time)

    def onHitSpell(self, opponent, items, time, scaling, type='magical'):
        # for archangels
        tempMana = self.fullMana
        self.fullMana = 0
        self.multiTargetSpell([opponent], items, time, 1, scaling, type)
        self.fullMana = tempMana

    def multiTargetSpell(self, opponents, items, time, targets, scaling, type='magical'):
        for item in items:
            item.ability("preAbility", time, self)
        baseDmg = scaling(self.level, self.atk.stat, self.ap.stat)
        baseCritDmg = baseDmg
        if self.canSpellCrit:
            baseCritDmg *= self.critDamage()
        baseDmg *= self.dmgMultiplier.stat
        baseCritDmg *= self.dmgMultiplier.stat
        for opponent in opponents[0:targets]:
            self.doDamage(opponent, items, self.crit.stat, baseCritDmg, baseDmg, type, time)
    

    def damage(self, dmg, dtype, defender):
        """deal dmg, dmg is premitigated
        
        Args:
            dmg (FLOAT): for basic attacks, it's just atk. sometimes 
            dtype (STRING): physical/magical/true
            defender (Champion): recipient
        """
        if dtype == "physical":
            defense = defender.armor.stat
        elif dtype == "magical":
            defense = defender.mr.stat
        elif dtype == "true":
            defense = 0

        dModifier = 100 / (100 + defense)
        return (dmg * dModifier, dtype)
        