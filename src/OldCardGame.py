from appJar import gui
import sqlite3 as sql
from hashlib import sha256
from random import shuffle

app = gui("Card Game")
directory = ""
db = None
cursor = None

players = ["", ""]

class Card:
    
    def __init__(self, number, bg, fg):
        self.number = number
        self.fg = fg
        self.bg = bg

    def show(self, playerNum):
        name = str(self.number)
        if len(name) == 1:
            name = " "+name
        app.setButton("Game.Cards"+str(playerNum), "\n\n\n      "+name+"      \n\n\n")
        app.setButtonFg("Game.Cards"+str(playerNum), self.fg)
        app.setButtonBg("Game.Cards"+str(playerNum), self.bg)

    def beats(self, other):
        if self.number > other.number:
            return True
        elif other.number > self.number:
            return False
        elif self.fg == other.bg:
            return True
        else:
            return False

    def __str__(self):
        return self.bg + str(self.number)

class Game:
    cards = []
    blankCard = None
    buttonCard = None
    turn = 0
    hands = [None, None]
    scores = [0, 0]
    
    @staticmethod
    def preload():
        app.startSubWindow("Game")
        app.addLabel("Game.Label0", row=0, column=0)
        app.addLabel("Shuffled Deck", row=0, column=1)
        app.addLabel("Game.Label1", row=0, column=2)
        
        app.addButton("Game.Cards0", Game.doNothing, row=1, column=0)
        app.addButton("Game.CardsDrawDeck", Game.revealCard, row=1, column=1)
        app.addButton("Game.Cards1", Game.doNothing, row=1, column=2)
        app.stopSubWindow()

    @staticmethod
    def go():
        Game.cards = []
        Game.scores = [0, 0]
        Game.hands = [None, None]
        for pair in [("red","black"), ("yellow","red"), ("black","yellow")]:
            for i in range(1, 11):
                Game.cards.append(Card(i, pair[0], pair[1]))
        shuffle(Game.cards)
        Game.buttonCard = Card(players[0]+" pick a card...", "grey", "black")
        Game.blankCard = Card("", "grey", "grey")
        app.setLabel("Game.Label0", players[0])
        app.setLabel("Game.Label1", players[1])
        app.setButton("Game.CardsDrawDeck", "\n\n\n"+players[0]+" pick a card...\n\n\n")
        Game.blankCard.show(0)
        Game.blankCard.show(1)
        #Game.buttonCard.show("DrawDeck")
        Game.turn = 0
        app.showSubWindow("Game")

    @staticmethod
    def revealCard(btn=None):
        if Game.turn == 2:
            roundWinner = 0 if Game.hands[0].beats(Game.hands[1]) else 1
            Game.scores[roundWinner] += 2
            if len(Game.cards) == 0:
                gameWinner = 0 if Game.scores[0] > Game.scores[1] else 1
                gameLoser = (gameWinner+1)%2
                cursor.execute("SELECT best FROM users WHERE username=?",(players[gameWinner],))
                if Game.scores[gameWinner] > cursor.fetchone()[0]:
                    cursor.execute("UPDATE users SET best=? WHERE username=?",(Game.scores[gameWinner],players[gameWinner]))
                Game.back()
                app.infoBox("Game Over",
                            players[gameWinner]+" won the game, beating "+players[gameLoser]+" "+str(Game.scores[gameWinner])+":"+str(Game.scores[gameLoser]),
                            "Select Players")
            else:
                app.setButton("Game.CardsDrawDeck", "\n\n\n"+players[0]+" pick a card...\n\n\n")
                Game.blankCard.show(0)
                Game.blankCard.show(1)
            Game.turn = (Game.turn+1)%3
            app.infoBox("Round Winner", players[roundWinner]+" wins this round!", "Game")
        else:
            if Game.turn == 1:
                app.setButton("Game.CardsDrawDeck", "\n\n\n   Continue... \n\n\n")
            else:
                app.setButton("Game.CardsDrawDeck", "\n\n\n"+players[1]+" pick a card...\n\n\n")
            Game.hands[Game.turn] = Game.cards.pop()
            Game.hands[Game.turn].show(Game.turn)
            Game.turn = (Game.turn+1)%3

    @staticmethod
    def doNothing(btn=None):
        pass

    @staticmethod
    def back(btn=None):
        app.hideSubWindow("Game")
        SelectPlayers.resume()

