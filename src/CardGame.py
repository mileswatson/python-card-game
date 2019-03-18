# GUI library
import appJar

# SHA-2 algorithm for hashing passwords
from hashlib import sha256

# serverless python database
import sqlite3 as sql

# allows the use of os.urandom, a cryptographically secure RNG (it is more secure than the usual psuedo-RNG)
import os

# faster, crypto-insecure RNG
import random

# creates the GUI object
app = appJar.gui("Card Game")

# function for creating an error box, handles the annoying appJar error on closing the window
def errorBox(title, contents, focus):
    try:
        app.errorBox(title, contents, focus)
    except:
        pass

# function for creating an info box, handles the annoying appJar error on closing the window
def infoBox(title, contents, focus):
    try:
        app.infoBox(title, contents, focus)
    except:
        pass

# a class that manages the database connection
class Database:

    # run on object construction
    def __init__(self, directory):

        # connect to the database, and store the connection in a property
        self.connection = sql.connect(directory+"/users.dbf")

        # creates a handle for accessing the database
        self.cursor = self.connection.cursor()

        # returns the names of all tables called users, to see whether one exists
        self.cursor.execute('''
            SELECT name FROM sqlite_master
            WHERE type="table"
                AND name="users"
        ''')

        # creates a table if there is no existing table called "users"
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

    # adds a user to the database
    def createUser(self, username, password, salt):

        # SQL command to add user to database using the handle
        self.cursor.execute('''
            INSERT INTO users(username,password,salt,cards) VALUES(?,?,?,0)
        ''',(username, password, salt))

        # saves changes
        self.connection.commit()

    # changes the password of a user in a database
    def changePassword(self, username, password):

        # SQL command to change the password of a user in the databse
        self.cursor.execute('''
            UPDATE users SET password=? WHERE username=?
        ''',(password, username))

        # saves changes
        self.connection.commit()

    # deletes user from databse
    def deleteUser(self, username):

        # SQL command to delete a user from "users" table
        self.cursor.execute('''
            DELETE FROM users WHERE username=?
        ''',(username,))

        # saves change
        self.connection.commit()

    # checks whether a user exists
    def userExists(self, username):

        # SQL command to get the ID's of all users with a particular username
        self.cursor.execute('''
            SELECT id FROM users WHERE username=?
        ''', (username,))

        # returns True if a user exists with the given username
        return len(self.cursor.fetchall())==1

    # returns the number of cards held by a given user
    def getCards(self, username):

        # SQL command to get the number of cards for a given username
        self.cursor.execute('''
            SELECT cards FROM users WHERE username=?
        ''', (username,))

        # fetches the number of cards stored in the database handle
        answer = self.cursor.fetchone()

        # returns -1 if username was not in the database, otherwise returns the number of cards
        if answer == None:
            return -1
        else:
            return answer[0]

    # gets the hashed password and salt of a given user, and returns them in a tuple
    def getAuthInfo(self, username):

        # SQL command to get password and salt for a particular username
        self.cursor.execute('''
            SELECT password, salt FROM users WHERE username=?
        ''', (username,))

        # returns password and salt as a tuple
        return self.cursor.fetchone()

    # gets the five users with the most amount of cards, from largest to smallest
    def getTopFive(self):
        
        # SQL command to get 5 username and cards pairs that have the greatest number of cards
        self.cursor.execute('''
            SELECT username, cards FROM users ORDER BY cards DESC LIMIT 5
        ''')
        
        # returns the username and number of cards as a tuple
        return self.cursor.fetchall()

    # adds a number to the cards value of a given user
    def addCards(self, username, cards):

        # SQL command to add a number to the cards field for a particular user
        self.cursor.execute('''
            UPDATE users SET cards=cards+? WHERE username=?
        ''',(cards, username))

        # save the database
        self.connection.commit()

    # closes the connection
    def close(self):
        self.connection.close()

