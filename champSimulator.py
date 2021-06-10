import items
import matplotlib.pyplot as plt
import time
import copy
import csv
from collections import deque
from set5champs import *
import buffs
import numpy as np
import itertools
import xlsxwriter
class Simulator(object):
    def __init__(self):
        self.current_time = 0
        self.frameTime = 1/30

    def itemStats(self,items, champion):
        for item in items:
            champion.addStats(item)
        for item in items:
            item.ability("preCombat", 0, champion)
    def simulate(self, items, buffs, champion, opponents, duration):
        # there's no real distinction between items and buffs
        items = items + buffs + champion.items
        champion.items = items
        self.itemStats(items, champion)
        self.current_time = 0

        for opponent in opponents:
            opponent.nextAttackTime = duration * 2
        while self.current_time < duration:
            champion.update(opponents, items, self.current_time)
            for opponent in opponents:
                opponent.update(champion, [], self.current_time)
            self.current_time += self.frameTime
        return champion.dmgVector

# def plotSimulation(items, t):
#     simulator = Simulator()
#     results = simulator.simulate(items, [], aphelios, [aphelios], t)
#     itemNames = ','.join([item.name for item in items])
#     plt.plot(*zip(*results), label = itemNames)


def resNoDmg(res, label):
    a,b = zip(*[(result[0], result[1][0]) for result in res])
    b = np.cumsum(b)
    plt.plot(a,b, label=label)

def plotRes(res, label):
    plt.plot(res[0], res[1], label)

def getDPS(results, time):
    dpsSum = 0
    for result in results:
        if result[0] < time:
            dpsSum += result[1][0]
    return dpsSum / time

def dpsSplit(results):
    dps = {"physical": 0, "magical": 0, "true": 0}
    for result in results:
        dps[result[1][1]] += result[1][0]
    total = sum(dps.values(), 0.0)
    return {k: v / total for k, v in dps.items()}

def createDPSChart(simList):
    for sim in simList:
        dps5s = getDPS(sim[3], 5)
        dps10s = getDPS(sim[3], 10)
        dps15s = getDPS(sim[3], 15)
        print(sim[0].name, [u.name for u in sim[1]], [u.name for u in sim[2]], dps5s, dps10s, dps15s, dpsSplit(sim[3]))

        # we want DPS at 5s, DPS at 10s, DPS at 15