class LeaderBoard:

    resetTable = [["Username", "High Score"]]

    @staticmethod
    def preload():
        app.startSubWindow("Leader Board")
        app.addTable("LeaderBoard.table", LeaderBoard.resetTable)
        app.setStopFunction(LeaderBoard.back)
        app.stopSubWindow()

    @staticmethod
    def go():
        cursor.execute('''
            SELECT username, best FROM users ORDER BY best DESC LIMIT 5
        ''')
        app.replaceAllTableRows("LeaderBoard.table", cursor.fetchall())
        app.showSubWindow("Leader Board")

    @staticmethod
    def back():
        app.hideSubWindow("Leader Board")
        SelectPlayers.resume()

class DeleteAccount:

    @staticmethod
    def preload():
        app.startSubWindow("Delete Account")
        app.addLabelEntry("   Username: ")
        app.addSecretLabelEntry("   Password: ")
        app.addNamedButton("DELETE ACCOUNT", "DeleteAccount.delete", DeleteAccount.delete)
        app.setStopFunction(DeleteAccount.back)
        app.stopSubWindow()
    
    @staticmethod
    def go():
        app.clearAllEntries()
        app.showSubWindow("Delete Account")
    
    @staticmethod
    def delete(btn=None):
        username = app.getEntry("   Username: ")
        password = sha256((username+app.getEntry("   Password: ")).encode()).digest()
        app.clearEntry("   Password: ")
        cursor.execute('''
            SELECT id FROM users WHERE username=? AND password=?
        ''', (username, password))
        userID = cursor.fetchall()
        if len(userID) == 0:
            app.errorBox("Error", "Incorrect username or password.", "Delete Account")
            return
        cursor.execute("DELETE FROM users WHERE username=?",(username,))
        db.commit()
        DeleteAccount.back()
        app.infoBox("Account Deleted","Your account has been deleted!","Select Players")

    @staticmethod
    def back(btn=None):
        app.clearAllEntries()
        app.hideSubWindow("Delete Account")
        SelectPlayers.resume()

class CreateAccount:

    @staticmethod
    def preload():
        app.startSubWindow("Create Account")
        app.addLabelEntry(" Username: ")
        app.addSecretLabelEntry(" Password: ")
        app.addNamedButton("Submit", "CreateAccount.Submit", CreateAccount.authenticate)
        app.setStopFunction(CreateAccount.back)
        app.stopSubWindow()
    
    @staticmethod
    def go():
        app.clearAllEntries()
        app.showSubWindow("Create Account")
    
    @staticmethod
    def authenticate(btn=None):
        username = app.getEntry(" Username: ")
        password = app.getEntry(" Password: ")
        app.clearEntry(" Password: ")
        if len(username) < 3 or len(username) > 20:
            app.errorBox("Error","Usernames must be between 3 and 20 characters long!","Create Account")
            return
        if not username.isalnum():
            app.errorBox("Error","Usernames must contain alphanumeric characters only!","Create Account")
            return
        cursor.execute('''
            SELECT id FROM users WHERE username=?
        ''', (username,))
        if len(cursor.fetchall()) > 0:
            app.errorBox("Error","Username already taken!","Create Account")
            return
        if len(password) < 8:
            app.errorBox("Error","Passwords must be 8 characters or longer!","Create Account")
            return
        password = sha256((username+password).encode()).digest()
        cursor.execute("INSERT INTO users(username,password,best) VALUES(?,?,?)",(username,password,0))
        db.commit()
        CreateAccount.back()
        app.infoBox("Account Created","Your account has been created!","Select Players")

    @staticmethod
    def back(btn=None):
        app.clearAllEntries()
        app.hideSubWindow("Create Account")
        SelectPlayers.resume()

