import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from window.connexion import Ui_Dialog as Ui_Connexion
from window.register import Ui_Dialog as Ui_Register
from window.agenda import Ui_Dialog as Ui_Agenda
from window.event import Ui_Dialog as Ui_Event
from window.settings import Ui_Dialog as Ui_Settings
from window.modify import Ui_Dialog as Ui_Modify
from window.error import Ui_invaliddisplayname as error
from PyQt5.QtWidgets import QTableWidgetItem
import datetime
from PyQt5.QtCore import QDateTime

from user import User, EventUser
import requests


class Connexion(QtWidgets.QDialog, Ui_Connexion):

    def __init__(self):
        super(Connexion, self).__init__()
        self.setupUi(self)
        self.window_register = Register()
        self.pushButtonRegister.clicked.connect(self.openRegister)
        self.pushButton.clicked.connect(self.checkUser)

        self.error_message = Error()

    def openRegister(self):
        self.hide()
        self.window_register.exec_()
        self.show()

    def openAgenda(self, client):
        self.window_agenda = Agenda(client)
        self.window_agenda.show()
    
    def checkUser(self):
        client = User()
        r = client.login(self.lineEdit.text(), self.lineEdit_2.text(), self.lineEditSecretstring.text())
        if r.status_code == 401:
            self.error_message.textBrowser.clear()
            self.error_message.textBrowser.setText(r.text)
            self.error_message.exec_()
        else:
            self.hide()
            self.openAgenda(client)


class Register(QtWidgets.QDialog, Ui_Register):

    def __init__(self):
        super(Register, self).__init__()
        self.setupUi(self)
        self.error_message = Error()
        self.pushButtonValide.clicked.connect(self.checkDisplayname)

    def checkDisplayname(self):
        lower, upper, digit = 0, 0, 0
        displayname = self.lineEdiDisplayname.text()
        if (len(displayname) >= 4):
            for i in displayname:

                if (i.islower()):
                    lower+=1		

                if (i.isupper()):
                    upper+=1		

                if (i.isdigit()):
                    digit+=1		

        if (lower+upper+digit==len(displayname) and lower+upper+digit >= 4):
            self.checkLoginname()
        else:
            self.error_message.textBrowser.clear()
            self.error_message.textBrowser.setText("Invalid displayname use only lowercase, uppercase and numbers. use at least 4 characters")
            self.error_message.exec_()

    def checkLoginname(self):
        lower, upper, digit = 0, 0, 0
        loginname = self.lineEditLoginname.text()
        if (len(loginname) >= 6):
            for i in loginname:

                if (i.islower()):
                    lower+=1		

                if (i.isupper()):
                    upper+=1		

                if (i.isdigit()):
                    digit+=1		

        if (lower+upper+digit==len(loginname) and lower+upper+digit >= 6 and loginname != self.lineEdiDisplayname.text()):
            self.checkPassword()
        else:
            self.error_message.textBrowser.clear()
            self.error_message.textBrowser.setText("Invalid loginname use only lowercase, uppercase and numbers. Use at least 6 characters and use different name from display name")
            self.error_message.exec_()

    def checkPassword(self):
        lower, upper, special, digit = 0, 0, 0, 0
        password = self.lineEditPassword.text()
        if (len(password) >= 8):
            for i in password:

                if (i.islower()):
                    lower+=1		

                if (i.isupper()):
                    upper+=1		

                if (i.isdigit()):
                    digit+=1		

                if(i=='?'or i=='!' or i=='_' or i=='+' or i=='/' or i=='@'):
                    special+=1	

        if (lower>=1 and upper>=1 and digit>=1 and special>=1 and lower+upper+digit+special==len(password)):
            client = User()
            r = client.register(self.lineEdiDisplayname.text(), self.lineEditLoginname.text(), self.lineEditPassword.text())
            if r.status_code == 409:
                self.error_message.textBrowser.clear()
                self.error_message.textBrowser.setText(r.text)
                self.error_message.exec_()
            else:
                self.error_message.textBrowser.clear()
                self.error_message.textBrowser.setText(r.text + "\n Your secret key is " + client.userSecret + 
                "\nPLEASE DO NOT LOSE IT! write it down somewhere because if it is lost, you can't access your agenda!")
                self.error_message.exec_()
                self.valid()
        else:
            self.error_message.textBrowser.clear()
            self.error_message.textBrowser.setText("Invalid password, please follow the instructions to create a strong password")
            self.error_message.exec_()

    def valid(self):
        self.lineEdiDisplayname.clear()
        self.lineEditLoginname.clear()
        self.lineEditPassword.clear()
        self.hide()


