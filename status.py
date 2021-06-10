
class Status(object):
    """Holds champion status effects:
    1. name
    2. wearoff time
    3. application effect
    4. wearoff effect
    """
    def __init__(self, name, wearoff_time):
        self.wearoff_time = wearoff_time
        self.name = name
        self.active = False
        self.opponent = None 
    def application(self, champion, opponent, time, duration, params):
        # opponent applies the status
        self.opponent = opponent

        self.active = True
        self.wearoff_time = time + duration
        self.applicationEffect(champion, time, duration, params)

    def applicationEffect(self, champion, time, duration, params):
        return 0

    def reapplication(self, champion, opponent, time, duration, params):
        self.opponent = opponent
        if self.reapplicationEffect(champion, time, duration, params):
            self.wearoff_time = time + duration

    def reapplicationEffect(self, champion, time, duration, params):
        return 0

    def wearoff(self, champion, time):
        self.wearoffEffect(champion, time)
        self.active = False
        self.opponent = None


    def wearoffEffect(self, champion, time):
        return 0

    def update(self, champion, time):
        if time > self.wearoff_time and self.active:
            self.wearoff(champion, time)

        #if status not in dict, put it in
        # applyeeffect: if inactive, application
        # else, reapplication

class VarusBolts(Status):
    def __init__(self, wearoff_time):
        super().__init__("Varus Bolt", wearoff_time=wearoff_time)
    def applicationEffect(self, champion, time, duration, params):
        return True
    def reapplicationEffect(self, champion, time, duration, params):
        return True
    def wearoffEffect(self, champion, time):
        return True


class SilverBolts(Status):
    def __init__(self, wearoff_time=999):
        super().__init__("Silver Bolt", wearoff_time=wearoff_time)
        self.stacks = 0
    def applicationEffect(self, champion, time, duration, params):
        self.stacks += 1
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        self.stacks += 1
        if self.stacks == 3:
            self.opponent.performAbility([champion], self.opponent.items, time)
            self.stacks = 0
        return True
    def wearoffEffect(self, champion, time):
        print("shouldnt be wearing off")
        self.stacks = 0
        return True

class ADModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, wearoff_time):
        super().__init__("AD Modifier", wearoff_time=wearoff_time)
        self.addition = 1
        self.mult = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.atk.add += params.add
        champion.atk.add += params.mult
        self.addition = params.add
        self.mult = params.mult
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        champion.atk.add  -= self.addition
        champion.atk.add  -= self.mult
        return True


class ASModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, wearoff_time):
        super().__init__("AS Modifier", wearoff_time=wearoff_time)
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.add += params
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True
    def wearoffEffect(self, champion, time):
        champion.aspd.add  -= self.addition
        return True


class MRReduction(Status):
    # reduce MR by N%
    def __init__(self, wearoff_time):
        super().__init__("MR Reduction", wearoff_time=wearoff_time)
        self.reduction = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.mr.mult = min(champion.mr.mult, params)
        self.reduction = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        if self.reduction >= params:
            champion.mr.mult = min(champion.mr.mult, self.reduction)
            return True
        else:
            # if it's weaker, doesnt work
            return False
    def wearoffEffect(self, champion, time):
        champion.mr.mult = 1
        return True
