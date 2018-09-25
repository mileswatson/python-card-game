import appJar
import sqlite3 as sql
from hashlib import sha256

app = appJar.gui("Cardography")
directory = ""
db = None
cursor = None

players = [-1, -1]

class Signup:

    @staticmethod
    def preload():
        app.startSubWindow("Signup")
        app.addLabelEntry(" Username: ")
        app.addSecretLabelEntry("First password: ")
        app.addSecretLabelEntry("Second password: ")
        app.addNamedButton("Submit", "Login.Submit", Signup.authenticate)
        app.setStopFunction(Signup.back)
        app.stopSubWindow()
    
    @staticmethod
    def go():
        app.clearAllEntries()
        app.showSubWindow("Signup")
    
    def authenticate(btn=None):
        username = app.getEntry(" Username: ")
        #################################################################

class Login:
    player = -1
    @staticmethod
    def preload():
        app.startSubWindow("Login")
        app.addLabelEntry("Username: ")
        #app.setEntryDefault("Login.Username", "Username")
        app.addSecretLabelEntry("Password: ")
        #app.setEntryDefault("Login.Password", "Password")
        app.addNamedButton("Submit", "Login.Submit", Login.authenticate)
        app.setStopFunction(Login.back)
        app.stopSubWindow()
    
    @staticmethod
    def go(btn=None):
        app.clearAllEntries()
        Login.player = int(btn[-1])
        #print("player", Login.player)
        app.showSubWindow("Login")
    
    @staticmethod
    def authenticate(btn=None):
        username = app.getEntry("Username: ")
        password = sha256((username+app.getEntry("Password: ")).encode()).digest()
        app.clearAllEntries()
        cursor.execute('''
            SELECT id FROM users WHERE username=? AND password=?
        ''', (username, password))
        players[Login.player] = cursor.fetchone()[0]
        if players[Login.player] == None or players[Login.player] == players[(Login.player+1)%2]:
            players[Login.player] = -1
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
        app.addNamedButton("", "SelectPlayers.Player0", SelectPlayers.login)
        app.addLabel("SelectPlayers.Username0", "   Username: ")
        app.addLabel("SelectPlayers.HighScore0", "   High Score: ")
        app.addEmptyLabel("SelectPlayers.Empty0")
        app.addNamedButton("", "SelectPlayers.Player1", SelectPlayers.login)
        app.addLabel("SelectPlayers.Username1", "   Username: ")
        app.addLabel("SelectPlayers.HighScore1", "   High Score: ")
        app.addEmptyLabel("SelectPlayers.Empty1")
        app.addNamedButton("Back", "SelectPlayers.Back", SelectPlayers.back)
        app.setStopFunction(SelectPlayers.back)
        app.stopSubWindow()

    @staticmethod
    def go():
        global db
        global cursor
        db = sql.connect(directory+"/"+"users.dbf")
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
        app.setButton("SelectPlayers.Player0", "")
        app.setLabel("SelectPlayers.Username0", "   Username: ")
        app.setLabel("SelectPlayers.HighScore0", "   High Score: ")
        app.setButton("SelectPlayers.Player1", "")
        app.setLabel("SelectPlayers.Username1", "   Username: ")
        app.setLabel("SelectPlayers.HighScore1", "   High Score: ")
        app.showSubWindow("Select Players")
    
    @staticmethod
    def login(btn=None):
        app.hideSubWindow("Select Players")
        Login.go(btn)

    @staticmethod
    def resume(btn=None):
        if players[0] >= 0:
            app.setButton("SelectPlayers.Player0", "Authenticated")
            cursor.execute("SELECT username, best FROM users WHERE id=?", (players[0],))
            username, best = cursor.fetchone()
            app.setLabel("SelectPlayers.Username0", "   Username: "+username)
            app.setLabel("SelectPlayers.HighScore0","    Best: "+str(best))
        else:
            app.setButton("SelectPlayers.Player0", "")
            app.setLabel("SelectPlayers.Username0", "   Username: ")
            app.setLabel("SelectPlayers.HighScore0", "   High Score: ")
        if players[1] >= 0:
            app.setButton("SelectPlayers.Player1", "Authenticated")
            cursor.execute("SELECT username, best FROM users WHERE id=?", (players[1],))
            username, best = cursor.fetchone()
            app.setLabel("SelectPlayers.Username1", "   Username: "+username)
            app.setLabel("SelectPlayers.HighScore1","    Best: "+str(best))
        else:
            app.setButton("SelectPlayers.Player1", "")
            app.setLabel("SelectPlayers.Username1", "   Username: ")
            app.setLabel("SelectPlayers.HighScore1", "   High Score: ")
        app.showSubWindow("Select Players")
    
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
        app.addNamedButton("Exit", "ChooseGame.Exit", ChooseGame.stop)
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

ChooseGame.go()