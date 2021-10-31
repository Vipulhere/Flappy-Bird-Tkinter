from tkinter import Tk, Canvas

from PIL.Image import open as openImage
from PIL.ImageTk import PhotoImage


class Background(Canvas):
    """
    Class to generate an animated background
    """

    __background = []
    __stop = False

    def __init__(self, tk_instance, *geometry, fp="background.png", animation_speed=50):

        # Checks whether the parameter tk_instance is an instance of Tk
        if not isinstance(tk_instance, Tk): raise TypeError("The tk_instance argument must be an instance of Tk.")

        # Receives the image path and animation speed
        self.image_path = fp
        self.animation_speed = animation_speed

        # Receives the width and height of the widget
        self.__width = geometry[0]
        self.__height = geometry[1]

        # Initializes the Canvas class constructor
        Canvas.__init__(self, master=tk_instance, width=self.__width, height=self.__height)

        # Loads the image that will be used in the background
        self.__bg_image = \
        self.getPhotoImage(image_path=self.image_path, width=self.__width, height=self.__height, closeAfter=True)[0]

        # Creates an image that will be fixed, that is, that will not be part of the animation and serves in bug situations in the animation
        self.__background_default = self.create_image(self.__width // 2, self.__height // 2, image=self.__bg_image)

        # Creates the images that will be used in the background animation
        self.__background.append(self.create_image(self.__width // 2, self.__height // 2, image=self.__bg_image))
        self.__background.append(
            self.create_image(self.__width + (self.__width // 2), self.__height // 2, image=self.__bg_image))

    def getBackgroundID(self):
        """
        Returns the id's of the background images
        """
        return [self.__background_default, *self.__background]

    @staticmethod
    def getPhotoImage(image=None, image_path=None, width=None, height=None, closeAfter=False):
        """ Returns an object of the PIL class. ImageTk. 
        PhotoImage of an image and images created from PIL. Image (photoImage, new, original) 
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

    def reset(self):
        """
        Method to reset the background by deleting all items other than the background
        """

        # Deletes all canvas items
        self.delete("all")

        # For the animation passing False to the "stop" attribute
        self.__stop = False

        # Clears the list of images used in the animation
        self.__background.clear()

        # Creates an image that will be fixed, that is, that will not be part of the animation and serves in bug situations in the animation
        self.__background_default = self.create_image(self.__width // 2, self.__height // 2, image=self.__bg_image)

        # Creates the images that will be used in the background animation
        self.__background.append(self.create_image(self.__width // 2, self.__height // 2, image=self.__bg_image))
        self.__background.append(
            self.create_image(self.__width + (self.__width // 2), self.__height // 2, image=self.__bg_image))

    def run(self):
        """
        Method to start background animation
        """

        # As long as the "stop" attribute is False, the animation will continue in an infinite loop
        if not self.__stop:

            # Moves background images in position X
            self.move(self.__background[0], -10, 0)
            self.move(self.__background[1], -10, 0)
            self.tag_lower(self.__background[0])
            self.tag_lower(self.__background[1])
            self.tag_lower(self.__background_default)

            # If the first image in the list has left the widget area, a new one will be created after the second image
            if self.bbox(self.__background[0])[2] <= 0:
                # Delete the first image from the list (image that left the widget area)
                self.delete(self.__background[0])
                self.__background.remove(self.__background[0])

                # Creates a new image from the last image of the animation
                width = self.bbox(self.__background[0])[2] + self.__width // 2
                self.__background.append(self.create_image(width, self.__height // 2, image=self.__bg_image))

            # Reruns the method after a certain time
            self.after(self.animation_speed, self.run)

    def stop(self):
        """
        Method to stop background animation
        """
        self.__stop = True
