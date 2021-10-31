__author__ = "Vipul Kumar"
__version__ = "1.0"

import os.path
from datetime import timedelta
from time import time
from tkinter import Tk, Button

from Background import Background
from Bird import Bird
from Settings import Settings
from Tubes import Tubes


class App(Tk, Settings):

    # Private variables and internal adjustments
    __background_animation_speed = 720
    __bestScore = 0
    __bird_descend_speed = 38.4
    __buttons = []
    __playing = False
    __score = 0
    __time = "%H:%M:%S"

    def __init__(self):

        Tk.__init__(self)
        self.setOptions()

        # If the size of the width and height of the window are set, they will be used in the game. 
        # # If they have the value None, the window size will be the size of the user's monitor.

        if all([self.window_width, self.window_height]):
            self.__width = self.window_width
            self.__height = self.window_height
        else:
            self.__width = self.winfo_screenwidth()
            self.__height = self.winfo_screenheight()

        # Sets up the program window
        self.title(self.window_name)
        self.geometry("{}x{}".format(self.__width, self.__height))
        self.resizable(*self.window_rz)
        self.attributes("-fullscreen", self.window_fullscreen)
        self["bg"] = "black"

        # Check for in-game images
        for file in self.images_fp:
            if not os.path.exists(file):
                raise FileNotFoundError("The following file was not found:\n{}".format(file))

        # Press the image of the button to start the game
        self.__startButton_image = Background.getPhotoImage(
            image_path=self.startButton_fp,
            width=(self.__width // 100) * self.button_width,
            height=(self.__height // 100) * self.button_height,
            closeAfter=True
        )[0]

        # Press the image of the button to exit the game
        self.__exitButton_image = Background.getPhotoImage(
            image_path=self.exitButton_fp,
            width=(self.__width // 100) * self.button_width,
            height=(self.__height // 100) * self.button_height,
            closeAfter=True
        )[0]

        # Uploads the game title image
        self.__title_image = Background.getPhotoImage(
            image_path=self.title_fp,
            width=(self.__width // 100) * self.title_width,
            height=(self.__height // 100) * self.title_height,
            closeAfter=True
        )[0]

        # Uploads the game scoreboard image
        self.__scoreboard_image = Background.getPhotoImage(
            image_path=self.scoreboard_fp,
            width=(self.__width // 100) * self.scoreboard_width,
            height=(self.__height // 100) * self.scoreboard_height,
            closeAfter=True
        )[0]

        # Sets the speed of the background animation based on the width of the window
        self.__background_animation_speed //= self.__width / 100
        self.__background_animation_speed = int(self.__background_animation_speed)

        # Sets the speed of descent of the bird based on the height of the window
        self.__bird_descend_speed //= self.__height / 100
        self.__bird_descend_speed = int(self.__bird_descend_speed)

    def changeFullscreenOption(self, event=None):
        """
        Method to put the game in "fullscreen" or "window" mode
        """

        self.window_fullscreen = not self.window_fullscreen
        self.attributes("-fullscreen", self.window_fullscreen)

    def close(self, event=None):
        """
        Method to close the game
        """

        # Saves the player's best score before leaving the game
        self.saveScore()

        # Tries to stop the processes
        try:
            self.__background.stop()
            self.__bird.kill()
            self.__tubes.stop()
        finally:
            quit()

    def createMenuButtons(self):
        """
        Method for creating menu buttons
        """

        # Sets button size in percentage based on window size
        width = (self.__width // 100) * self.button_width
        height = (self.__height // 100) * self.button_height

        # Create a button to start the game
        startButton = Button(
            self, image=self.__startButton_image, bd=0, command=self.start, cursor=self.button_cursor,
            bg=self.button_bg, activebackground=self.button_activebackground
        )
        # Places the button inside the background (Canvas)
        self.__buttons.append(
            self.__background.create_window((self.__width // 2) - width // 1.5,
                                            int(self.__height / 100 * self.button_position_y),
                                            window=startButton))

        # Create a button to exit the game
        exitButton = Button(
            self, image=self.__exitButton_image, bd=0, command=self.close, cursor=self.button_cursor,
            bg=self.button_bg, activebackground=self.button_activebackground
        )

        # Places the button inside the background (Canvas)
        self.__buttons.append(
            self.__background.create_window((self.__width // 2) + width // 1.5,
                                            int(self.__height / 100 * self.button_position_y),
                                            window=exitButton))

    def createScoreBoard(self):
        """
        Method to create the image of the game scoreboard 
        in the background along with the player's information.
        """

        # Sets position X and Y
        x = self.__width // 2
        y = (self.__height // 100) * self.scoreboard_position_y

        # Calculates the size of the scoreboard image
        scoreboard_w = (self.__width // 100) * self.scoreboard_width
        scoreboard_h = (self.__width // 100) * self.scoreboard_height

        # Calculates the X and Y position of the punctuation text of the last game
        score_x = x - scoreboard_w / 100 * 60 / 2
        score_y = y + scoreboard_h / 100 * 10 / 2

        # Calculates the X and Y position of the player's best score text
        bestScore_x = x + scoreboard_w / 100 * 35 / 2
        bestScore_y = y + scoreboard_h / 100 * 10 / 2

        # Calculates the X and Y position of the game time text
        time_x = x
        time_y = y + scoreboard_h / 100 * 35 / 2

        # Defines the source of the texts
        font = (self.text_font, int(0.02196 * self.__width + 0.5))

        # Creates the scoreboard image in the background
        self.__background.create_image(x, y, image=self.__scoreboard_image)

        # Creates text to show the score of the last game
        self.__background.create_text(
            score_x, score_y, text="Score: %s" % self.__score,
            fill=self.text_fill, font=font
        )

        # Creates text to show the player's best score
        self.__background.create_text(
            bestScore_x, bestScore_y, text="Best Score: %s" % self.__bestScore,
            fill=self.text_fill, font=font
        )

        # Creates text to show game time
        self.__background.create_text(
            time_x, time_y, text="Time: %s" % self.__time,
            fill=self.text_fill, font=font
        )

    def createTitleImage(self):
        """
        Method to create the image of the game title in the background
        """

        self.__background.create_image(self.__width // 2, (self.__height // 100) * self.title_position_y,
                                       image=self.__title_image)

    def deleteMenuButtons(self):
        """
        Method for delete menu buttons 
        """

        # Delete so-like button created inside the background
        for item in self.__buttons:
            self.__background.delete(item)

        # Clears the list of buttons
        self.__buttons.clear()

    def gameOver(self):
        """
        Endgame method
        """

        # Calculates the time played in seconds and then formats it
        self.__time = int(time() - self.__time)
        self.__time = str(timedelta(seconds=self.__time))

        # Stops background animation and tube animation
        self.__background.stop()
        self.__tubes.stop()

        # Declares that the game is no longer running
        self.__playing = False

        # Creates the started buttons
        self.createMenuButtons()

        # Creates image of the game title
        self.createTitleImage()

        # Creates picture of the scoreboard and shows the information of the past game
        self.createScoreBoard()

    def increaseScore(self):
        """
        Method to increase the score of the player's current game
        """

        self.__score += 1
        if self.__score > self.__bestScore:
            self.__bestScore = self.__score

    def init(self):
        """
        Method to start the program itself, creating all the initial graphical part of the game
        """

        # self.createMenuButtons()
        self.loadScore()

        # Creates the game background
        self.__background = Background(
            self, self.__width, self.__height, fp=self.background_fp, animation_speed=self.__background_animation_speed
        )

        # Focuses on the background so you can define the events
        self.__background.focus_force()
        # Sets event to change window mode to "fullscreen" or "window"
        self.__background.bind(self.window_fullscreen_event, self.changeFullscreenOption)
        # Sets event to start the game
        self.__background.bind(self.window_start_event, self.start)
        # Sets event to exit the game
        self.__background.bind(self.window_exit_event, self.close)

        # Defines a method if the user closes the game window
        self.protocol("WM_DELETE_WINDOW", self.close)

        # Packages the background object
        self.__background.pack()

        # Create so-how buttons from the game menu
        self.createMenuButtons()

        # Creates image of the game title
        self.createTitleImage()

        # Create sit-in the game
        self.__bird = Bird(
            self.__background, self.gameOver, self.__width, self.__height,
            fp=self.bird_fp, event=self.bird_event, descend_speed=self.__bird_descend_speed
        )

    def loadScore(self):
        """
        Method to load player score
        """

        # Tries to load the user's score
        try:
            file = open(self.score_fp)
            self.__bestScore = int(file.read(), 2)
            file.close()

        # If this is not possible, a file will be created to save the
        except:
            file = open(self.score_fp, 'w')
            file.write(bin(self.__bestScore))
            file.close()

    def saveScore(self):
        """
        Method to save player score
        """

        with open(self.score_fp, 'w') as file:
            file.write(bin(self.__bestScore))

    def start(self, event=None):
        """
        Method to initialize the game
        """

        # This method runs only if the player is not already playing
        if self.__playing: return

        # Restarts the leaderboard
        self.__score = 0
        self.__time = time()

        # Removes menu buttons
        self.deleteMenuButtons()

        # Restarts the background
        self.__background.reset()

        # Initializes background animation if True
        if self.background_animation:
            self.__background.run()

        # Create a bird in the game
        self.__bird = Bird(
            self.__background, self.gameOver, self.__width, self.__height,
            fp=self.bird_fp, event=self.bird_event, descend_speed=self.__bird_descend_speed
        )

        # Create tubes in the game
        self.__tubes = Tubes(
            self.__background, self.__bird, self.increaseScore, self.__width, self.__height,
            fp=self.tube_fp, animation_speed=self.__background_animation_speed
        )

        # Initializes bird and tubes animation
        self.__bird.start()
        self.__tubes.start()


if __name__ == "__main__":
    try:
        app = App()
        app.init()
        app.mainloop()

    except FileNotFoundError as error:
        print(error)
