import appJar
from hashlib import sha256
import sqlite3 as sql
import os
import random

app = appJar.gui("Card Game")

def errorBox(title, contents, focus):
    try:
        app.errorBox(title, contents, focus)
    except:
        pass

def infoBox(title, contents, focus):
    try:
        app.infoBox(title, contents, focus)
    except:
        pass

class Database:

    def __init__(self, directory):
        self.connection = sql.connect(directory+"/users.dbf")
        self.cursor = self.connection.cursor()
        self.cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type="table"
                AND name="users"
        ''')
        if len(self.cursor.fetchall()) == 0:
            self.cursor.execute('''
                CREATE TABLE users(
                    id                  INTEGER PRIMARY KEY,
                    username            VARCHAR(16),
                    password            CHAR(32),
                    salt                CHAR(32),
                    cards               INTEGER
                )
            ''')
            self.connection.commit()

    def createUser(self, username, password, salt):
        self.cursor.execute('''
            INSERT INTO users(username,password,salt,cards) VALUES(?,?,?,0)
        ''',(username, password, salt))
        self.connection.commit()

    def changePassword(self, username, password):
        self.cursor.execute('''
            UPDATE users SET password=? WHERE username=?
        ''',(password, username))
        self.connection.commit()

    def deleteUser(self, username):
        self.cursor.execute('''
            DELETE FROM users WHERE username=?
        ''',(username,))
        self.connection.commit()

    def userExists(self, username):
        self.cursor.execute('''
            SELECT id FROM users WHERE username=?
        ''', (username,))
        return len(self.cursor.fetchall())==1

    def getCards(self, username):
        self.cursor.execute('''
            SELECT cards FROM users WHERE username=?
        ''', (username,))
        answer = self.cursor.fetchone()
        if answer == None:
            return -1
        else:
            return answer[0]

    def getAuthInfo(self, username):
        self.cursor.execute('''
            SELECT password, salt FROM users WHERE username=?
        ''', (username,))
        return self.cursor.fetchone()

    def getTopFive(self):
        self.cursor.execute('''
            SELECT username, cards FROM users ORDER BY cards DESC LIMIT 5
        ''')
        return self.cursor.fetchall()

    def addCards(self, username, cards):
        self.cursor.execute('''
            UPDATE users SET cards=cards+? WHERE username=?
        ''',(cards, username))
        self.connection.commit()

    def close(self):
        self.connection.close()

class Widget:

    def __init__(self, widgetType, name, label="", row=0, col=0, colspan=1, special=None, fg=None, bg=None):
        self.type = widgetType
        self.window = sha256(b'').hexdigest()
        self.name = name
        self.id = self.window + "." + self.name
        self.label = label
        self.row = row
        self.col = col
        self.special = special
        self.fg = fg
        self.bg = bg

    def setWindow(self, window):
        self.window = sha256(window.name.encode()).hexdigest()
        self.id = self.window + "." + self.name
        if self.type == "button":
            app.addButton(self.id,self.special,row=self.row, column=self.col)
            app.setButton(self.id, self.label)
            app.setButtonFg(self.id, self.fg)
            app.setButtonBg(self.id, self.bg)
        elif self.type == "label":
            app.addLabel(self.id, row=self.row, column=self.col)
            app.setLabel(self.id, self.label)
            app.setLabelFg(self.id, self.fg)
            app.setLabelBg(self.id, self.bg)
        elif self.type == "entry":
            if self.special == "secret":
                app.addSecretEntry(self.id, row=self.row, column=self.col)
            else:
                app.addEntry(self.id, row=self.row, column=self.col)
        elif self.type == "table":
            app.addTable(self.id, self.special)

    def setLabel(self, text):
        self.label = text
        if self.type == "button":
            app.setButton(self.id, self.label)
        elif self.type == "label":
            app.setLabel(self.id, self.label)

    def changeBackground(self, color):
        self.bg = color
        if self.type == "button":
            app.setButtonBg(self.id, self.bg)
        elif self.type == "label":
            app.setLabelBg(self.id, self.bg)

    def changeForeground(self, color):
        self.fg = color
        if self.type == "button":
            app.setButtonFg(self.id, self.fg)
        elif self.type == "label":
            app.setLabelFg(self.id, self.fg)

class Label(Widget):

    def __init__(self, name, label, row=0, col=0, colspan=1, fg=None, bg=None):
        super().__init__(
            widgetType="label",
            name=name,
            label=label,
            row=row,
            col=col,
            colspan=colspan,
            special=None,
            fg=fg,
            bg=bg
        )

class Button(Widget):

    def __init__(self, name, label, btn, row=0, col=0, colspan=1, fg=None, bg=None):
        super().__init__(
            widgetType="button",
            name=name,
            label=label,
            row=row,
            col=col,
            colspan=colspan,
            special=btn,
            fg=fg,
            bg=bg
        )

class Entry(Widget):

    def __init__(self, name, entryType="normal", row=0, col=0, colspan=1, fg=None, bg=None):
        super().__init__(
            widgetType="entry",
            name=name,
            row=row,
            col=col,
            colspan=colspan,
            special=entryType,
            fg=fg,
            bg=bg
        )

    def getEntry(self):
        return app.getEntry(self.id)

    def clearEntry(self):
        store = app.getEntry(self.id)
        app.clearEntry(self.id)
        return store

class Table(Widget):

    def __init__(self, name, columns, row=0, col=0, colspan=1, fg=None, bg=None):
        super().__init__(
            widgetType="table",
            name=name,
            row=row,
            col=col,
            colspan=colspan,
            special=[columns],
            fg=fg,
            bg=bg
        )

    def fill(self, rows):
        app.replaceAllTableRows(self.id, rows)

class Window:
    
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.widgets = dict()
        self.children = dict()
        
    def preload(self, widgets, children):
        self.children = {child.name:child for child in children}
        self.widgets = {widget.name:widget for widget in widgets}
        app.startSubWindow(self.name)
        app.setStopFunction(self.back)
        for name in self.widgets:
            self.widgets[name].setWindow(self)
        app.stopSubWindow()
        
    def go(self, parent=None):
        self.parent = parent
        app.showSubWindow(self.name)

    def getChild(self, childName):
        return self.children[childName]

    def getWidget(self, widgetName):
        return self.widgets[widgetName]

    def switch(self, childName):
        app.hideSubWindow(self.name)
        self.children[childName].go(self)

    def resume(self):
        app.showSubWindow(self.name)

    def back(self):
        app.hideSubWindow(self.name)
        if self.parent == None:
            app.stop()
            quit()
        else:
            self.parent.resume()

class ChooseGame(Window):

    def selectFolder(self):
        directory = app.directoryBox(title="Select Folder")
        if directory != None:
            self.getChild("Select Players").setDirectory(directory)
            self.switch("Select Players")

class SelectPlayers(Window):

    def __init__(self, name):
        super().__init__(name)
        self.directory = ""
        self.db = None
        self.players = ["", ""]

    def go(self, parent=None):
        self.db = Database(self.directory)
        self.resetPlayer(0)
        self.resetPlayer(1)
        super().go(parent)

    def resume(self):
        if self.players[0] == "":
            self.resetPlayer(0)
        else:
            cards = self.db.getCards(self.players[0])
            self.setPlayer(0, cards)
        if self.players[1] == "":
            self.resetPlayer(1)
        else:
            cards = str(self.db.getCards(self.players[1]))
            self.setPlayer(1, cards)
        super().resume()

    def back(self):
        self.db.close()
        super().back()

    def resetPlayer(self, num):
        num = str(num)
        self.getWidget("Player"+num).setLabel("SELECT PLAYER")
        self.getWidget("Username"+num).setLabel("")
        self.getWidget("Total"+num).setLabel("")

    def setPlayer(self, num, cards):
        string = str(num)
        self.getWidget("Username"+string).setLabel(self.players[num])
        self.getWidget("Total"+string).setLabel(str(cards))

    def setDirectory(self, directory):
        self.directory = directory

    def setUsername(self, slot, username):
        self.players[slot] = username

    def login(self, btn=None):
        self.getChild("Login").setSlot(int(btn[-1]))
        self.switch("Login")

    def play(self, btn=None):
        if self.players[0] == "" or self.players[1] == "":
            errorBox(
                "Error",
                "Both players must be logged in!",
                self.name
            )
        else:
            self.switch("Game")

    def leaderboard(self, btn=None):
        self.switch("Leaderboard")

    def create(self, btn=None):
        self.switch("Create Account")

    def change(self, btn=None):
        self.switch("Change Password")

    def delete(self, btn=None):
        self.switch("Delete Account")
        
class Login(Window):

    def __init__(self, name):
        super().__init__(name)
        self.slot = 0

    def setSlot(self, num):
        self.slot = num

    def go(self, parent):
        super().go(parent)
        self.parent.players[self.slot] = ""

    def authenticate(self, btn=None):
        username = self.getWidget("UsernameEntry").getEntry()
        enteredPassword = sha256(self.getWidget("PasswordEntry").clearEntry().encode()).digest()
        if username == self.parent.players[(self.slot+1)%2]:
            errorBox(
                "Error",
                "You can't play against yourself!",
                self.name
            )
            return
        if self.parent.db.userExists(username):
            actualPassword, salt = self.parent.db.getAuthInfo(username)
            enteredPassword = sha256(salt + enteredPassword).digest()
            if enteredPassword == actualPassword:
                app.clearAllEntries()
                self.parent.setUsername(self.slot, username)
                self.back()
                return
        errorBox(
            "Error",
            "Incorrect username or password!",
            self.name
        )
        
class CreateAccount(Window):

    def create(self, btn=None):
        username = self.getWidget("UsernameEntry").getEntry()
        password = self.getWidget("PasswordEntry").clearEntry()
        if len(username) < 3 or len(username) > 20:
            errorBox(
                "Error",
                "Usernames must be between 3 and 20 characters long!",
                self.name
            )
            return
        if not username.isalnum():
            errorBox(
                "Error",
                "Usernames must contain alphanumeric characters only!",
                self.name
            )
            return
        if self.parent.db.userExists(username):
            errorBox(
                "Error",
                "Username is already taken!",
                self.name
            )
            return
        if len(password) < 8:
            errorBox(
                "Error",
                "Passwords must be 8 characters or longer!",
                self.name
            )
        salt = os.urandom(32)
        password = sha256(password.encode()).digest()
        password = sha256(salt+password).digest()
        self.parent.db.createUser(username, password, salt)
        self.back()
        app.infoBox(
            "Account Created",
            "Your account has been created!",
            self.parent.name
        )

class ChangePassword(Window):

    def change(self, btn=None):
        username = self.getWidget("UsernameEntry").getEntry()
        oldPassword = sha256(self.getWidget("OldPasswordEntry").clearEntry().encode()).digest()
        newPassword = self.getWidget("NewPasswordEntry").clearEntry()
        if self.parent.db.userExists(username):
            password, salt = self.parent.db.getAuthInfo(username)
            oldPassword = sha256(salt+oldPassword).digest()
            if oldPassword == password:
                if len(newPassword) < 8:
                    errorBox(
                        "Error",
                        "Passwords must be 8 characters or longer!",
                        self.name
                    )
                    return
                newPassword = sha256(newPassword.encode()).digest()
                newPassword = sha256(salt+newPassword).digest()
                self.parent.db.changePassword(username, newPassword)
                self.back()
                infoBox(
                    "Password Changed",
                    "Your password has been changed successfully!",
                    self.parent.name
                )
        errorBox(
            "Error",
            "Incorrect username or password!",
            self.name
        )

class DeleteAccount(Window):

    def delete(self, btn=None):
        username = self.getWidget("UsernameEntry").getEntry()
        enteredPassword = sha256(self.getWidget("PasswordEntry").clearEntry().encode()).digest()
        if self.parent.db.userExists(username):
            actualPassword, salt = self.parent.db.getAuthInfo(username)
            enteredPassword = sha256(salt + enteredPassword).digest()
            if enteredPassword == actualPassword:
                app.clearAllEntries()
                self.parent.db.deleteUser(username)
                if self.parent.players[0] == username:
                    self.parent.players[0] = ""
                if self.parent.players[1] == username:
                    self.parent.players[1] = ""
                self.back()
                infoBox(
                    "Account Deleted",
                    "Your account has been deleted successfully!",
                    self.parent.name
                )
                return
        errorBox(
            "Error",
            "Incorrect username or password!",
            self.name
        )

class Leaderboard(Window):

    def go(self, parent):
        super().go(parent)
        data = self.parent.db.getTopFive()
        self.getWidget("Table").fill(data)

class Game(Window):

    def __init__(self, name):
        super().__init__(name)
        self.cards = []
        self.drawn = [None, None]
        self.hands = [[], []]
        self.turn = 0
        self.blankCard = Card("", "grey", "grey")

    def go(self, parent):
        super().go(parent)
        self.cards = []
        self.drawn = [None, None]
        self.hands = [[],[]]
        for pair in [("red", "black"),("yellow", "red"),("black", "yellow")]:
            for i in range(1, 11):
                self.cards.append(Card(i, pair[0], pair[1]))
        random.shuffle(self.cards)
        self.getWidget("Player0").setLabel(self.parent.players[0])
        self.getWidget("Player1").setLabel(self.parent.players[1])
        self.getWidget("DrawDeck").setLabel(self.parent.players[0]+" pick a card...")
        self.blankCard.show(self.getWidget("Card0"))
        self.blankCard.show(self.getWidget("Card1"))
        self.turn = 0

    def revealCard(self, btn=None):
        if self.turn == 2:
            roundWinner = 0 if self.drawn[0] > self.drawn[1] else 1
            self.hands[roundWinner] += self.drawn
            self.drawn = [None, None]
            if len(self.cards) == 0:
                gameWinner = 0 if len(self.hands[0]) > len(self.hands[1]) else 1
                gameLoser = (gameWinner+1)%2
                self.parent.db.addCards(
                    self.parent.players[gameWinner],
                    len(self.hands[gameWinner])
                )
                self.back()
                infoBox(
                    "Game Over",
                    self.parent.players[gameWinner]+" won the game, beating "
                    +self.parent.players[gameLoser]+" "
                    +str(len(self.hands[gameWinner]))+":"
                    +str(len(self.hands[gameLoser]))+" .",
                    self.parent.name
                )
                return
            else:
                self.getWidget("DrawDeck").setLabel(self.parent.players[0]+" pick a card...")
                self.blankCard.show(self.getWidget("Card0"))
                self.blankCard.show(self.getWidget("Card1"))
            self.turn = 0
            infoBox(
                "Round Winner",
                self.parent.players[roundWinner]+" wins this round!",
                self.name
            )
        else:
            if self.turn == 1:
                self.getWidget("DrawDeck").setLabel("Continue...")
            else:
                self.getWidget("DrawDeck").setLabel(self.parent.players[1]+" pick a card...")
            self.drawn[self.turn] = self.cards.pop()
            self.drawn[self.turn].show(self.getWidget("Card"+str(self.turn)))
            self.turn = self.turn + 1

    def doNothing():
        pass
    
class Card:

    def __init__(self, number, bg, fg):
        self.number = number
        self.fg = fg
        self.bg = bg

    def show(self, widget):
        text = str(self.number)
        if len(text) == 1:
            text = " "+text
        widget.setLabel(text)
        widget.changeForeground(self.fg)
        widget.changeBackground(self.bg)

    def __gt__(self, other):
        if self.fg == other.bg:
            return True
        elif other.fg ==  self.bg:
            return False
        elif self.number > other.number:
            return True
        else:
            return False

    def __str__(self):
        return self.bg + str(self.number)
        

chooseGame = ChooseGame("Choose Game")
selectPlayers = SelectPlayers("Select Players")
login = Login("Login")
createAccount = CreateAccount("Create Account")
changePassword = ChangePassword("Change Password")
deleteAccount = DeleteAccount("Delete Account")
leaderboard = Leaderboard("Leaderboard")
game = Game("Game")

game.preload(
    [
        Label("Player0", "", row=0, col=0),
        Label("ShuffledDeck", "Shuffled Deck", row=0, col=1),
        Label("Player1", "", row=0, col=2),

        Button("Card0", "", game.doNothing, row=1, col=0),
        Button("DrawDeck", "", game.revealCard, row=1, col=1),
        Button("Card1", "", game.doNothing, row=1, col=2)
    ],
    []
)

leaderboard.preload(
    [
        Table("Table", ["Username", "Total Cards"])
    ],
    []
)

deleteAccount.preload(
    [
        Label("UsernameLabel", "Username: ", row=0, col=0),
        Entry("UsernameEntry", row=0, col=1),
        Label("PasswordLabel", "Password: ", row=1, col=0),
        Entry("PasswordEntry", entryType="secret", row=1, col=1),
        Button("DeleteButton", "Delete", deleteAccount.delete, row=2, col=0)
    ],
    []
)

changePassword.preload(
    [
        Label("UsernameLabel", "Username: ", row=0, col=0),
        Entry("UsernameEntry", row=0, col=1),
        Label("OldPasswordLabel", "Old Password: ", row=1, col=0),
        Entry("OldPasswordEntry", entryType="secret", row=1, col=1),
        Label("NewPasswordLabel", "New Password: ", row=2, col=0),
        Entry("NewPasswordEntry", entryType="secret", row=2, col=1),
        Button("ChangeButton", "Change Password", changePassword.change, row=3, col=0)    
    ],
    []
)

createAccount.preload(
    [
        Label("UsernameLabel", "Username: ", row=0, col=0),
        Entry("UsernameEntry", row=0, col=1),
        Label("PasswordLabel", "Password: ", row=1, col=0),
        Entry("PasswordEntry", entryType="secret", row=1, col=1),
        Button("CreateButton", "Create Account", createAccount.create, row=2, col=0)
    ],
    []
)

login.preload(
    [
        Label("UsernameLabel", "Username: ", row=0, col=0),
        Entry("UsernameEntry", row=0, col=1),
        Label("PasswordLabel", "Password: ", row=1, col=0),
        Entry("PasswordEntry", entryType="secret", row=1, col=1),
        Button("LoginButton", "Login", login.authenticate, row=2, col=0)
    ],
    []
)

selectPlayers.preload(
    [
        Button("Player0", "SELECT PLAYER", selectPlayers.login, row=0, col=0, colspan=2),
        Label("UsernameLabel0", "   Username: ", row=1, col=0),
        Label("Username0", "", row=1, col=1),
        Label("TotalLabel0", "  Total Cards: ", row=2, col=0),
        Label("Total0", "", row=2, col=1),

        Button("Play", "Play", selectPlayers.play, row=0, col=4),
        Button("Leaderboard", "Leaderboard", selectPlayers.leaderboard, row=1, col=4),

        Button("CreateAccount", "Create Account", selectPlayers.create, row=3, col=4),
        Button("ChangePassword", "Change Password", selectPlayers.change, row=4, col=4),
        Button("DeleteAccount", "Delete Account", selectPlayers.delete, row=5, col=4),
        
        
        
        Button("Player1", "SELECT PLAYER", selectPlayers.login, row=0, col=6, colspan=2),
        Label("UsernameLabel1", "   Username:", row=1, col=6),
        Label("Username1", "", row=1, col=7),
        Label("TotalLabel1", "  Total Cards: ", row=2, col=6),
        Label("Total1", "", row=2, col=7),
    ],
    [
        login,
        createAccount,
        changePassword,
        deleteAccount,
        leaderboard,
        game
    ]
)

chooseGame.preload(
    [
        Button("SelectFolderButton", "Select Folder", chooseGame.selectFolder, row=1)
    ],
    [
        selectPlayers
    ]
)

chooseGame.go()
