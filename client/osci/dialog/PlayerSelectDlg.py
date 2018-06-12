#
#  Copyright 2001 - 2016 Ludek Smid [http://www.ospace.net/]
#
#  This file is part of Outer Space.
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

import pygameui as ui
from osci import client, gdata, res
from ige.ospace.Const import *
from MainGameDlg import MainGameDlg
from ConfirmDlg import ConfirmDlg
from BookingDlg import BookingDlg
import ige

class PlayerSelectDlg:
    """ Called for selection of active or picking a new player."""

    def __init__(self, app):
        self.app = app
        self.wantsNew = False
        self.needsPassword = False
        self.previousSelection = None # this is to fix connection lost/relog usability issue
        self.createUI()
        self.confirmDlg = ConfirmDlg(app)
        self.confirmDlg.setTitle(_("No free starting position"))

    def display(self, caller = None):
        self.caller = caller
        if gdata.mainGameDlg and self.previousSelection:
            # this means connection dropped and we relogged
            # let's go straight to the previously selected game
            self._selectPlayer(self.previousSelection)
            return
        if self.show():
            self.win.show()

    def hide(self):
        self.win.hide()

    def show(self):
        items = []
        items.extend(self.showActivePlayers())
        if self.wantsNew:
            items.extend(self.showStartPositions())
        self.win.vPos.setItems(items)
        self.showPassword()
        return True

    def showPassword(self):
        self.win.vLPassword.visible = self.win.vPassword.visible = self.needsPassword

    def showActivePlayers(self):
        dataActive = client.cmdProxy.getActivePositions()
        items = []
        for playerID, galaxyName, playerType in dataActive:
            item = ui.Item(galaxyName, type = 'Active', tObjID = playerID, tPosType = PLAYER_SELECT_CONTINUE)
            if playerType == T_PLAYER:
                item.tPos = _('Continue playing.')
            elif playerType == T_PIRPLAYER:
                item.tPos = _('Yarr!')
            else:
                item.tPos = _('Unknown type of player.')
            items.append(item)
        if not items:
            item = ui.Item('', type = '', tObjID = 'No active players', tPosType = None)
            item.tPos = 'No Active Player'
            items.append(item)
        return items

    def showStartPositions(self):
        dataStart = client.cmdProxy.getStartingPositions()
        items = []
        for objID, galaxyName, posType in dataStart:
            item = ui.Item(galaxyName, type = _('Open'), tObjID = objID, tPosType = posType)
            if posType == PLAYER_SELECT_NEWPLAYER:
                item.tPos = _('Independent player')
            elif posType == PLAYER_SELECT_AIPLAYER:
                item.tPos = _("Rebel faction")
            elif posType == PLAYER_SELECT_PIRATE:
                item.tPos = _("Pirate faction [VIP password needed]")
            else:
                item.tPos = _('Unknown. You cannot use this.')
            items.append(item)
        return items

    def onSelect(self, widget, action, data):
        if not self.win.vPos.selection:
            self.win.setStatus(_('Select position.'))
            return
        item = self.win.vPos.selection[0]
        if item.tPosType == PLAYER_SELECT_CONTINUE:
            playerID = item.tObjID
        elif item.tPosType == PLAYER_SELECT_NEWPLAYER:
            self.win.setStatus(_('Executing CREATE NEW PLAYER command...'))
            playerID = client.cmdProxy.createNewPlayer(item.tObjID)
            self.win.setStatus(_('Command has been executed.'))
        elif item.tPosType == PLAYER_SELECT_AIPLAYER:
            self.win.setStatus(_('Executing TAKE OVER REBEL FACTION command...'))
            playerID = client.cmdProxy.takeOverAIPlayer(item.tObjID)
            self.win.setStatus(_('Command has been executed.'))
        elif item.tPosType == PLAYER_SELECT_PIRATE:
            password = self.win.vPassword.text
            if not password:
                self.win.setStatus(_("Supply VIP password, please."))
                return
            self.win.setStatus(_('Executing TAKE OVER PIRATE FACTION command...'))
            try:
                playerID = client.cmdProxy.takeOverPirate(item.tObjID, password)
            except ige.SecurityException:
                self.win.setStatus(_("Supply valid VIP password."))
                return
            self.win.setStatus(_('Command has been executed.'))
        else:
            return
        self._selectPlayer(playerID)

    def _selectPlayer(self, playerID):
        self.win.setStatus(_('Executing SELECT PLAYER command...'))
        client.cmdProxy.selectPlayer(playerID)
        self.previousSelection = playerID
        self.win.setStatus(_('Command has been executed.'))
        self.hide()
        if not gdata.mainGameDlg:
            gdata.mainGameDlg = MainGameDlg(self.app)
            gdata.mainGameDlg.display()
        client.updateDatabase()

    def onToggleNew(self, widget, action, data):
        self.wantsNew = not self.wantsNew
        if self.wantsNew:
            self.win.vToggle.text = _('Hide Open Slots')
        else:
            self.win.vToggle.text = _('Show Open Slots')
            self.win.vPos.unselectAll()
            self.needsPassword = False
        # there is a bug which prevents redraw for mere text change
        self.win.vToggle.visible = 0
        self.win.vToggle.visible = 1
        self.show()

    def onListSelect(self, widget, action, data):
        if data.tPosType == PLAYER_SELECT_CONTINUE:
            playerID = data.tObjID
            self._selectPlayer(playerID)
        needsPassword = data.tPosType == PLAYER_SELECT_PIRATE
        dirty = False
        if needsPassword != self.needsPassword:
            self.needsPassword = needsPassword
            self.showPassword()

    def onBooking(self, widget, action, data):
        self.win.hide()
        self.win.setStatus(_('Command has been executed.'))
        BookingDlg(gdata.app).display(self)

    def onCancel(self, widget, action, data):
        self.win.hide()
        self.app.exit()

    def createUI(self):
        w, h = gdata.scrnSize
        self.win = ui.Window(self.app,
            modal = 1,
            movable = 0,
            title = _('Select gaming session'),
            rect = ui.Rect((w - 564) / 2, (h - 264) / 2, 564, 264),
            layoutManager = ui.SimpleGridLM(),
            tabChange = True
        )
        ui.Listbox(self.win, layout = (0, 0, 28, 10), id = 'vPos',
            columns = ((_('Type'), 'type', 4, ui.ALIGN_W),
                       (_('Galaxy'), 'text', 8, ui.ALIGN_W),
                       (_('Position'), 'tPos', 0, ui.ALIGN_W)),
            action = 'onListSelect',
            columnLabels = 1)
        self.win.subscribeAction('*', self)
        ui.Label(self.win, layout = (8, 10, 5, 1), id = 'vLPassword', text = _("VIP Password:"))
        ui.Entry(self.win, layout = (13, 10, 7, 1), id = 'vPassword', align = ui.ALIGN_W, showChar = '*', orderNo = 1 )
        ui.TitleButton(self.win, layout = (20, 10, 8, 1), text = _('Book New Game'), action = 'onBooking', tooltipTitle = _("New galaxy"), tooltip = _("Allows you to either start new single player galaxy, or get in a queue for\ngame with other players. That game will start when queue fills the capacity,\nand will show up in this dialog as active.\n\nYou can queue for multiple galaxies. Only single player games has account limit."))
        ui.TitleButton(self.win, layout = (0, 10, 8, 1), id = 'vToggle', text = _('Show Open Slots'), action = 'onToggleNew', tooltipTitle = _("Open slots"), tooltip = _("Slots available in already running galaxies, there is no telling\nwhat state the game or the empire is in."))
        ui.Title(self.win, layout = (0, 11, 20, 1), id = 'vStatusBar', align = ui.ALIGN_W)
        ui.TitleButton(self.win, layout = (20, 11, 4, 1), text = _('Exit'), action = 'onCancel')
        ui.TitleButton(self.win, layout = (24, 11, 4, 1), text = _('Select'), action = 'onSelect')
        self.win.statusBar = self.win.vStatusBar