def createDPScsv(simLists):
    headers_arr = ["Champion", "Level", "Items", "Item 1", "Item 2", "Item 3", "Buff 1", "DPS at 5s", "DPS at 10s", "DPS at 15s", "DPS at 20s",
                   "% physical", "% magical", "% true", "# Attacks", "# Casts", "Item 1 DPS Increase", "Item 2 DPS Increase", "Item 3 DPS Increase",
                   "Buff DPS Increase"]
    workbook   = xlsxwriter.Workbook('dps_stats.xlsx')
    dpsDict = {}
    newEntryLength = 0
    count = 0
    for simList in simLists:
        worksheet1 = workbook.add_worksheet(simList[0][0].name + str(simList[0][0].level))
        worksheet1.write_row(0, 0, headers_arr)
        worksheet1.freeze_panes(1, 0)
        worksheet1.autofilter('A1:Z9999')
        for index, sim in enumerate(simList):
            new_entry = []
            # Champion
            new_entry.append(sim[0].name)
            new_entry.append(sim[0].level)

            new_entry.append(len([x for x in sim[1] if x.name != "NoItem"]))

            #Item 1
            new_entry.append(sim[1][0].name)
            new_entry.append(sim[1][1].name)
            new_entry.append(sim[1][2].name)

            # Buff 1
            new_entry.append(sim[2][0].name)

            # DPS at 5s
            dpsAt5=int(getDPS(sim[3],5))
            dpsAt10=int(getDPS(sim[3],10))
            dpsAt15=int(getDPS(sim[3],15))
            dpsAt20=int(getDPS(sim[3],20))
            new_entry.append(dpsAt5)
            new_entry.append(dpsAt10)
            new_entry.append(dpsAt15)
            new_entry.append(dpsAt20)

            # % Physical
            dps = dpsSplit(sim[3])
            # print(dps)
            new_entry.append(dps['physical'])
            new_entry.append(dps['magical'])
            new_entry.append(dps['true'])

            # # Attacks
            new_entry.append(sim[0].numAttacks)
            new_entry.append(sim[0].numCasts)
            newEntryLength= len(new_entry)
            # item1 formula
            # formula = '=J{0} / INDEX(J:J,MATCH(1,(A{0}=A:A)*("NoItem"=D:D)*(G{0}=G:G)*((E{0}=E:E)*(F{0}=F:F)+(E{0}=F:F)*(F{0}=E:E)),0))'.format(index+2)
            # print(formula)
                
            dpsDict[(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name)] = dpsAt15
            #if sim[2][0].name == "NoItem":
            #    continue
            worksheet1.write_row(index+1, 0, new_entry)
            

        for index, sim in enumerate(simList):
            mainTup = (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name)
            tuples0 = [(sim[0].name, sim[0].level, "NoItem", sim[1][1].name, sim[1][2].name, sim[2][0].name),
                      (sim[0].name, sim[0].level, "NoItem", sim[1][2].name, sim[1][1].name, sim[2][0].name)] 
            tuples1 = [(sim[0].name, sim[0].level, "NoItem", sim[1][0].name, sim[1][2].name, sim[2][0].name),
                      (sim[0].name, sim[0].level, "NoItem", sim[1][2].name, sim[1][0].name, sim[2][0].name)]
            tuples2 = [(sim[0].name, sim[0].level, "NoItem", sim[1][0].name, sim[1][1].name, sim[2][0].name),
                      (sim[0].name, sim[0].level, "NoItem", sim[1][1].name, sim[1][0].name, sim[2][0].name)]
            tuples3 = [(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, "NoItem")]
            for tup in tuples0:
                if tup in dpsDict:
                    worksheet1.write(index+1, len(new_entry), round(dpsDict[mainTup] / dpsDict[tup], 2))
            for tup in tuples1:
                if tup in dpsDict:
                    worksheet1.write(index+1, len(new_entry)+1, round(dpsDict[mainTup] / dpsDict[tup], 2))
            for tup in tuples2:
                if tup in dpsDict:
                    worksheet1.write(index+1, len(new_entry)+2, round(dpsDict[mainTup] / dpsDict[tup], 2))
            for tup in tuples3:
                if tup in dpsDict:
                    worksheet1.write(index+1, len(new_entry)+3, round(dpsDict[mainTup] / dpsDict[tup], 2))
    workbook.close()

def doExperiment(champion, opponent, itemList, buffList, t):
    simulator = Simulator()
    simList = []
    buffList.append(buffs.NoBuff(0,[]))
    for itemCombo in itemList:
        for buff in buffList:
            champ = copy.deepcopy(champion)
            results1 = simulator.simulate(itemCombo, [copy.deepcopy(buff)], champ,
                [copy.deepcopy(opponent), copy.deepcopy(opponent), copy.deepcopy(opponent), copy.deepcopy(opponent)], t)    
            simList.append((champ, itemCombo, [buff], results1))
        #resNoDmg(results1, label=item.name)
    return simList

def doExperimentGivenItems(champion, opponent, itemList, buffs, t):
    simulator = Simulator()
    simList = []
    for itemCombo in itemList:
        champ = copy.deepcopy(champion)
        results1 = simulator.simulate(itemCombo, copy.deepcopy(buffs), champ,
            [copy.deepcopy(opponent) for i in range(8)], t)    
        simList.append((champ, itemCombo, [buffs], results1))
    return simList  

def getComboList(items):
    itemComboList = itertools.combinations_with_replacement(items, 3)
    return [list(a) for a in itemComboList]