# a class that represents a GUI item, such as a label or an entry
class Widget:

    # run on construction, sets default values if they are left
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

    # adds the widget to a window
    def setWindow(self, window):

        # sets the window property to the hex encoded hash of the window name
        self.window = sha256(window.name.encode()).hexdigest()

        # combines the name of the window and itself to give an ID
        self.id = self.window + "." + self.name

        # uses the various different functions for each widget type
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

    # sets the label of the widget
    def setLabel(self, text):
        
        self.label = text

        # uses different functions for each widget type
        if self.type == "button":
            app.setButton(self.id, self.label)
        elif self.type == "label":
            app.setLabel(self.id, self.label)

    # changes the background of a widget to a given colour
    def changeBackground(self, color):
        
        self.bg = color

        # uses diggerent functions for each widget type
        if self.type == "button":
            app.setButtonBg(self.id, self.bg)
        elif self.type == "label":
            app.setLabelBg(self.id, self.bg)

    # changes the background of a widget to a given colour
    def changeForeground(self, color):
        
        self.fg = color
        
        # uses diggerent functions for each widget type
        if self.type == "button":
            app.setButtonFg(self.id, self.fg)
        elif self.type == "label":
            app.setLabelFg(self.id, self.fg)

# a label class that extends the widget class
class Label(Widget):

    # constructor for a label
    def __init__(self, name, label, row=0, col=0, colspan=1, fg=None, bg=None):

        # runs the constructor for its parent class (the Widget constructor)
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

# a button class that extends the widget class
class Button(Widget):

    # constructor for a button
    def __init__(self, name, label, btn, row=0, col=0, colspan=1, fg=None, bg=None):

        # runs the constructor for its parent class (the Widget constructor)
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

# an entry class that extends the widget class
class Entry(Widget):

    # constructor for an entry
    def __init__(self, name, entryType="normal", row=0, col=0, colspan=1, fg=None, bg=None):

        # runs the constructor for its parent class (the Widget constructor)
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

    # returns the text a user entered into the entrybox
    def getEntry(self):
        return app.getEntry(self.id)

    # clears the text that was entered into the entry, returning the cleared value
    def clearEntry(self):
        store = app.getEntry(self.id)
        app.clearEntry(self.id)
        return store

# a table class that extends the widget class
class Table(Widget):

    # constructor for a table object
    def __init__(self, name, columns, row=0, col=0, colspan=1, fg=None, bg=None):

        # runs the constructor for its parent class (the Widget constructor)
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

    # fills the table with the given rows
    def fill(self, rows):
        app.replaceAllTableRows(self.id, rows)

# a window template for representing a window in the GUI
class Window:

    # default constructor for the window class
    def __init__(self, name):
        self.name = name
        self.parent = None
        self.widgets = dict()
        self.children = dict()

    # preloads the window to improve performance
    def preload(self, widgets, children):

        # creates a dictionary linking a child window name to a window object
        self.children = {child.name:child for child in children}

        # creates a dictionary linking widget names to widget objects
        self.widgets = {widget.name:widget for widget in widgets}

        # tells appJar that we are describing this particular window
        app.startSubWindow(self.name)

        # will run self.back when the window is closed
        app.setStopFunction(self.back)

        # adds each widget to the window
        for name in self.widgets:
            self.widgets[name].setWindow(self)

        # tells appJar that we have finished describing the window
        app.stopSubWindow()

    # run when the parent window wants to switch to this window
    def go(self, parent=None):
        self.parent = parent
        app.showSubWindow(self.name)

    # gets the window of a child given a name
    def getChild(self, childName):
        return self.children[childName]

    # gets the widget of a child given a name
    def getWidget(self, widgetName):
        return self.widgets[widgetName]

    # switches window to a child window
    def switch(self, childName):
        app.hideSubWindow(self.name)
        self.children[childName].go(self)

    # run when a child window closes and this window is open
    def resume(self):
        app.showSubWindow(self.name)

    # run when the window is closed by the user
    def back(self):
        app.hideSubWindow(self.name)

        # stops the program if the window has no parent, otherwise the parent resumes
        if self.parent == None:
            app.stop()
            quit()
        else:
            self.parent.resume()

# a window used to choose a game folder
class ChooseGame(Window):

    # opens a window that displays and allows the user to choose a folder
    def selectFolder(self):
        directory = app.directoryBox(title="Select Folder")

        # checks to see whether the user selected a folder or just clicked cancel
        if directory != None:
            self.getChild("Select Players").setDirectory(directory)
            self.switch("Select Players")

