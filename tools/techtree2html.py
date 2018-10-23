#!/usr/bin/env python2
#
#  Copyright 2001 - 2018 Ludek Smid [http://www.ospace.net/]
#  Copyright 2018 Yann Cantin
#
#  Outer Space is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  Outer Space is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Outer Space; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

# setup library path
import sys
sys.path.append("../server/lib")

# install i18n helpers
def N_(text):
    return text
sys.modules["__builtin__"].N_ = N_

# YSOFT : workaround
def _(s): return s

import os
from optparse import OptionParser

# parse command line arguments (needs to be first, so we have configDir ready when importing)
parser = OptionParser()
parser.add_option("",  "--configdir", dest = "configDir",
    metavar = "DIRECTORY", default = os.path.join(os.path.expanduser("~"), ".outerspace"),
    help = "Override default configuration directory",)

options, args = parser.parse_args()

# imports
import ige.ospace.Rules as Rules

Rules.init(options.configDir)

import ige.ospace.TechHandlers as TechHandlers

# setup jinja2 html template engine
from jinja2 import Environment, FileSystemLoader
jinjaEnv = Environment(loader=FileSystemLoader('./tech2html/templates'))
webroot = os.path.dirname(os.path.abspath(__file__))
webroot = os.path.join(webroot, 'tech2html')

def cclass2Text(cclass):
    return [_("small"), _("medium"), _("large"), _("planet")][cclass]

def structWeapons2Text(array):
    string = ''
    i = 0
    j = 0
    for weaponNum in array:
        if i>3:
            break
        if weaponNum > 0:
            if j > 0:
                string += _(', ')
            string += _('%d') % ( weaponNum )
            string += [_("S"), _("M"), _("L"), _("P"), _("?"),_("?"),_("?"),_("?"),_("?"),_("?")][i]
            j+=1
        i+=1
    return string

def bool2Text(value):
    if value:
        return _("Yes")
    else:
        return _("No")

def perc2Text(value):
    string = _('%d%%') % (value * 100)
    return string

def percBase1_2Text(value):
    value = value-1
    string = _('%+d%%') % (value * 100)
    return string

def perc100_2Text(value):
    string = _('%d%%') % (value)
    return string

def getTechName(techID):
    try:
        tech = Rules.techs[techID]
        return tech.name
    except:
        return _('Unknown')

def getTechShortname(techID):
    try:
        tech = Rules.techs[techID]
        if tech.shortname:
            return tech.shortname
        return tech.name
    except:
        return _('Unknown')

def getRateName(rate):
    string = _('%d Turns') % (int(rate))
    return string

V_NONE = 0x00
V_STRUCT = 0x01
V_HULL = 0x02
V_SEQUIP = 0x04
V_PROJECT = 0x08
V_EFF = 0x10 # attr * techEff
V_EFF_REV = 0x20 # attr / techEff
V_ALL = V_STRUCT|V_HULL|V_SEQUIP|V_PROJECT

techAttrs = {}

defaultAttr = (0, _('Not specified'), V_NONE, True, None, int)

def addAttr(attr, uisort, descr, props, showIfDefault, default = 0, convertor = int):
    global techAttrs
    techAttrs[attr] = (uisort, descr, props, showIfDefault, default, convertor)


addAttr('buildProd',        0, _('Construction request - construction points'), V_ALL, 0)

addAttr('operBio',          100, _('Operational request - biomatter'), V_ALL, 0)
addAttr('operMin',          101, _('Operational request - minerals'), V_ALL, 0)
addAttr('operEn',           102, _('Operational request - energy'), V_ALL, 0)
addAttr('operWorkers',      103, _('Operational request - workers'), V_ALL, 0)