def constructGraph():
    t = 22
    # want to construct graph for karma  
    oneItemList = [items.NoItem(), items.Blue(), items.Archangels(), items.Shojin(), items.JG(),
                   items.HoJ(), items.Rab()]
    oneItemList = [[a] for a in oneItemList]
    twoItemList = [[items.Blue(), items.Archangels()],
                   [items.Shojin(), items.Archangels()],
                   [items.Archangels(), items.Archangels()],
                   [items.Blue(), items.Rab()],
                   [items.Shojin(), items.Rab()],
                   [items.JG(), items.IE()],  
                   [items.Blue(), items.Shojin()],
                   [items.Blue(), items.HoJ()],
                   [items.JG(), items.Rab()]]
    itemList = twoItemList
    karmaSimList = doExperimentGivenItems(Karma(2), Viktor(2), itemList, [buffs.Invoker(2,[])], t)
    printSims(karmaSimList)
    #karmaSimList = [[k[3][0:i[0]][0] for i in enumerate(k[3])]  for k in karmaSimList]
    karmaSimList = [np.array([[damageInstance[0], damageInstance[1][0]] for damageInstance in k[3]]) for k in karmaSimList]
    # karmaSimList = [[k[:,0],k[:,1]] for k in karmaSimList ]
    for i in enumerate(karmaSimList):
      karmaSimList[i[0]][:,1] = np.cumsum(karmaSimList[i[0]][:,1], axis=0)
  
    
    # newList = np.cumsum(karmaSimList[0], axis=1)

#   # print(np.cumsum(karmaSimList[0], axis=1))
    for index, value in enumerate(karmaSimList):
      itemNames = ','.join([item.name for item in itemList[index]])
      # itemNames = oneItemList[index][0].name
      plt.plot(*zip(*value), label = itemNames)
    plt.legend()
    plt.show()
    

def printSims(simList):
  f = open("karmaSims.txt", "w")
  for sim in simList:    
    f.write("Champion: {0} {1} \n Items: {2} \n Buffs: {3}\n".format(sim[0].name, sim[0].level,
                                                                   ','.join([item.name for item in sim[1]]),
                                                                   ','.join([buff[0].name for buff in sim[2]])))
    for dmg in sim[3]:
      f.write("t {0:.2f}, dmg {1:.2f}, type {2} \n".format(dmg[0], dmg[1][0], dmg[1][1]))
    f.write("\n")