class ChangePassword:

    @staticmethod
    def preload():
        app.startSubWindow("Change Password")
        app.addLabelEntry("  Username: ")
        app.addSecretLabelEntry("  Old Password: ")
        app.addSecretLabelEntry("  New Password: ")
        app.addNamedButton("Submit", "ChangePassword.Submit", ChangePassword.authenticate)
        app.setStopFunction(ChangePassword.back)
        app.stopSubWindow()
    
    @staticmethod
    def go():
        app.clearAllEntries()
        app.showSubWindow("Change Password")
    
    @staticmethod
    def authenticate(btn=None):
        username = app.getEntry("  Username: ")
        oldPassword = sha256((username+app.getEntry("  Old Password: ")).encode()).digest()
        newPassword = app.getEntry("  New Password: ")
        app.clearEntry("  Old Password: ")
        app.clearEntry("  New Password: ")
        cursor.execute('''
            SELECT id FROM users WHERE username=? AND password=?
        ''', (username, oldPassword))
        userID = cursor.fetchall()
        if len(userID) == 0:
            app.errorBox("Error", "Incorrect username or password.", "Change Password")
            return
        if len(newPassword) < 8:
            app.errorBox("Error","Passwords must be 8 characters or longer!","Change Password")
            return
        newPassword = sha256((username+newPassword).encode()).digest()
        cursor.execute("UPDATE users SET password=? WHERE username=?",(newPassword, username))
        db.commit()
        ChangePassword.back()
        app.infoBox("Password Changed","Your password has been changed!","Select Players")

    @staticmethod
    def back(btn=None):
        app.clearAllEntries()
        app.hideSubWindow("Change Password")
        SelectPlayers.resume()

class Login:
    player = ""
    @staticmethod
    def preload():
        app.startSubWindow("Login")
        app.addLabelEntry("Username: ")
        app.addSecretLabelEntry("Password: ")
        app.addNamedButton("Submit", "Login.Submit", Login.authenticate)
        app.setStopFunction(Login.back)
        app.stopSubWindow()
    
    @staticmethod
    def go(btn=None):
        app.clearAllEntries()
        Login.player = int(btn[-1])
        app.showSubWindow("Login")
    
    @staticmethod
    def authenticate(btn=None):
        username = app.getEntry("Username: ")
        password = sha256((username+app.getEntry("Password: ")).encode()).digest()
        app.clearAllEntries()
        cursor.execute('''
            SELECT id FROM users WHERE username=? AND password=?
        ''', (username, password))
        if len(cursor.fetchall()) == 0:
            players[Login.player] = ""
            app.errorBox("Error", "Incorrect username or password.", "Login")
        elif username == players[(Login.player+1)%2]:
            players[Login.player] = ""
            app.errorBox("Error","You can't play against yourself!", "Login")
        else:
            players[Login.player] = username
            Login.back()
    
    @staticmethod
    def back(btn=None):
        app.clearAllEntries()
        app.hideSubWindow("Login")
        SelectPlayers.resume()