addAttr('prodBio',          200, _('Production - biomatter'), V_STRUCT|V_EFF, 0)
addAttr('prodMin',          201, _('Production - minerals'), V_STRUCT|V_EFF, 0)
addAttr('prodEn',           202, _('Production - energy'), V_STRUCT|V_EFF, 0)
addAttr('prodPop',          203, _('Production - population'), V_STRUCT|V_EFF, 0)
addAttr('prodProd',         204, _('Production - construction points'), V_STRUCT|V_PROJECT|V_EFF, 0)
addAttr('prodSci',          205, _('Production - research points'), V_STRUCT|V_PROJECT|V_EFF, 0)
addAttr('prodEnv',          206, _('Production - environment effect'), V_STRUCT|V_EFF, 0)

addAttr('solarMod',         300, _('Orbital Shift Effect'), V_STRUCT|V_EFF, 0)

addAttr('storBio',          400, _('Storage - biomatter'), V_STRUCT|V_EFF, 0)
addAttr('storMin',          401, _('Storage - minerals'), V_STRUCT|V_EFF, 0)
addAttr('storEn',           402, _('Storage - energy'), V_ALL|V_EFF, 0)
addAttr('storPop',          403, _('Accommodate population'), V_STRUCT|V_EFF, 0)

addAttr('revoltThr',        500, _('Lowers revolt threshold by'), V_STRUCT|V_PROJECT|V_EFF, 0)
addAttr('moraleTrgt',       501, _('Increases maximun morale by'), V_STRUCT|V_PROJECT|V_EFF, 0)
addAttr('govPwr',           502, _('Government power'), V_STRUCT|V_EFF, 0)

addAttr('maxHP',            600, _('Hit points'), V_STRUCT|V_HULL|V_SEQUIP|V_EFF, 0)

addAttr('scannerPwr',       700, _('Scanner power'), V_STRUCT|V_SEQUIP|V_EFF, 0)
addAttr('planetShield',     701, _('Planetary shield'), V_STRUCT|V_EFF, 0)
addAttr('structWeapons',    702, _('Weapons'), V_STRUCT, 0, convertor = structWeapons2Text)
addAttr('systemAtt',        703, _('Fleet attack (bonus)'), V_STRUCT|V_EFF, 0)
addAttr('systemDef',        704, _('Fleet defense (bonus)'), V_STRUCT|V_EFF, 0)
addAttr('fleetSpeedBoost',  705, _('Boost speed of fleets'), V_STRUCT|V_EFF, 0, convertor = float)
addAttr('refuelMax',        706, _('Maximum refuel percent'), V_STRUCT|V_EFF, 0, convertor = perc100_2Text)
addAttr('refuelInc',        707, _('Refuel increase percent'), V_STRUCT|V_EFF, 0, convertor = perc100_2Text)
addAttr('repairShip',       708, _('Repair increase percent'), V_STRUCT|V_EFF, 0, convertor = perc2Text)
addAttr('upgradeShip',      709, _('Upgrade points per turn'), V_STRUCT|V_EFF, 0)

addAttr('trainShipInc',     800, _('Experience points per turn'), V_STRUCT|V_EFF, 0, convertor = float)
addAttr('trainShipMax',     801, _('Experience cap (base exp multiple)'), V_STRUCT|V_EFF, 0)

addAttr('mineclass',        900, _('Mine Class Deployed'), V_STRUCT, 0, convertor = getTechShortname)
addAttr('minenum',          901, _('Maximum Supported Mines'), V_STRUCT|V_EFF, 0, convertor = int)
addAttr('minerate',         902, _('Mine Rate of Deploy'), V_STRUCT|V_EFF_REV, 0, convertor = getRateName)

addAttr('combatClass',          1000, _('Hull class'), V_HULL, 0, convertor = cclass2Text)
addAttr('maxWeight',            1001, _('Maximum payload'), V_HULL, 0)
addAttr('minHull',              1002, _('Minimum required hull'), V_SEQUIP|V_HULL, 0, convertor = cclass2Text)
addAttr('weight',               1003, _('Weight'), V_SEQUIP|V_HULL, 0)
addAttr('slots',                1004, _('Slots'), V_SEQUIP|V_HULL, 0)
addAttr('engPwr',               1005, _('Engine power'), V_SEQUIP|V_EFF, 0)

