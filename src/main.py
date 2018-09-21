import appJar as aj
import sqlite3 as sql

app = aj.gui("Cardography")
directory = ""
db = None

class UserLogin:

    @staticmethod
    def go(path):
        global db
        db = sql.connect(path+"/"+"users.dbf")
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
                    best        INTEGER
                )
            ''')
            db.commit()
        
        app.startSubWindow("Login")
        app.addLabelEntry("Username: ")
        app.addSecretLabelEntry("Password: ")
        app.stopSubWindow()
        app.showSubWindow("Login")



class ChooseGame:

    @staticmethod
    def go():
        app.startSubWindow("Choose")
        app.addButton("Select Folder", ChooseGame.choose)
        app.addButton("Exit", ChooseGame.stop)
        app.setStopFunction(ChooseGame.stop)
        app.stopSubWindow()
        app.go(startWindow = "Choose")

    @staticmethod
    def choose(btn=None):
        global directory
        directory = app.directoryBox(
            title="Select Folder"
        )
        if directory != None:
            app.hideSubWindow("Choose")
            UserLogin.go(directory)

    @staticmethod
    def resume(btn=None):
        app.showSubWindow("Choose")

    @staticmethod
    def stop(btn=None):
        print("here")
        app.stop()

ChooseGame.go()