def constructCSV():
    t = 22
    simLists = []
    simDict = {}
    viktor = Zyra(2)  
    itemComboList = getComboList([items.NoItem(),
                items.Blue(),
                items.Archangels(),
                items.Rageblade(),
                items.cursedRageblade(),
                items.HoJ(),
                items.Rab(),
                items.Shojin(),
                items.cursedGS(),
                items.JG(),
                items.Shiv(),
                items.cursedShiv(),
                items.cursedShojin(),
                items.IE()])
    buffList = [buffs.Spellweaver(2,[5,6,7,8,8.7,9.9,10,11.2,11.4])]

    ADComboList = getComboList([items.NoItem(),
               items.IE(),
               items.HoJ(),
               items.RH(),
               items.cursedRH(),
               items.LW(),
               items.Rageblade(),
               items.cursedRageblade(),
               items.DB([5,7,8,10,11,12,13,14]),
               items.Rab(),
               items.Shojin(),
               items.Shiv(),
               items.cursedShiv(),
               items.cursedZekes(),
               items.cursedGS(),
               items.RFC(),
               items.Blue()])

    VayneComboList = getComboList([items.NoItem(),
                  items.HoJ(),
                  items.RH(),
                  items.cursedRH(),
                  items.Rageblade(),
                  items.DB([5,7,8,10,11,12,13,14]),
                  items.Rab(),
                  items.IE(),
                  items.JG(),
                  items.cursedZekes()
                  ])

    YasuoComboList = getComboList([items.NoItem(),
                  items.HoJ(),
                  items.RH(),
                  items.cursedRH(),
                  items.Rageblade(),
                  items.DB([5,7,8,10,11,12,13,14]),
                  items.Rab(),
                  items.IE(),
                  items.JG(),
                  items.cursedZekes(),
                  items.Blue(),
                  items.Shojin(),
                  items.cursedShojin(),
                  items.Shiv(),
                  items.cursedShiv(),
                  items.Archangels(),
                  items.RFC(),
                  items.cursedGS()
                  ])
    blueList = getComboList([items.NoItem(),
                  items.Blue()
                  ])
    UdyrComboList = getComboList([items.NoItem(),
                  items.HoJ(),
                  items.RH(),
                  items.cursedRH(),
                  items.Rageblade(),
                  items.DB([5,7,8,10,11,12,13,14]),
                  items.IE(),
                  items.cursedZekes(),
                  items.Blue(),
                  items.Shojin(),
                  items.cursedShojin(),
                  items.Shiv(),
                  items.cursedShiv(),
                  items.RFC()
                  ])



    # Zyra w/ spellweaver
    # simLists.append(doExperiment(Zyra(2), Viktor(2), itemComboList, copy.deepcopy(buffList), t))

    # Varus
    simLists.append(doExperiment(Varus(2), DummyTank(2), YasuoComboList, [buffs.Ranger(2, [])], t))


    # Viktor w/ spellweaver
    # simLists.append(doExperiment(Viktor(2), Viktor(2), itemComboList, copy.deepcopy(buffList), t))

    # Ziggs w/ spellweaver
    simLists.append(doExperiment(Ziggs(2), Viktor(2), itemComboList, copy.deepcopy(buffList), t))

    # Syndra w/ redeemed
    # simLists.append(doExperiment(Syndra(2), Viktor(2), itemComboList, [buffs.Redeemed(3,[])], t))

    # Karma w/ invoker
    simLists.append(doExperiment(Ryze(2), Viktor(2), itemComboList, [buffs.Forgotten(3, 2)], t))

    # Vayne w/ forgotten
    simLists.append(doExperiment(Vayne(3), Viktor(2), VayneComboList, [buffs.Forgotten(3, 2)], t))
    
    # Yasuo w/ Legionnaire
    simLists.append(doExperiment(Yasuo(2), Viktor(2), YasuoComboList, [buffs.Legionnaire(2, [])], t))

    # Yasuo 3 w/ Legionnaire
    simLists.append(doExperiment(Yasuo(3), Viktor(2), YasuoComboList, [buffs.Legionnaire(6, [])], t))

    # Karma w/ invoker
    simLists.append(doExperiment(Karma(2), Viktor(2), itemComboList, [buffs.Invoker(2,[])], t))

    # Aphelios
    simLists.append(doExperiment(Aphelios(1), Viktor(2), ADComboList, [buffs.Ranger(2, [])], t))
    # Aphelios
    simLists.append(doExperiment(Aphelios(2), DummyTank(2), ADComboList, [buffs.Ranger(2, [])], t))
    # Kalista
    simLists.append(doExperiment(Kalista(2), Viktor(2), ADComboList, [buffs.Legionnaire(2, [])], t))

    # Udyr
    simLists.append(doExperiment(Udyr(2), Viktor(2), UdyrComboList, [buffs.Skirmisher(3, [])], t))

    # Jax
    simLists.append(doExperiment(Jax(1), Viktor(2), ADComboList, [buffs.Skirmisher(3, [])], t))

    # Riven
    simLists.append(doExperiment(Riven(2), Viktor(2), ADComboList, [buffs.Legionnaire(2, [])], t))

    # Riven with 6 legionaire
    simLists.append(doExperiment(Riven(3), Viktor(2), ADComboList, [buffs.Legionnaire(6, [])], t))

    # Draven
    simLists.append(doExperiment(Draven(2), DummyTank(2), ADComboList, [buffs.Forgotten(6, 2)], t))


    merged = list([itertools.chain.from_iterable(simList) for simList in simLists])
    createDPScsv(simLists)
    #createDPSChart(simList)


if __name__ == "__main__":
    #constructCSV()
    constructGraph()