addAttr('signature',            2000, _('Scan signature'), V_SEQUIP|V_HULL, 0)
addAttr('signatureCloak',       2001, _('Signature visibility'), V_SEQUIP|V_HULL, 0)
addAttr('signatureDecloak',     2003, _('Signature visibility'), V_SEQUIP|V_HULL, 0)
addAttr('minSignature',         2004, _('Minimum signature'), V_SEQUIP|V_HULL, 0)

addAttr('weaponClass',          3000, _('Target class'), V_SEQUIP, True, convertor = cclass2Text)
addAttr('weaponAtt',            3001, _('Weapon attack'), V_SEQUIP|V_EFF, 0)
addAttr('weaponROF',            3002, _('Weapon Rate Of Fire'), V_SEQUIP, 0, convertor = float)
addAttr('weaponDmgMin',         3003, _('Weapon minimum damage'), V_SEQUIP|V_EFF, 0)
addAttr('weaponDmgMax',         3004, _('Weapon maximum damage'), V_SEQUIP|V_EFF, 0)
addAttr('weaponIsMissile',      3005, _('Missile weapon (ECM counts)'), V_SEQUIP|V_HULL, 0, convertor = bool2Text)
addAttr('weaponIgnoreShield',   3006, _('Weapon ignore shield'), V_SEQUIP|V_HULL, 0, convertor = bool2Text)
addAttr('weaponGoodForFlak',    3007, _('Weapon can be used in flak'), V_SEQUIP, 0, default=1, convertor = bool2Text)

addAttr('combatDef',            4000, _('Combat defense'), V_SEQUIP|V_HULL|V_EFF, 0)
addAttr('combatAtt',            4001, _('Combat attack'), V_SEQUIP|V_HULL|V_EFF, 0)
addAttr('missileDef',           4002, _('Missile defense'), V_SEQUIP|V_EFF, 0)
addAttr('combatAttPerc',        4003, _('Combat attack (extra)'), V_SEQUIP|V_HULL|V_EFF, 0, default=1, convertor = percBase1_2Text)
addAttr('combatDefPerc',        4004, _('Combat defense (extra)'), V_SEQUIP|V_HULL|V_EFF, 0, default=1, convertor = percBase1_2Text)
addAttr('missileDefPerc',       4005, _('Missile defense (extra)'), V_SEQUIP|V_EFF, 0, default=1, convertor = percBase1_2Text)

addAttr('shieldPerc',           5000, _('Shield strength'), V_SEQUIP|V_HULL|V_EFF, 0, convertor = perc2Text)
addAttr('shieldRechargeFix',    5001, _('Shield recharge fixed'), V_SEQUIP|V_HULL|V_EFF, 0)
addAttr('shieldRechargePerc',   5002, _('Shield recharge percent'), V_SEQUIP|V_HULL|V_EFF, 0, convertor = perc2Text)
addAttr('damageAbsorb',         5003, _('Armor damage absorption'), V_SEQUIP|V_HULL, 0)
addAttr('autoRepairFix',        5004, _('Repair fixed'), V_SEQUIP|V_HULL|V_EFF, 0)
addAttr('autoRepairPerc',       5005, _('Repair percent'), V_SEQUIP|V_HULL|V_EFF, 0, convertor = perc2Text)

addAttr('addMP',                6000, _('Device MP'), V_SEQUIP|V_HULL, 0)

race2Name = {
    "B": "Bionic",
    "C": "Cyborg",
    "H": "Human",
    "m": "Mutant",
    "r": "Renegade",
    "e": "EDEN",
    "p": "Pirate",
    "#": "Dev",
}

race2Filename = {
    "B": "bionic",
    "C": "cyborg",
    "H": "human",
    "m": "mutant",
    "r": "renegade",
    "e": "eden",
    "p": "pirate",
    "#": "dev",
}