class Agenda(QtWidgets.QDialog, Ui_Agenda):
    def __init__(self, user):
        super(Agenda, self).__init__()
        self.setupUi(self)
        self.window_event = Event(user)
        self.window_settings = Settings(user)
        self.window_modify = Modify(user)
        self.pushButtonEvent.clicked.connect(self.openCreationEvent)
        self.pushButtonSettings.clicked.connect(self.openSettings)
        self.pushButtonModify.clicked.connect(self.openModify)
        #self.pushButtonDeleteEvent.clicked.connect(self.deleteEvent)
        self.pushButtonInvite.clicked.connect(self.addContact)
        self.pushButtonAcceptInvit.clicked.connect(self.acceptContact)
        self.pushButtonDeny.clicked.connect(self.removeContact)
        self.pushButtonDelete.clicked.connect(self.removeContact)
        self.comboBox_2.activated.connect(self.clickerContact)
        self.comboBoxEvent.activated.connect(self.clickerEvent)
        self.tableWidget.selectionModel().selectionChanged.connect(self.modifyButton)
        self.error_message = Error()

        self.user = user
        self.loadEvents(self.user.events())
        self.loadContacts(self.user.contacts())
    
    def loadEvents(self, listEvents):
        self.tableWidget.setRowCount(len(listEvents))
        
        for i, event in enumerate(listEvents):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(event.name))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(event.creator))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(event.startdate))
            self.tableWidget.setItem(i, 3, QTableWidgetItem(event.enddate))
            self.tableWidget.setItem(i, 4, QTableWidgetItem(event.location))
            self.tableWidget.setItem(i, 5, QTableWidgetItem(",".join(event.participants)))
            self.tableWidget.setItem(i, 6, QTableWidgetItem(event.description))

        self.tableWidget.resizeColumnsToContents()
        
        return
    
    def modifyButton(self):
        # Check if there are any selected items in the table
        selected = self.tableWidget.selectedItems()
        if selected and self.comboBoxEvent.currentText() == "My events" and len(selected) == 7:
            self.pushButtonModify.setEnabled(True)
        else:
            self.pushButtonModify.setEnabled(False)
    
    def addContact(self):
        userToAdd = self.lineEditAddContact.text()
        if (userToAdd != self.user.displayname):
            r = self.user.addContact(userToAdd)

            if r.status_code == 201:
                print(r.text)  # success OK.
            else:
                self.error_message.textBrowser.clear()
                self.error_message.textBrowser.setText(r.text)
                self.error_message.exec_()

        return
    
    def loadContacts(self, contacts):
        self.listWidget.clear()
        self.listWidget.addItems(contacts)
        return

    def acceptContact(self):
        userToAccept = self.listWidget.currentItem()

        if userToAccept:
            r = self.user.acceptContact(userToAccept.text())

            if r.status_code == 200:
                print(r.text)  # success OK.
                self.listWidget.clear()
                self.loadContacts(self.user.contacts())
            else:
                self.error_message.textBrowser.clear()
                self.error_message.textBrowser.setText(r.text)
                self.error_message.exec_()
        
        return

    def removeContact(self):
        userToRemove = self.listWidget.currentItem()

        if userToRemove:
            r = self.user.removeContact(userToRemove.text())

            if r.status_code == 200:
                print(r.text)  # success OK.
                self.listWidget.clear()
                self.loadContacts(self.user.contacts())
            else:
                self.error_message.textBrowser.clear()
                self.error_message.textBrowser.setText(r.text)
                self.error_message.exec_()
        
        return

    def clickerContact(self):
        if self.comboBox_2.currentText() == "Pending invitations":
            self.loadContacts(self.user.pendingContacts())
            self.pushButtonDeny.setEnabled(True)
            self.pushButtonAcceptInvit.setEnabled(True)
            self.pushButtonDelete.setEnabled(False)
        else:
            self.loadContacts(self.user.contacts())
            self.pushButtonDeny.setEnabled(False)
            self.pushButtonAcceptInvit.setEnabled(False)
            self.pushButtonDelete.setEnabled(True)
    
    def clickerEvent(self):
        if self.comboBoxEvent.currentText() == "My events":
            self.loadEvents(self.user.events())
        else:
            self.loadEvents(self.user.invitedEvents())

    def openCreationEvent(self):
        self.hide()
        self.window_event.exec_()
        self.loadEvents(self.user.events())
        self.show()

    def openSettings(self):
        self.hide()
        self.window_settings.exec_()
        self.show()

    def openModify(self):
        self.hide()
        selected = self.tableWidget.selectedItems()
        eventParticipants = selected[5].text().split(",")
        selectedEvent = EventUser(selected[0].text(), selected[1].text(), eventParticipants, selected[2].text(), selected[3].text(), selected[4].text(),
                                  selected[6].text())
        self.window_modify.loadEventToModify(selectedEvent)
        self.window_modify.exec_()
        self.loadEvents(self.user.events())
        self.show()

