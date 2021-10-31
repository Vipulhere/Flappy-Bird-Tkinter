import os
from json import dumps
from json import loads


class Settings(object):
    """ Class with all game settings """

    # Window settings
    window_name = "Flappy Bird"
    window_rz = (False, False)
    window_fullscreen = True
    window_width = None
    window_height = None

    # Button settings
    button_width = 22
    button_height = 17
    button_bg = "black"
    button_fg = "white"
    button_activebackground = "black"
    button_font = ("Impact", 40)
    button_position_y = 85
    button_cursor = "hand2"

    # Player score image settings
    scoreboard_width = 40
    scoreboard_height = 40
    scoreboard_position_y = 50

    # Scoreboard text settings
    text_font = "Autumn"
    text_fill = "White"

    # Game title settings
    title_width = 35
    title_height = 15
    title_position_y = 15

    # Events
    bird_event = "<Up>"
    window_fullscreen_event = "<F11>"
    window_start_event = "<Return>"
    window_exit_event = "<Escape>"

    # File paths
    background_fp = "Images/background.png"
    bird_fp = "Images/bird.png"
    startButton_fp = "Images/start_button.png"
    exitButton_fp = "Images/exit_button.png"
    tube_fp = ["Images/tube.png", "Images/tube_mouth.png"]
    title_fp = "Images/title.png"
    scoreboard_fp = "Images/scoreboard.png"
    score_fp = "Data/scr.txt"
    settings_fp = "Data/settings.json"

    # Animation settings
    background_animation = True

    # Joins all directories into one list
    images_fp = [background_fp, bird_fp, startButton_fp, exitButton_fp, tube_fp[0], tube_fp[1], title_fp]

    def setOptions(self):
        """ Method to receive some game settings from a.json file. 
        If the file does not exist, one with the default settings will be created. """

        # Some attributes that can be changed
        attributes = "window_fullscreen,window_width,window_height".split(',')

        # Tries to open the file stop reading
        try:
            file = open(self.settings_fp, 'r')
            data = loads(file.read())
            file.close()

           # Sets attributes with the values obtained from the file as long as they are 
           # referring to events or are on the list of allowed attributes.

            for attr in data:
                if "event" in attr or attr in attributes:
                    setattr(Settings, attr, data[attr])

        # If there is no file to get the settings, it will be created
        except:

            # If the directory does not exist, it will be created.
            if not os.path.exists(os.path.split(self.settings_fp)[0]):
                os.mkdir(os.path.split(self.settings_fp)[0])

            file = open(self.settings_fp, 'w')

            data = dict()

            # Stores attributes in the file with their default values as long as they are 
            # referring to events or are on the list of allowed attributes.
            for attr in Settings.__dict__:
                if "event" in attr or attr in attributes:
                    data[attr] = Settings.__dict__[attr]

            # Put the information in the file and close it
            file.write(dumps(data, indent=2))
            file.close()