stratRes = {
    0: "None",
    1: "Uranium",
    2: "Titanium",
    3: "Chromium",
    4: "Silicium",
    5: "Carboneum",
    6: "Antimatter",
    7: "Plutonium",
    8: "Wolframium",
    100: "Mutagen",
    1000: "Unnilseptium"
}

stratRes2filename = {
    0: "none",
    1: "uranium",
    2: "titanium",
    3: "chromium",
    4: "silicium",
    5: "carboneum",
    6: "antimatter",
    7: "plutonium",
    8: "wolframium",
    100: "mutagen",
    1000: "unnilseptium"
}

techType2txt = {
    V_NONE: "Progress", 
    V_STRUCT: "Structure", 
    V_HULL: "Ship hull",
    V_SEQUIP: "Ship equipment",
    V_PROJECT: "Project"
}

techType2filename = {
    V_NONE: "progress", 
    V_STRUCT: "structure", 
    V_HULL: "ship_hull",
    V_SEQUIP: "ship_equipment",
    V_PROJECT: "project"
}

def races2Names(s):
    descr = []
    for c in s:
        try:
            descr.append(("%s" % race2Name[c], "%s" % race2Filename[c]))
        except KeyError:
            descr.append(("???", "unknown"))
    return descr

def strategicResources2Text(tech, attr):
    try:
        resourceDict = getattr(tech, attr)
    except AttributeError:
        return ""
    requiredStrategicResources = []
    for res in resourceDict:
        try:
            amount = resourceDict[res] / float(Rules.stratResAmountBig)
        except IndexError:
            # this is case of research resources - it's pure list, not a dictionary
            requiredStrategicResources += [stratRes[res]]
        else:
            # continuation of build resources
            requiredStrategicResources += ['{0} ({1})'.format(stratRes[res], amount)]
    return ', '.join(requiredStrategicResources)

class HtmlTech:
    def __init__(self,  id):
        self.id = id
        self.name = ''
        self.type = V_NONE
        self.typeStr = ''
        self.tl = 0
        self.advanceTl = False
        self.races = 'BCHmrep#'
        self.racesStr = races2Names(self.races)
        self.maxImprovement = Rules.techMaxImprovement
        self.costs = {} # [1..tech.maxImprovement+1] = cost
        self.researchRequires = [] # list of (techID, tech.level, tech.name, improvement)
        self.researchDisables = [] # list of (techID, tech.level, tech.name)
        self.researchEnables = [] # list of (techID, tech.level, tech.name, improvement, reseachRaces, reseachRacesTxt)
        self.researchReqSRes = [] # list of (num, txt, filenametxt)
        self.canBeBuild = False
        self.buildCP = 0 # CP
        self.buildSRes = [] # list of (num, txt, ammount, filenametxt)
        self.prodBioMod = []
        self.prodEnMod = []
        self.prodProdMod = []
        self.textPreRsrch = 'No information available.'
        self.textDescr = 'No information available.'
        self.textFlavor = 'No information available.'
        self.specs = [] # list of (uisort, txt, EFF, value, values)