class Event(QtWidgets.QDialog, Ui_Event):
    def __init__(self, user):
        super(Event, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.create)
        self.listWidget.itemClicked.connect(self.addContact)
        self.listWidgetParticipants.itemClicked.connect(self.deleteContact)
        self.error_message = Error()

        self.user = user
        self.loadContacts(self.user.contacts())

    def addContact(self):
        item = self.listWidget.currentItem().text()
        self.listWidgetParticipants.addItem(item)

    def deleteContact(self):
        item = self.listWidgetParticipants.currentIndex().row()
        self.listWidgetParticipants.takeItem(item)
    
    def loadContacts(self, contacts):
        self.listWidget.clear()
        self.listWidget.addItems(contacts)
        return

    def create(self):
        self.loadContacts(self.user.contacts())
        participants = [self.listWidgetParticipants.item(x).text() for x in range(self.listWidgetParticipants.count())]
        event = EventUser(self.lineEditName.text(), self.user.displayname, participants, self.dateTimeEditBegin.dateTime().toString(self.dateTimeEditBegin.displayFormat()), 
                      self.dateTimeEditEnd.dateTime().toString(self.dateTimeEditEnd.displayFormat()), 
                      self.lineEditLocation.text(), self.plainTextEdit.toPlainText())
        r = self.user.createEvent(event)

        if r.status_code == 409:
            self.error_message.textBrowser.clear()
            self.error_message.textBrowser.setText(r.text)
            self.error_message.exec_()
        else:
            print(r.text)  # message ok
            self.hide()

class Modify(QtWidgets.QDialog, Ui_Modify):
    def __init__(self, user):
        super(Modify, self).__init__()
        self.setupUi(self)
        self.listWidgetContact.itemClicked.connect(self.addContact)
        self.listWidget.itemClicked.connect(self.deleteContact)
        self.pushButtonDelete.clicked.connect(self.delete)
        self.pushButtonModify.clicked.connect(self.modify)
        self.error_message = Error()

        self.user = user
        self.loadContacts(self.user.contacts())

    def addContact(self):
        item = self.listWidgetContact.currentItem().text()
        self.listWidget.addItem(item)
    
    def loadContacts(self, contacts):
        self.listWidgetContact.clear()
        self.listWidgetContact.addItems(contacts)
        return
    
    def loadEventToModify(self, event_):
        self.event_ = event_
        self.loadContacts(self.user.contacts())
        self.lineEditName.setText(event_.name)
        self.listWidget.addItems(event_.participants)
        self.dateTimeEditBegin.setDateTime(QDateTime(datetime.datetime.strptime(event_.startdate, "%d/%m/%Y %H:%M")))
        self.dateTimeEditEnd.setDateTime(QDateTime(datetime.datetime.strptime(event_.enddate, "%d/%m/%Y %H:%M")))
        self.lineEditLocation.setText(event_.location)
        self.plainTextEdit.setPlainText(event_.description)

    def deleteContact(self):
        item = self.listWidget.currentIndex().row()
        self.listWidget.takeItem(item)

    def delete(self):
        self.lineEditLocation.clear()
        self.lineEditName.clear()
        self.listWidget.clear()
        self.listWidgetContact.clear()
        self.dateTimeEditBegin.clear()
        self.dateTimeEditEnd.clear()
        self.plainTextEdit.clear()
        
        r = self.user.removeEvent(self.event_)

        if r.status_code == 200:
            print(r.text)  # OK
            self.hide()
        else:
            self.error_message.textBrowser.clear()
            self.error_message.textBrowser.setText(r.text)
            self.error_message.exec_()

    def modify(self):
        oldEvent = self.event_
        newParticipants = [self.listWidget.item(x).text() for x in range(self.listWidget.count())]
        newEvent = EventUser(self.lineEditName.text(), self.user, newParticipants, self.dateTimeEditBegin.dateTime().toString(self.dateTimeEditBegin.displayFormat()), 
                      self.dateTimeEditEnd.dateTime().toString(self.dateTimeEditEnd.displayFormat()), 
                      self.lineEditLocation.text(), self.plainTextEdit.toPlainText())
        
        r = self.user.modifyEvent(oldEvent, newEvent)

        if r.status_code == 200:
            print(r.text)  # OK
            self.hide()
        else:
            self.error_message.textBrowser.clear()
            self.error_message.textBrowser.setText(r.text)
            self.error_message.exec_()



class Settings(QtWidgets.QDialog, Ui_Settings):
    def __init__(self, user):
        super(Settings, self).__init__()
        self.setupUi(self)
        self.user = user
        self.pushButtonModifyDisplayname.clicked.connect(self.modifyDisplay)
        self.pushButtonModifyPswd.clicked.connect(self.modifyPswd)

    def checkPassword(self):
        pswd = self.lineEditEnterPswd.text()

    def openButtons(self):
        self.pushButtonModifyDisplayname.setEnabled(True)
        self.pushButtonModifyPswd.setEnabled(True)
        self.lineEditModifyDisplayname.setEnabled(True)
        self.lineEditModifyPswd.setEnabled(True)

    def modifyDisplay(self):
        new_display = self.lineEditModifyDisplayname
        

    def modifyPswd(self):
        new_pswd = self.lineEditModifyPswd()
        


    

"""
    Classe Pop up
"""

class Error(QtWidgets.QDialog, error):
    def __init__(self):
        super(Error, self).__init__()
        self.setupUi(self)
        self.buttonBox.clicked.connect(self.closePopup)

    def closePopup(self):
        self.hide()


def main():
    app = QApplication(sys.argv)
    mainwin = Connexion()
    mainwin.show()
    app.exec_()

if __name__ == '__main__':
    main()