# a window used to select the players
class SelectPlayers(Window):

    # overrides the default Window.__init__() function
    def __init__(self, name):
        super().__init__(name)
        self.directory = ""
        self.db = None
        self.players = ["", ""]

    # creates a new database object when the window is opened, and resets the players
    def go(self, parent=None):
        self.db = Database(self.directory)
        self.resetPlayer(0)
        self.resetPlayer(1)
        super().go(parent)

    # checks whether players are logged in, and displays there names and cards if they are
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

    # closes the database when the window is closed
    def back(self):
        self.db.close()
        super().back()

    # resets the information of a player given the player number
    def resetPlayer(self, num):
        num = str(num)
        self.getWidget("Player"+num).setLabel("SELECT PLAYER")
        self.getWidget("Username"+num).setLabel("")
        self.getWidget("Total"+num).setLabel("")

    # sets the information of a player given the player number
    def setPlayer(self, num, cards):
        string = str(num)
        self.getWidget("Username"+string).setLabel(self.players[num])
        self.getWidget("Total"+string).setLabel(str(cards))

    # sets the game directory
    def setDirectory(self, directory):
        self.directory = directory

    # sets the username of a player given the player number
    def setUsername(self, slot, username):
        self.players[slot] = username

    # open the login window
    def login(self, btn=None):
        self.getChild("Login").setSlot(int(btn[-1]))
        self.switch("Login")

    # starts the game if both players are logged in
    def play(self, btn=None):
        if self.players[0] == "" or self.players[1] == "":
            errorBox(
                "Error",
                "Both players must be logged in!",
                self.name
            )
        else:
            self.switch("Game")

    # opens the leaderboard window
    def leaderboard(self, btn=None):
        self.switch("Leaderboard")

    # opens the create account window
    def create(self, btn=None):
        self.switch("Create Account")

    # opens change password window
    def change(self, btn=None):
        self.switch("Change Password")

    # opens window to delete an account
    def delete(self, btn=None):
        self.switch("Delete Account")

# class that handles user login, inherits from the window class
class Login(Window):

    # initialises login window
    def __init__(self, name):
        super().__init__(name)
        self.slot = 0

    # function that the select players window uses, determines which player (0 or 1) is being logged in
    def setSlot(self, num):
        self.slot = num

    # resets login slot
    def go(self, parent):
        super().go(parent)
        self.parent.players[self.slot] = ""

    # checks whether user has entered the correct username and password
    def authenticate(self, btn=None):

        # gets the username from the entry box
        username = self.getWidget("UsernameEntry").getEntry()

        # gets the passcode from the entry box and hashes it immediately
        enteredPassword = sha256(self.getWidget("PasswordEntry").clearEntry().encode()).digest()

        # prevents users from playing against themselves
        if username == self.parent.players[(self.slot+1)%2]:
            errorBox(
                "Error",
                "You can't play against yourself!",
                self.name
            )
            return

        # checks if the user actually exists
        if self.parent.db.userExists(username):

            # gets the authentication info of the user
            actualPassword, salt = self.parent.db.getAuthInfo(username)

            # hashes the already hashed password again, this time with salt
            enteredPassword = sha256(salt + enteredPassword).digest()

            # ensures the retrieved password and the entered password are the same
            if enteredPassword == actualPassword:
                app.clearAllEntries()
                self.parent.setUsername(self.slot, username)
                self.back()
                return
        
        # error box informs user of incorrect login details
        errorBox(
            "Error",
            "Incorrect username or password!",
            self.name
        )