def techtree2html():
    # process tree
    techs = [tech for tech in list(Rules.techs.itervalues())]
    techs = sorted(techs, key=lambda x: x.id)
    
    htmlTechs = {}
    
    for tech in techs:
        htmlTech = HtmlTech(tech.id)
        
        htmlTech.name = tech.name
        
        techType = V_NONE
        if tech.isStructure:
            techType = V_STRUCT
        elif tech.isShipHull:
            techType = V_HULL
        elif tech.isShipEquip:
            techType = V_SEQUIP
        elif tech.isProject:
            techType = V_PROJECT
        htmlTech.type = techType
        htmlTech.typeStr = techType2txt[techType]
        htmlTech.typeFilename = techType2filename[techType]

        htmlTech.tl = tech.level
        
        if tech.finishResearchHandler == TechHandlers.finishResTLAdvance:
            htmlTech.advanceTl = True
            
        if tech.researchRaces:
            htmlTech.races = tech.researchRaces
            htmlTech.racesStr = races2Names(tech.researchRaces)

        if hasattr(tech, 'maxImprovement'):
            htmlTech.maxImprovement = tech.maxImprovement
            
        if hasattr(tech, 'researchMod'):
            if tech.level < 10:
                for improvement in range(1,  htmlTech.maxImprovement+1):
                   # from Utils.py getTechRCost
                    resCost = int((2 ** tech.level) * Rules.techImprCostMod[improvement] * tech.researchMod)
                    htmlTech.costs[improvement] = resCost
        
        if tech.researchRequires:
            for tmpTechID, improvement in tech.researchRequires:
                tmpTech = Rules.techs[tmpTechID]
                htmlTech.researchRequires.append((tmpTechID, tmpTech.level, tmpTech.name, improvement))

        try:
            resourceDict = getattr(tech, "researchReqSRes")
        except AttributeError:
            pass
        else:
            for res in resourceDict:
                htmlTech.researchReqSRes.append((res, stratRes[res], stratRes2filename[res]))

        if hasattr(tech, "researchDisables") and tech.researchDisables:
            for tmpTechID in tech.researchDisables:
                tmpTech = Rules.techs[tmpTechID]
                htmlTech.researchDisables.append((tmpTechID, tmpTech.level, tmpTech.name))
        
        for improvement in range(1, Rules.techMaxImprovement+1):
            for tmpTechID in tech.researchEnables[improvement]:
                tmpTech = Rules.techs[tmpTechID]
                researchRaces = ''
                researchRacesTxt = ''
                if tmpTech.researchRaces:
                    researchRaces = tmpTech.researchRaces
                    researchRacesTxt = races2Names(tmpTech.researchRaces)
                htmlTech.researchEnables.append((tmpTechID, tmpTech.level, tmpTech.name, improvement, researchRaces, researchRacesTxt))

        if tech.prodBioMod != [0, 0, 0, 0] and tech.prodBioMod != [0, 0, 0, 1]:
            htmlTech.prodBioMod = tech.prodBioMod
        if tech.prodEnMod != [0, 0, 0, 0] and tech.prodEnMod != [0, 0, 0, 1]:
            htmlTech.prodEnMod = tech.prodEnMod
        if tech.prodProdMod != [0, 0, 0, 0] and tech.prodProdMod != [0, 0, 0, 1]:
            htmlTech.prodProdMod = tech.prodProdMod
        if tech.prodSciMod != [0, 0, 0, 0] and tech.prodSciMod != [0, 0, 0, 1]:
            htmlTech.prodSciMod = tech.prodSciMod

        if tech.textPreRsrch:
            htmlTech.textPreRsrch = tech.textPreRsrch
        if tech.textDescr:
            htmlTech.textDescr = tech.textDescr
        if tech.textFlavor:
            htmlTech.textFlavor = tech.textFlavor

        for attr in dir(tech):
            if attr == "buildProd": continue
            value = getattr(tech, attr)
            uisort, descr, props, showIfDef, default, convertor = techAttrs.get(attr, defaultAttr)
            if techType & props and (value != default or showIfDef):
                tmpValue = 0
                tmpValues = {}
                if (V_EFF & props) or (V_EFF_REV & props):
                    for improvement in range(1, htmlTech.maxImprovement+1):
                        techEff = Rules.techImprEff[improvement]
                        if V_EFF & props:
                            tmpValues[improvement] = convertor(value * techEff)
                        elif V_EFF_REV & props:
                            tmpValues[improvement] = convertor(value / techEff)
                else:
                    tmpValue = convertor(value)
                htmlTech.specs.append((uisort, descr, (V_EFF & props) or (V_EFF_REV & props),  tmpValue,  tmpValues))
        
        # Extract production requirements
        htmlTech.buildCP = getattr(tech, "buildProd", 0)
        try:
            resourceDict = getattr(tech, "buildSRes")
        except AttributeError:
            pass
        else:
            for res in resourceDict:
                htmlTech.buildSRes.append((res, stratRes[res], resourceDict[res] / float(Rules.stratResAmountBig), stratRes2filename[res]))
        if (len(htmlTech.buildSRes) + htmlTech.buildCP) > 0:
            htmlTech.canBeBuild = True

        # Handle special tech (from TechHandlers.py)
        if tech.finishConstrHandler == TechHandlers.finishProjectNF:
            htmlTech.specs.append((1, 'Produce %s' % stratRes[int(tech.data)], False,  Rules.stratResAmountSmall,  {}))
            
        if tech.finishConstrHandler == TechHandlers.finishProjectNF2:
            htmlTech.specs.append((1, 'Produce %s' % stratRes[int(tech.data)], False,  4 * Rules.stratResAmountBig,  {}))

        if tech.finishConstrHandler == TechHandlers.finishProjectIMPRENV:
            enTrans = {}
            for improvement in range(1, htmlTech.maxImprovement+1):
                techEff = Rules.techImprEff[improvement]
                enTrans[improvement] = int(float(tech.data) * techEff)
            htmlTech.specs.append((1, 'Max environment gain', True,  0,  enTrans))

        if tech.finishConstrHandler == TechHandlers.finishProjectAsteroidMining:
            minTrans = {}
            for improvement in range(1, htmlTech.maxImprovement+1):
                techEff = Rules.techImprEff[improvement]
                minTrans[improvement] = int(float(tech.data) * techEff)
            htmlTech.specs.append((1, 'Max mineral gain', True,  0,  minTrans))

        if tech.finishConstrHandler == TechHandlers.finishProjectShiftPlDown:
            minTrans = {}
            for improvement in range(1, htmlTech.maxImprovement+1):
                techEff = Rules.techImprEff[improvement]
                minTrans[improvement] = int(float(tech.data) * techEff)
            htmlTech.specs.append((1, 'Max energy gain', True,  0,  minTrans))

        if tech.finishConstrHandler == TechHandlers.finishProjectShiftPlUp:
            minTrans = {}
            for improvement in range(1, htmlTech.maxImprovement+1):
                techEff = Rules.techImprEff[improvement]
                minTrans[improvement] = int(float(tech.data) * techEff)
            htmlTech.specs.append((1, 'Max energy loss', True,  0,  minTrans))

        if tech.finishConstrHandler == TechHandlers.finishProjectDEEPSPACESCAN:
            boost = {}
            for improvement in range(1, htmlTech.maxImprovement+1):
                techEff = Rules.techImprEff[improvement]
                boost[improvement] = "%i %%" % int(float(tech.data) * techEff * 100)
            htmlTech.specs.append((1, 'Max scanner power boost', True,  0,  boost))

        # sort for ui
        htmlTech.researchRequires.sort(key=lambda item: (item[1], item[2]))
        htmlTech.researchDisables.sort(key=lambda item: item[2])
        htmlTech.researchEnables.sort(key=lambda item: (item[1], item[2]))
        htmlTech.researchReqSRes.sort(key=lambda item: item[0])
        htmlTech.buildSRes.sort(key=lambda item: item[0])
        htmlTech.specs.sort(key=lambda item: item[0])
        
        # Add to htmlTechs
        htmlTechs[tech.id] = htmlTech

        # Extract techs
        techByTl = {}
        techByRace = {}
        techByType = {}
        techByStrat = {}
        indexes = {}
        for id, t in htmlTechs.iteritems():
            # TL
            if t.tl in techByTl:
                techByTl[t.tl].append(t)
            else:
                techByTl[t.tl] = [t]
            # Race
            for r in "BCHmrep#":
                if r in t.races:
                    if r in techByRace:
                        if t.tl in techByRace[r]:
                            techByRace[r][t.tl].append(t)
                        else:
                            techByRace[r][t.tl] = [t]
                    else:
                        techByRace[r] = {}
                        techByRace[r][t.tl] = [t]
            # Type
            for k in (V_NONE, V_STRUCT, V_HULL, V_SEQUIP, V_PROJECT):
                if k == t.type:
                    if k in techByType:
                        if t.tl in techByType[k]:
                            techByType[k][t.tl].append(t)
                        else:
                            techByType[k][t.tl] = [t]
                    else:
                        techByType[k] = {}
                        techByType[k][t.tl] = [t]
            # Stratres
            usedStrat = []
            for slist in t.researchReqSRes:
                usedStrat.append(slist[0])
            for slist in t.buildSRes:
                usedStrat.append(slist[0])
            for s in (1, 2, 3, 4, 5, 6, 7, 8, 100, 1000):
                if s in usedStrat:
                    if s in techByStrat:
                        if t.tl in techByStrat[s]:
                            techByStrat[s][t.tl].append(t)
                        else:
                            techByStrat[s][t.tl] = [t]
                    else:
                        techByStrat[s] = {}
                        techByStrat[s][t.tl] = [t]

        # sort
        for tl in techByTl:
            techByTl[tl].sort(key=lambda item: item.name)
        for r in techByRace:
            for tl in techByRace[r]:
                techByRace[r][tl].sort(key=lambda item: item.name)
        for k in techByType:
            for tl in techByType[k]:
                techByType[k][tl].sort(key=lambda item: item.name)
        for s in techByStrat:
            for tl in techByStrat[s]:
                techByStrat[s][tl].sort(key=lambda item: item.name)
        
        # nav
        nav = {("Home", "techtree.html"), ("All", "index_tl.html")}
        
        # Generate tech pages
        techTemplate = jinjaEnv.get_template("tech.html")
        for id, t in htmlTechs.iteritems():
            filename = os.path.join(webroot, "%s.html" % id)
            with open(filename, 'w') as fh:
                fh.write(techTemplate.render(nav = nav, tech = t, maxImprovement = t.maxImprovement))
        # Generate indexes
        # TL
        tlTemplate = jinjaEnv.get_template("tl.html")
        filename = os.path.join(webroot, "index_tl.html")
        with open(filename, 'w') as fh:
            fh.write(tlTemplate.render(nav = nav, techs = techByTl))
        indexes["TL"] = [("All technologies", "index_tl.html")]
        # Races
        raceTemplate = jinjaEnv.get_template("race.html")
        indexes["Races"] = []
        for r in techByRace:
            filename = os.path.join(webroot, "index_%s.html" % races2Names(r)[0][1])
            with open(filename, 'w') as fh:
                fh.write(raceTemplate.render(nav = nav, race = races2Names(r)[0][0], techs = techByRace[r]))
            indexes["Races"].append((races2Names(r)[0][0], "index_%s.html" % races2Names(r)[0][1]))
        # Types
        typeTemplate = jinjaEnv.get_template("type.html")
        indexes["Types"] = []
        for k in techByType:
            filename = os.path.join(webroot, "index_%s.html" % techType2filename[k])
            with open(filename, 'w') as fh:
                fh.write(typeTemplate.render(nav = nav, type = techType2txt[k], techs = techByType[k]))
            indexes["Types"].append((techType2txt[k], "index_%s.html" % techType2filename[k]))
        # Stratres
        typeTemplate = jinjaEnv.get_template("strat.html")
        indexes["Strategic ressources"] = []
        for s in sorted(techByStrat):
            filename = os.path.join(webroot, "index_%s.html" % stratRes2filename[s])
            with open(filename, 'w') as fh:
                fh.write(typeTemplate.render(nav = nav, strat = stratRes[s], techs = techByStrat[s]))
            indexes["Strategic ressources"].append((stratRes[s], "index_%s.html" % stratRes2filename[s]))
        # Global
        techtreeTemplate = jinjaEnv.get_template("techtree.html")
        filename = os.path.join(webroot, "techtree.html")
        with open(filename, 'w') as fh:
            fh.write(techtreeTemplate.render(nav = nav, pages = indexes))

techtree2html()
