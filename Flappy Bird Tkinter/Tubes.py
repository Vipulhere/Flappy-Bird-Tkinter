from random import randint
from threading import Thread

from Background import Background
from Bird import Bird
from PIL.Image import open as openImage
from PIL.ImageTk import PhotoImage


class Tubes(Thread):
    """ Class for creating pipes """

    __distance = 0
    __move = 10
    __pastTubes = []

    def __init__(self, background, bird, score_function=None, *screen_geometry, fp=("tube.png", "tube_mourth"),
                 animation_speed=50):

        # Checks past parameters and throws an error if something is incorrect
        if not isinstance(background, Background): raise TypeError(
            "The background argument must be an instance of Background.")
        if not len(fp) == 2: raise TypeError(
            "The parameter fp should be a sequence containing the path of the images of the tube body and the tube mouth.")
        if not isinstance(bird, Bird): raise TypeError("The birdargument must be an instance of Bird.")
        if not callable(score_function): raise TypeError("The score_function argument must be a callable object.")

        Thread.__init__(self)

        # Instance the parameters
        self.__background = background
        self.image_path = fp
        self.__animation_speed = animation_speed
        self.__score_method = score_function

        # Receives the width and height of the background
        self.__width = screen_geometry[0]
        self.__height = screen_geometry[1]

        # Gets bird size
        self.__bird_w = bird.width
        self.__bird_h = bird.height

        # Calculates the width and height of the image
        self.__imageWidth = (self.__width // 100) * 10
        self.__imageHeight = (self.__height // 100) * 5

        # Creates a list to save images of the tubes
        try:
            self.deleteAll()
        except:
            self.__background.tubeImages = []

        # Creates a list only to save future images of the bodies of the generated tubes
        self.__background.tubeImages.append([])

        # Loads the image of the tube mouth
        self.__background.tubeImages.append(
            self.getPhotoImage(
                image_path=self.image_path[1],
                width=self.__imageWidth,
                height=self.__imageHeight,
                closeAfter=True)[0]
        )

        # Carries tube body image
        self.__background.tubeImages.append(
            self.getPhotoImage(
                image_path=self.image_path[0],
                width=self.__imageWidth,
                height=self.__imageHeight)[1]
        )

        # Calculates the initial minimum distance between the tubes
        self.__minDistance = int(self.__imageWidth * 4.5)

        self.__stop = False
        self.__tubes = []

    def createNewTubes(self):
        """ Method to create 2 new tubes (bottom and top) in the same Position X """

        # Creates a list to store the body parts of the top tube
        tube1 = []

        #Sets the X position that the top tube will initially appear in the background
        width = self.__width + (self.__imageWidth)

        # Sets a Y position for the tube randomly respecting some rules that are: 
        # Space for the bird to pass and space to add the bottom tube.

        height = randint(self.__imageHeight // 2, self.__height - (self.__bird_h * 2) - self.__imageHeight)

        # Creates and adds to the top tube body list, the tube mouth
        tube1.append(self.__background.create_image(width, height, image=self.__background.tubeImages[1]))

        # Creates a new image in the image list with the height being equal to the Y position of the top tube
        self.__background.tubeImages[0].append(
            [self.getPhotoImage(image=self.__background.tubeImages[2], width=self.__imageWidth, height=height)[0], ]
        )

        # Sets the Y position of the top tube body
        y = (height // 2) + 1 - (self.__imageHeight // 2)

        # Creates and adds to the top tube body list, the tube body
        tube1.append(self.__background.create_image(width, y, image=self.__background.tubeImages[0][-1][0]))

        ###############################################################################################################
        ###############################################################################################################

        # Creates a list to store the body parts of the bottom tube
        tube2 = []

        #The Y position of the bottom tube is calculated based on the position of the top tube, plus the size of the bird
        height = height + (self.__bird_h * 2) + self.__imageHeight - 1

        # Creates and adds to the bottom tube body list, the tube mouth
        tube2.append(self.__background.create_image(width, height, image=self.__background.tubeImages[1]))

        # Sets the height of the body image of the bottom tube
        height = self.__height - height

        # Creates a new image in the image list with the height being equal to the Y position of the bottom tube
        self.__background.tubeImages[0][-1].append(
            self.getPhotoImage(image=self.__background.tubeImages[2], width=self.__imageWidth, height=height)[0]
        )

        # Sets the Y position of the bottom tube body
        y = (self.__height - (height // 2)) + self.__imageHeight // 2

        # Creates and adds to the bottom tube body list, the tube body
        tube2.append(self.__background.create_image(width, y, image=self.__background.tubeImages[0][-1][1]))

        # Adds the top and bottom tubes of position X to the list of tubes
        self.__tubes.append([tube1, tube2])

        # Sets the distance to ZERO
        self.__distance = 0

    def deleteAll(self):
        """ Method for descing all generated tubes """

        # Delete the tubes generated in the background
        for tubes in self.__tubes:
            for tube in tubes:
                for body in tube:
                    self.__background.delete(body)

        self.__background.clear()
        self.__background.tubeImages.clear()

    @staticmethod
    def getPhotoImage(image=None, image_path=None, width=None, height=None, closeAfter=False):
        """ Returns an object of the PIL class. ImageTk.PhotoImage of an image and images created from PIL. Image (photoImage, new, original) 
        @param image: Pil instance. Image.open 
        @param image_path: Image Directory 
        @param width: Image width 
        @param height: Image height 
        @param closeAfter: If True, the image will be closed after a PhotoImage is created of the same """

        if not image:
            if not image_path: return

            # Opens the image using its path
            image = openImage(image_path)

        # The image is redded only if there is a width or height
        if not width: width = image.width
        if not height: height = image.height

        # Creates a new image already resized
        newImage = image.resize([width, height])

        # Create a photoImage
        photoImage = PhotoImage(newImage)

        # If closeAfter is True, it closes the images
        if closeAfter:
            # Closes the new image
            newImage.close()
            newImage = None

            # Closes the original image
            image.close()
            image = None

# Returns the PhotoImage of the image, the new image that was used, and the original image
        return photoImage, newImage, image

    def move(self):
        """ Method for moving all tubes """

        # Creates an auxilar variable to check if the scoring method has been executed
        scored = False

        # Moves the generated tubes in the background
        for tubes in self.__tubes:
            for tube in tubes:

                # Check to see if the bird's past the tube. If yes, the method for scoring will run
                if not scored:

                    # Receives the position of the barrel
                    x2 = self.__background.bbox(tube[0])[2]

                    # If the "x2" position of the tube is smaller than the "x1" position of the bird and if it has not yet been 
                    # Punctuated this same barrel, the method to score will be called.

                    if (self.__width / 2) - (self.__bird_w / 2) - self.__move < x2:
                        if x2 <= (self.__width / 2) - (self.__bird_w / 2):

                            # Checks if the tube is in the list of past tubes
                            if not tube[0] in self.__pastTubes:
                                # Calls the method to score and adds the punctuated tube to the list of passed tubes
                                self.__score_method()
                                self.__pastTubes.append(tube[0])
                                scored = True

                # Moves each part of the tube cup in the background
                for body in tube:
                    self.__background.move(body, -self.__move, 0)

    def run(self):
        """ Method to generate the tubes in the background and make your animation in an infinite loop """

        # If the "stop" method has been called, the animation is terminated
        if self.__stop: return

        # If the tubes (up and down) of an X position have disappeared from the background area, 
        # they will be deleted along with your images and all your data.

        if len(self.__tubes) >= 1 and self.__background.bbox(self.__tubes[0][0][0])[2] <= 0:

            # Erases the entire tube body inside the background
            for tube in self.__tubes[0]:
                for body in tube:
                    self.__background.delete(body)

            # Removes the tubes (up and down) from the list of tubes
            self.__background.tubeImages[0].remove(self.__background.tubeImages[0][0])

            # Removes the tube body image from the image list
            self.__tubes.remove(self.__tubes[0])

            # Removes the first object from the list of passed tubes
            self.__pastTubes.remove(self.__pastTubes[0])

        # If the distance between the last tube created and the "x2" side of the background is greater than the distance 
        # Minimum set, then a new tube will be created.

        if self.__distance >= self.__minDistance:
            self.createNewTubes()
        else:
            # Increases distance as tubes move
            self.__distance += self.__move

        # Move the tubes
        self.move()

        # Reruns the method at a certain time
        self.__background.after(self.__animation_speed, self.run)

    def stop(self):
        """
        Método para interromper a Thread
        """

        self.__stop = True