# a class that handles account creation, inherits from the window class
class CreateAccount(Window):

    # a function to create the account, if all checks are passed
    def create(self, btn=None):

        # gets the usernames and passwords from the entry boxes
        username = self.getWidget("UsernameEntry").getEntry()
        password = self.getWidget("PasswordEntry").clearEntry()

        # performs a length check
        if len(username) < 3 or len(username) > 20:
            errorBox(
                "Error",
                "Usernames must be between 3 and 20 characters long!",
                self.name
            )
            return

        # prevents disallowed characters
        if not username.isalnum():
            errorBox(
                "Error",
                "Usernames must contain alphanumeric characters only!",
                self.name
            )
            return

        # checks username doesn't already exist
        if self.parent.db.userExists(username):
            errorBox(
                "Error",
                "Username is already taken!",
                self.name
            )
            return

        # password length check
        if len(password) < 8:
            errorBox(
                "Error",
                "Passwords must be 8 characters or longer!",
                self.name
            )
            return

        # generates a random 32 byte salt, prevents the use of a rainbow table
        salt = os.urandom(32)

        # hashes password twice, with salt the second time
        password = sha256(password.encode()).digest()
        password = sha256(salt+password).digest()

        # create user
        self.parent.db.createUser(username, password, salt)

        # return to the select players window
        self.back()

        # inform the user of the successful account creation
        app.infoBox(
            "Account Created",
            "Your account has been created!",
            self.parent.name
        )

# a class that handles password changing, inherits from the Window class
class ChangePassword(Window):

    # function fo change the password, if all tests are passed
    def change(self, btn=None):

        # gets all entry fields
        username = self.getWidget("UsernameEntry").getEntry()
        oldPassword = sha256(self.getWidget("OldPasswordEntry").clearEntry().encode()).digest()
        newPassword = self.getWidget("NewPasswordEntry").clearEntry()

        # checks if the user actually exists
        if self.parent.db.userExists(username):

            # gets authentication info of the user
            password, salt = self.parent.db.getAuthInfo(username)

            # hashes the old password using the salt
            oldPassword = sha256(salt+oldPassword).digest()


            # checks if the passwords match
            if oldPassword == password:

                # length check on the password
                if len(newPassword) < 8:
                    errorBox(
                        "Error",
                        "Passwords must be 8 characters or longer!",
                        self.name
                    )
                    return

                # creates, hashes and salts new password
                newPassword = sha256(newPassword.encode()).digest()
                newPassword = sha256(salt+newPassword).digest()

                # updates password in the database
                self.parent.db.changePassword(username, newPassword)

                # returns to the Select Players window
                self.back()

                # informs the user that their password has been changed
                infoBox(
                    "Password Changed",
                    "Your password has been changed successfully!",
                    self.parent.name
                )
                return

        # tells the user they have entered incorrect login details
        errorBox(
            "Error",
            "Incorrect username or password!",
            self.name
        )

# a class that handles account deletion, inherits from the window class
class DeleteAccount(Window):

    # function to delete a user from the database, if tests are passed
    def delete(self, btn=None):

        # gets entry fields
        username = self.getWidget("UsernameEntry").getEntry()
        enteredPassword = sha256(self.getWidget("PasswordEntry").clearEntry().encode()).digest()

        # ensures the user exists
        if self.parent.db.userExists(username):

            # get the information required to authenticate the user
            actualPassword, salt = self.parent.db.getAuthInfo(username)
            enteredPassword = sha256(salt + enteredPassword).digest()

            # checks that the user entered the correct password
            if enteredPassword == actualPassword:

                # clears all entry fields
                app.clearAllEntries()

                # tells the database to delete the user
                self.parent.db.deleteUser(username)

                # logs out the player if they were already logged in
                if self.parent.players[0] == username:
                    self.parent.players[0] = ""
                if self.parent.players[1] == username:
                    self.parent.players[1] = ""

                # returns to the select players window
                self.back()
                infoBox(
                    "Account Deleted",
                    "Your account has been deleted successfully!",
                    self.parent.name
                )
                return

        # informs the user they have entered the wrong password
        errorBox(
            "Error",
            "Incorrect username or password!",
            self.name
        )

# simple class to show leaderboard, inherits from the Window class
class Leaderboard(Window):

    # overrides default window function
    def go(self, parent):
        super().go(parent)
        data = self.parent.db.getTopFive()
        self.getWidget("Table").fill(data)

