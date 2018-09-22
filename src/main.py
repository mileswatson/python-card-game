import appJar
import sqlite3 as sql
from hashlib import sha256

app = appJar.gui("Cardography")
directory = ""
db = None
player1 = "1"
player2 = "2"

def dummy(btn=None):
    ChooseGame.stop()

class ChooseAuthentication:

    btn = ""

    @staticmethod
    def preload():
        app.startSubWindow("ChooseAuthentication", modal=True)
        app.addNamedButton("Login", "ChooseAuthentication.Login", ChooseAuthentication.back)
        app.addNamedButton("Cancel","ChooseAuthentication.Cancel", ChooseAuthentication.back)
        app.setStopFunction(ChooseAuthentication.back)
        app.stopSubWindow()

    @staticmethod
    def go(btn=None):
        ChooseAuthentication.btn = btn
        app.showSubWindow("ChooseAuthentication")
    
    @staticmethod
    def resume(btn=None):
        pass
    
    @staticmethod
    def back(btn=None):
        app.hideSubWindow("ChooseAuthentication")
        if btn == "ChooseAuthentication.Login":
            SelectPlayers.resume(ChooseAuthentication.btn)
        else:
            SelectPlayers.resume(None)


class SelectPlayers:

    @staticmethod
    def preload():
        app.startSubWindow("Select Players")
        app.addNamedButton("", "SelectPlayers.Player1", ChooseAuthentication.go)
        app.addLabel("SelectPlayers.Username1", "   Username: ")
        app.addLabel("SelectPlayers.HighScore1", "   High Score: ")
        app.addEmptyLabel("SelectPlayers.Empty1")
        app.addNamedButton("", "SelectPlayers.Player2", ChooseAuthentication.go)
        app.addLabel("SelectPlayers.Username2", "   Username: ")
        app.addLabel("SelectPlayers.HighScore2", "   High Score: ")
        app.addEmptyLabel("SelectPlayers.Empty2")
        app.addButton("Back", SelectPlayers.back)
        app.setStopFunction(SelectPlayers.back)
        app.stopSubWindow()

    @staticmethod
    def go():
        global db
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
                    username    TEXT,
                    password    CHAR(32),
                    best        INTEGER,
                    used        INTEGER
                )
            ''')
            db.commit()
        app.setButton("SelectPlayers.Player1", "")
        app.setButton("SelectPlayers.Player2", "")
        app.showSubWindow("Select Players")
    
    @staticmethod
    def resume(btn=None):
        if btn != None:
            app.setButton(btn, player1 if btn[-1] == "1" else player2)
            
    
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
ChooseAuthentication.preload()

ChooseGame.go()