class SelectPlayers:

    @staticmethod
    def preload():
        app.startSubWindow("Select Players")
        app.addNamedButton("SELECT PLAYER 0", "SelectPlayers.Player0", SelectPlayers.login, row=0, column=0)
        app.addLabel("SelectPlayers.Username0", "   Username: ", row=1, column=0)
        app.addLabel("SelectPlayers.HighScore0", "   High Score: ", row=2, column=0)
        app.addEmptyLabel("SelectPlayers.Empty0", row=0, column=1)
        app.setLabel("SelectPlayers.Empty0", "     ")
        app.addNamedButton("SELECT PLAYER 1", "SelectPlayers.Player1", SelectPlayers.login, row=0, column=4)
        app.addLabel("SelectPlayers.Username1", "   Username: ", row=1, column=4)
        app.addLabel("SelectPlayers.HighScore1", "   High Score: ", row=2, column=4)
        app.addEmptyLabel("SelectPlayers.Empty1", row=0, column=3)
        app.setLabel("SelectPlayers.Empty1", "     ")
        app.addNamedButton("Play", "SelectPlayers.Play", SelectPlayers.play, row=0, column=2)
        app.addNamedButton("Leader Board", "SelectPlayers.LeaderBoard", SelectPlayers.leaderBoard, row=1, column=2)
        app.addEmptyLabel("SelectPlayers.Empty2", row=2, column=2)
        app.addNamedButton("Change Password", "SelectPlayers.ChangePassword", SelectPlayers.changePassword, row=3, column=2)
        app.addNamedButton("Create Account", "SelectPlayers.CreateAccount", SelectPlayers.createAccount, row=4, column=2)
        app.addNamedButton("Delete Account", "SelectPlayers.DeleteAccount", SelectPlayers.deleteAccount, row=5, column=2)
        app.setStopFunction(SelectPlayers.back)
        app.stopSubWindow()

    @staticmethod
    def go():
        global db
        global cursor
        db = sql.connect(directory+"/users.dbf")
        cursor = db.cursor()
        cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type="table"
                AND name="users"
        ''')
        if len(cursor.fetchall()) == 0:
            cursor.execute('''
                CREATE TABLE users(
                    id          INTEGER PRIMARY KEY,
                    username    VARCHAR(16),
                    password    CHAR(32),
                    best        INTEGER
                )
            ''')
            db.commit()
        app.setButton("SelectPlayers.Player0", "SELECT PLAYER 0")
        app.setLabel("SelectPlayers.Username0", "   Username: ")
        app.setLabel("SelectPlayers.HighScore0", "   High Score: ")
        app.setButton("SelectPlayers.Player1", "SELECT PLAYER 1")
        app.setLabel("SelectPlayers.Username1", "   Username: ")
        app.setLabel("SelectPlayers.HighScore1", "   High Score: ")
        app.showSubWindow("Select Players")

    @staticmethod
    def resume(btn=None):
        if players[0] != "":
            app.setButton("SelectPlayers.Player0", "CHANGE PLAYER 0")
            cursor.execute("SELECT best FROM users WHERE username=?", (players[0],))
            best = cursor.fetchone()[0]
            app.setLabel("SelectPlayers.Username0", "   Username: "+players[0])
            app.setLabel("SelectPlayers.HighScore0","    Best: "+str(best))
        else:
            app.setButton("SelectPlayers.Player0", "SELECT PLAYER 0")
            app.setLabel("SelectPlayers.Username0", "   Username: ")
            app.setLabel("SelectPlayers.HighScore0", "   High Score: ")
        if players[1] != "":
            app.setButton("SelectPlayers.Player1", "CHANGE PLAYER 1")
            cursor.execute("SELECT best FROM users WHERE username=?", (players[1],))
            best = cursor.fetchone()[0]
            app.setLabel("SelectPlayers.Username1", "   Username: "+players[1])
            app.setLabel("SelectPlayers.HighScore1","    Best: "+str(best))
        else:
            app.setButton("SelectPlayers.Player1", "SELECT PLAYER 1")
            app.setLabel("SelectPlayers.Username1", "   Username: ")
            app.setLabel("SelectPlayers.HighScore1", "   High Score: ")
        app.showSubWindow("Select Players")
    
    @staticmethod
    def login(btn=None):
        app.hideSubWindow("Select Players")
        Login.go(btn)

    @staticmethod
    def play(btn=None):
        if players[0] != "" and players[1] != "":
            app.hideSubWindow("Select Players")
            Game.go()
        else:
            app.errorBox("Error","Both users must be logged in!","Select Players")

    @staticmethod
    def changePassword(btn=None):
        app.hideSubWindow("Select Players")
        ChangePassword.go()

    @staticmethod
    def createAccount(btn=None):
        app.hideSubWindow("Select Players")
        CreateAccount.go()

    @staticmethod
    def deleteAccount(btn=None):
        app.hideSubWindow("Select Players")
        DeleteAccount.go()

    @staticmethod
    def leaderBoard(btn=None):
        app.hideSubWindow("Select Players")
        LeaderBoard.go()

    @staticmethod
    def back(btn=None):
        db.commit()
        db.close()
        app.hideSubWindow("Select Players", useStopFunction=False)
        ChooseGame.resume()



class ChooseGame:

    @staticmethod
    def preload():
        app.startSubWindow("Choose Game")
        app.addNamedButton("Select Folder", "ChooseGame.SelectFolder", ChooseGame.selectFolder)
        app.setStopFunction(ChooseGame.stop)
        app.stopSubWindow()

    @staticmethod
    def go():
        app.go(startWindow = "Choose Game")

    @staticmethod
    def resume(btn=None):
        app.showSubWindow("Choose Game")

    @staticmethod
    def stop(btn=None):
        app.stop()
    
    @staticmethod
    def selectFolder(btn=None):
        global directory
        directory = app.directoryBox(title="Select Folder")
        if directory != None:
            app.hideSubWindow("Choose Game")
            SelectPlayers.go()

ChooseGame.preload()
SelectPlayers.preload()
Login.preload()
ChangePassword.preload()
CreateAccount.preload()
DeleteAccount.preload()
LeaderBoard.preload()
Game.preload()

ChooseGame.go()