# handles the game "loop", determines the winner, inherits from Window class
class Game(Window):

    # sets up the starting state of the game
    def __init__(self, name):
        super().__init__(name)
        self.cards = []
        self.drawn = [None, None]
        self.hands = [[], []]
        self.turn = 0
        self.blankCard = Card("", "grey", "grey")

    # run when game is started
    def go(self, parent):

        # initialise values
        super().go(parent)
        self.cards = []
        self.drawn = [None, None]
        self.hands = [[],[]]

        # create the cards in the deck
        for pair in [("red", "black"),("yellow", "red"),("black", "yellow")]:
            for i in range(1, 11):
                self.cards.append(Card(i, pair[0], pair[1]))

        # shuffle the deck
        random.shuffle(self.cards)

        # reset the visual cards
        self.getWidget("Player0").setLabel(self.parent.players[0])
        self.getWidget("Player1").setLabel(self.parent.players[1])
        self.getWidget("DrawDeck").setLabel(self.parent.players[0]+" pick a card...")

        # show blank cards for both player's hands
        self.blankCard.show(self.getWidget("Card0"))
        self.blankCard.show(self.getWidget("Card1"))

        # player 0 starts
        self.turn = 0

    # reveals a card
    def revealCard(self, btn=None):

        # turn 2 means that both players have drawn their cards
        if self.turn == 2:

            # one line condition to determine the winner
            roundWinner = 0 if self.drawn[0] > self.drawn[1] else 1

            # adds the cards to the hands of the winner
            self.hands[roundWinner] += self.drawn

            # resets the hands of the winner
            self.drawn = [None, None]

            # checks if there are no cards left in the deck
            if len(self.cards) == 0:

                # determines the winner of the game
                gameWinner = 0 if len(self.hands[0]) > len(self.hands[1]) else 1
                gameLoser = (gameWinner+1)%2

                # increases the number of cards of the winner
                self.parent.db.addCards(
                    self.parent.players[gameWinner],
                    len(self.hands[gameWinner])
                )

                # returns to the select players window
                self.back()

                # shows the winning player, and displays the cards of the winner
                infoBox(
                    "Game Over",
                    self.parent.players[gameWinner]+" won the game, beating "
                    +self.parent.players[gameLoser]+" "
                    +str(len(self.hands[gameWinner]))+":"
                    +str(len(self.hands[gameLoser]))+" .\n"
                    +"Winner's cards:\n\t  > "
                    +",\n\t  > ".join(sorted([str(i) for i in self.hands[gameWinner]])),
                    self.parent.name
                )
                return
            else:

                # resets both player's current card, and instructs player 0 to pick a card
                self.getWidget("DrawDeck").setLabel(self.parent.players[0]+" pick a card...")
                self.blankCard.show(self.getWidget("Card0"))
                self.blankCard.show(self.getWidget("Card1"))

            # informs the players of the round winner
            self.turn = 0
            infoBox(
                "Round Winner",
                self.parent.players[roundWinner]+" wins this round!",
                self.name
            )
        else:

            # set the instruction button to the relevant command
            if self.turn == 1:
                self.getWidget("DrawDeck").setLabel("Continue...")
            else:
                self.getWidget("DrawDeck").setLabel(self.parent.players[1]+" pick a card...")

            # pops a card off the top of the deck
            self.drawn[self.turn] = self.cards.pop()

            # shows the card that was popped of the deck
            self.drawn[self.turn].show(self.getWidget("Card"+str(self.turn)))

            # next player's turn
            self.turn = self.turn + 1

    # empty function that appJar requires for a button
    def doNothing():
        pass

# a class that represents an instance of a card object   
class Card:

    # sets up starting values
    def __init__(self, number, bg, fg):
        self.number = number
        self.fg = fg
        self.bg = bg

    # sets a widget to have the same foreground, background, and text properties as the card
    def show(self, widget):
        text = str(self.number)
        if len(text) == 1:
            text = " "+text
        widget.setLabel(text)
        widget.changeForeground(self.fg)
        widget.changeBackground(self.bg)

    # override inbuilt "greater than" function, for comparing two cards
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
        return self.bg + " " + str(self.number)
        
# initialises all windows, gives them a name
chooseGame = ChooseGame("Choose Game")
selectPlayers = SelectPlayers("Select Players")
login = Login("Login")
createAccount = CreateAccount("Create Account")
changePassword = ChangePassword("Change Password")
deleteAccount = DeleteAccount("Delete Account")
leaderboard = Leaderboard("Leaderboard")
game = Game("Game")


# adds all the widgets to each of the windows

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

# if the module is being run directly (not just imported), start the game
if __name__ == "__main__":
    chooseGame.go()
