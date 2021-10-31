from threading import Thread

from Background import Background
from PIL.Image import open as openImage
from PIL.ImageTk import PhotoImage


class Bird(Thread):
    """ Class to create a bird """

    __tag = "Bird"
    __isAlive = None
    __going_up = False
    __going_down = 0
    __times_skipped = 0
    __running = False

    decends = 0.00390625
    climbsUp = 0.0911458333

    def __init__(self, background, gameover_function, *screen_geometry, fp="bird.png", event="<Up>", descend_speed=5):

        # Checks whether "background" is a Background instance and if the "gamerover_method" is chamável
        if not isinstance(background, Background): raise TypeError(
            "The background argument must be an instance of Background.")
        if not callable(gameover_function): raise TypeError("The gameover_method argument must be a callable object.")

        # Instance the parameters
        self.__canvas = background
        self.image_path = fp
        self.__descend_speed = descend_speed
        self.gameover_method = gameover_function

        # Receives the width and height of the background
        self.__width = screen_geometry[0]
        self.__height = screen_geometry[1]

        # Sets the decide and climb of the bird based on the height of the background
        self.decends *= self.__height
        self.decends = int(self.decends + 0.5)
        self.climbsUp *= self.__height
        self.climbsUp = int(self.climbsUp + 0.5)

        # Invokes the Thread Builder Method
        Thread.__init__(self)

        # Calculates bird size based on window width and height
        self.width = (self.__width // 100) * 6
        self.height = (self.__height // 100) * 11

        # Loads and creates bird image in background
        self.__canvas.bird_image = \
        self.getPhotoImage(image_path=self.image_path, width=self.width, height=self.height, closeAfter=True)[0]
        self.__birdID = self.__canvas.create_image(self.__width // 2, self.__height // 2,
                                                   image=self.__canvas.bird_image, tag=self.__tag)

        # Sets event to make the bird rise
        self.__canvas.focus_force()
        self.__canvas.bind(event, self.jumps)
        self.__isAlive = True

    def birdIsAlive(self):
        """ Method to check if the bird is alive """

        return self.__isAlive

    def checkCollision(self):
        """ Method to check if the bird has crossed the edge of the window or collided with something """

        # Receives bird position in the background
        position = list(self.__canvas.bbox(self.__tag))

        # If the bird has crossed the bottom edge of the background, it will be declared dead
        if position[3] >= self.__height + 20:
            self.__isAlive = False

        # If the bird has crossed the top edge of the background, it will be declared dead    
        if position[1] <= -20:
            self.__isAlive = False

        # Gives x pixels bird a margin of error 
        position[0] += int(25 / 78 * self.width)
        position[1] += int(25 / 77 * self.height)
        position[2] -= int(20 / 78 * self.width)
        position[3] -= int(10 / 77 * self.width)

        # Sets objects to ignore in collisions
        ignored_collisions = self.__canvas.getBackgroundID()
        ignored_collisions.append(self.__birdID)

        # Checks for possible collisions with the bird
        possible_collisions = list(self.__canvas.find_overlapping(*position))

        # Removes ignored objects from possible collisions
        for _id in ignored_collisions:
            try:
                possible_collisions.remove(_id)
            except:
                continue

        # If there is a collision the bird dies
        if len(possible_collisions) >= 1:
            self.__isAlive = False

        return not self.__isAlive

    def getTag(self):
        """ Method to return bird tag """

        return self.__tag

    @staticmethod
    def getPhotoImage(image=None, image_path=None, width=None, height=None, closeAfter=False):
        """
        Retorna um objeto da classe PIL.ImageTk.PhotoImage de uma imagem e as imagens criadas de PIL.Image 
        (photoImage, new, original)

        @param image: Instância de PIL.Image.open
        @param image_path: Diretório da imagem
        @param width: Largura da imagem
        @param height: Altura da imagem
        @param closeAfter: Se True, a imagem será fechada após ser criado um PhotoImage da mesma
        """

        if not image:
            if not image_path: return

            # Opens the image using her path
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

    def jumps(self, event=None):
        """ Method to make the bird jump """

        # Checks if the bird has left the background area
        self.checkCollision()

        # If the bird is dead, this method cannot be executed
        if not self.__isAlive or not self.__running:
            self.__going_up = False
            return

        # Declares that the bird is rising
        self.__going_up = True
        self.__going_down = 0

        # Move the bird while the ascent limit per animation has not exceeded
        if self.__times_skipped < self.climbsUp:

            # Move the bird up
            self.__canvas.move(self.__tag, 0, -1)
            self.__times_skipped += 1

            # Runs the method again
            self.__canvas.after(3, self.jumps)

        else:

            # Declares that the bird is no longer rising
            self.__going_up = False
            self.__times_skipped = 0

    def kill(self):
        """ Method to kill the bird """

        self.__isAlive = False

    def run(self):
        """ Method to start the animation of the falling passaro """

        self.__running = True

        # Checks if the bird has left the background area
        self.checkCollision()

        # As long as the bird has not reached its maximum speed, the speed will increase by 0.05
        if self.__going_down < self.decends:
            self.__going_down += 0.05

        # Performs descent animation only if the bird is alive
        if self.__isAlive:

            # Performs descent animation only if the bird is not climbing
            if not self.__going_up:
                # Move the bird down
                self.__canvas.move(self.__tag, 0, self.__going_down)

            # Reruns the method
            self.__canvas.after(self.__descend_speed, self.run)

        # If the bird is dead, an endgame method will be executed
        else:
            self.__running = False
            self.gameover_method()
