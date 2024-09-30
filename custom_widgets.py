# Built-in libraries
import timeit
from datetime import datetime
import math
import textwrap
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mbox
from typing import Union
from typing import Literal
from PIL import ImageTk, Image

# External libraries
import customtkinter as ctk

# Custom libraries
import backend
import crud_functionality as crud
import utilities as util

# Display settings
ctk.FontManager.load_font("Poppins-Regular.ttf")
ctk.FontManager.load_font("Inter-Regular.ttf")
ctk.set_appearance_mode("light")
colours = util.Colours()


class Frame(ctk.CTkFrame):
    """
    Format for CTkFrame widget

    Parameters
    ----------
    parent : any
        The parent widget in which the frame is contained

    fg_color : str
        The foreground colour of the frame

    border_width : int
        The width of the frame's border

    corner_radius : int
        The corner radius
    """
    def __init__(self,
                 parent: any,
                 fg_color: str = colours.get_bg_colour(),
                 border_width: int = 0,
                 corner_radius: int = 0,
                 **kwargs):
        # Set background as foreground unless not specified to
        if kwargs.get("bg_color"):
            bg_color = kwargs.get("bg_color")
            kwargs.pop("bg_color")
        else:
            bg_color = fg_color
        super().__init__(parent,
                         fg_color=fg_color,
                         bg_color=bg_color,
                         background_corner_colors=(bg_color, bg_color, bg_color, bg_color),
                         border_width=border_width,
                         border_color="Black",
                         corner_radius=corner_radius,
                         **kwargs)


class ScrollableFrame(ctk.CTkScrollableFrame):
    """
    Format for CTkScrollableFrame widget

    Parameters
    ----------
    parent : any
        The parent widget in which the frame is contained

    fg_color : str
        The foreground colour
    """
    def __init__(self,
                 parent: any,
                 fg_color: str = colours.get_bg_colour(),
                 **kwargs):
        # Set background as foreground unless not specified to
        if kwargs.get("bg_color"):
            bg_color = kwargs.get("bg_color")
            kwargs.pop("bg_color")
        else:
            bg_color = fg_color
        super().__init__(parent,
                         fg_color=fg_color,
                         border_width=0,
                         **kwargs)


class WelcomeAnimation(ctk.CTkCanvas):
    """
    Animation used when loading the application

    Parameters
    ----------
    parent : any
        The parent widget in which the frame is contained

    app : any
        The main window of the application
    """
    def __init__(self,
                 parent: any,
                 app: any):
        app.update()
        self.full_width = app.winfo_width()
        self.full_height = app.winfo_height()
        # Initalise borderless canvas
        super().__init__(parent,
                         width=self.full_width,
                         height=self.full_height,
                         bg=colours.get_primary_colour(),
                         highlightthickness=0)
        self.image_side = round(self.full_height / 3)
        offset = self.full_height * 0.1
        # Set images and their coordinates determined by their position
        images = {"logo_top_left.png": (-self.image_side-offset, (self.full_height/2)-self.image_side),
                  "logo_top_right.png": (self.full_width/2, -self.image_side-offset),
                  "logo_bottom_left.png": (self.full_width/2 - self.image_side, self.full_height+offset),
                  "logo_bottom_right.png": (self.full_width+offset, self.full_height/2)}
        # Labels for images based on standard x and y coordinates
        # "-xy": top left, "xy": top right, "-x-y": bottom left, "x-y": bottom right
        image_labels = ["-xy", "xy", "-x-y", "x-y"]
        self.image_ids = {}
        self.image_ref = []
        for count, (image, coord) in enumerate(images.items()):
            try:
                formatted_image = ImageTk.PhotoImage(Image.open(backend.get_directory("images") + image).resize((self.image_side, self.image_side)))
            except OSError:
                # Replace image with placeholder if it doesn't exist
                formatted_image = ImageTk.PhotoImage(Image.open(backend.get_directory("images") + "placeholder.png").resize((self.image_side, self.image_side)))
            image_id = self.create_image(coord,
                                         image=formatted_image,
                                         anchor="nw")
            # Store image reference to avoid garbage collection
            self.image_ref.append(formatted_image)
            self.image_ids[image_labels[count]] = image_id

        # Widgets
        self.button_frame = Frame(self,
                                  width=self.full_width,
                                  height=self.full_height,
                                  fg_color=colours.get_primary_colour())
        login_button = FilledButton(self.button_frame,
                                    text="Login",
                                    command=lambda: app.load_frame("LoginFrame"),
                                    width=125)
        login_button.pack()
        register_button = FilledButton(self.button_frame,
                                       text="Register",
                                       command=lambda: app.load_frame("RegisterFrame"),
                                       width=125)
        register_button.pack(pady=10)

        self.top_left_dist = self.full_width/2 + offset
        self.top_right_dist = self.full_height/2 + offset
        self.bottom_left_dist = -(self.full_height/2) - offset
        self.bottom_right_dist = -self.full_width/2 - offset
        self.buttons_id = self.create_window(0,
                                             self.full_height,
                                             width=self.full_width,
                                             height=self.full_height,
                                             window=self.button_frame,
                                             anchor="nw")

        self.is_active = False
        self.loop_id = None
        self.loop_count = 0
        self.jigsaw_connected = False

    def start(self):
        """
        Starts the animation
        """
        if not self.is_active:
            self.is_active = True
            self._animation_loop()

    def _connect_jigsaw(self):
        """
        Animation for the connection of the four images of the logo
        """
        increment = 0.01
        if self.loop_count < 100:
            self.move(self.image_ids["-xy"], self.top_left_dist*increment, 0)
            self.move(self.image_ids["xy"], 0, self.top_right_dist * increment)
            self.move(self.image_ids["-x-y"], 0, self.bottom_left_dist * increment)
            self.move(self.image_ids["x-y"], self.bottom_right_dist * increment, 0)
            self.loop_count += 1
        else:
            self.loop_count = 0
            self.jigsaw_connected = True

    def _load_buttons(self):
        """
        Animation for the buttons rising up onto the screen
        """
        img_dist_up = round(self.full_height / 8)
        button_dist_up = round(self.full_height / 3.5)
        increment = 0.01
        if self.loop_count < 100:
            # Move connected logo up
            for image_id in self.image_ids.values():
                self.move(image_id, 0, -img_dist_up * increment)
            # Move buttons up at a different speed
            self.move(self.buttons_id, 0, -button_dist_up * increment)
            self.loop_count += 1
        else:
            self.stop()

    def _animation_loop(self):
        """
        Keeps looping the animation until it is complete
        """
        if self.is_active:
            if not self.jigsaw_connected:
                self._connect_jigsaw()
            else:
                self._load_buttons()
            self.loop_id = self.after(10, self._animation_loop)

    def _get_image_coord(self, corner: str):
        """
        Get an image's current coordinate

        Parameters
        ----------
        corner : str
            The corner the image is situated in, defined in axis
        """
        if corner == "-xy" or corner == "x-y":
            return self.coords(self.image_ids[corner])[0]
        else:
            return self.coords(self.image_ids[corner])[1]

    def stop(self):
        """
        Stops the animation
        """
        if self.loop_id:
            self.after_cancel(self.loop_id)
        self.is_active = False


class Sidebar(Frame):
    """
    Custom frame which acts as a retractable sidebar

    Parameters
    ----------
    parent : any
        The parent widget in which the sidebar is contained

    stick_to : any
        The widget to which the sidebar occupies and expands / collapses in

    emerge_from : str
        The side which the sidebar expands from and collapses into.
        Either 'left' [-->] or 'right' [<--].
        Defaults to 'right'

    rel_width : float
        The percentage of width that a fully opened sidebar will occupy in the widget
        Defaults to 0.25 (25%)

    rel_height : float
        The percentage of height that a fully opened sidebar will occupy in the widget
        Defaults to 1 (100%)

    animation_type : str
        The type of animation for expanding and collapsing.
        'glide' indicates a staggered animation, using increments at intervals.
        'instant' indicates a single jump straight to the destination (default)
    """
    def __init__(self,
                 parent: any,
                 emerge_from: Literal["left", "right"] = "right",
                 width: float = 0.25,
                 height: float = 1,
                 animation_type: Literal["glide", "instant"] = "instant",
                 **kwargs):

        # If sidebar will stick to parent
        self.stick_to = parent
        self.stick_to.update()
        # Set width and height
        self.width = 900*width
        self.rel_width = self.width
        rel_height = 600*height

        # Initialise frame
        super().__init__(self.stick_to,
                         width=self.width,
                         height=rel_height,
                         **kwargs)
        self.propagate(False)

        # Set boundaries from sidebar
        if emerge_from == "right":
            # self.left_margin = self.stick_to.winfo_width() - self.width
            self.left_margin = 900 - self.width
            self.right_margin = 901
            self.expand_direction = "left"
            self.collapse_direction = "right"
            self.x = self.right_margin
        else:
            self.left_margin = -self.width - 1
            self.right_margin = 0
            self.expand_direction = "right"
            self.collapse_direction = "left"
            self.x = self.left_margin

        # Initialise attributes for processing
        self.animation_type = animation_type
        self.movement_increment = 0
        self.is_active = False
        self.expand_loop_id = None
        self.collapse_loop_id = None

    def _glide_right(self):
        """
        Completes a step of the gliding right animation
        """
        # If sidebar has not reached destination
        if self.x < self.right_margin:
            # If sidebar will exceed right margin if incremented by amount
            if self.x + self.movement_increment > self.right_margin:
                movement_amount = self.right_margin - self.x
            else:
                movement_amount = self.movement_increment
            # Move sidebar
            self.place(x=self.x+movement_amount, y=0)
            self.stick_to.update()
            self.x += movement_amount
        else:
            self.stop()

    def _glide_left(self):
        """
        Completes a step of the gliding left animation
        """
        # If sidebar has not reached destination
        if self.x > self.left_margin:
            # If sidebar will exceed left margin if incremented by amount
            if self.x - self.movement_increment < self.left_margin:
                movement_amount = self.left_margin - self.x
            else:
                movement_amount = -self.movement_increment
            # Move sidebar
            self.place(x=self.x+movement_amount, y=0)
            self.stick_to.update()
            self.x += movement_amount
        else:
            self.stop()

    def _jump_right(self):
        """
        Moves the sidebar to the right position in one go
        """
        # Move to the right margin in one go
        self.place(x=self.right_margin,
                   y=0)
        self.lift()

    def _jump_left(self):
        """
        Moves the sidebar to the left position in one go
        """
        # Move to the left margin in one go
        self.place(x=self.left_margin,
                   y=0)
        self.lift()

    def expand(self, increment: int = 15, interval: int = 10):
        """
        Expand the sidebar

        Parameters
        ----------
        increment : int
            The number of pixels the sidebar moves per increment

        interval : int
            The number of ms between increment
        """
        if self.animation_type == "glide":
            if not self.is_active:
                self.movement_increment = increment
                # Raise frame above other widgets
                self.lift()
                self.is_active = True
                self._animation_loop("expand", interval)
        else:
            self.lift()
            if self.expand_direction == "right":
                self._jump_right()
            else:
                self._jump_left()

    def collapse(self, increment: int = 15, interval: int = 10):
        """
        Collapse the sidebar

        Parameters
        ----------
        increment : int
            The number of pixels the sidebar moves per increment

        interval : int
            The number of ms between increment
        """
        if self.animation_type == "glide":
            if not self.is_active:
                self.movement_increment = increment
                self.is_active = True
                # Enter recursive loop
                self._animation_loop("collapse", interval)
        else:
            if self.collapse_direction == "left":
                self._jump_left()
            else:
                self._jump_right()

    def _animation_loop(self, mode: str, interval: int = 5):
        """
        Keeps looping the animation until it is complete

        Parameters
        ----------
        mode : str
            The mode for the animation, either 'expand' or 'collapse'

        interval : int
            The number of ms between frames
        """
        if self.is_active:
            if mode == "expand":
                if self.expand_direction == "left":
                    self._glide_left()
                else:
                    self._glide_right()
                # Recursive element
                self.expand_loop_id = self.after(interval, self._animation_loop, "expand", interval)
            else:
                if self.collapse_direction == "left":
                    self._glide_left()
                else:
                    self._glide_right()
                # Recursive element
                self.collapse_loop_id = self.after(interval, self._animation_loop, "collapse", interval)

    def stop(self):
        """
        Stop the sidebar animation
        """
        if self.expand_loop_id is not None:
            self.after_cancel(self.expand_loop_id)
        elif self.collapse_loop_id is not None:
            self.after_cancel(self.collapse_loop_id)
        self.is_active = False


class AccountSidebar(Sidebar):
    """
    Custom sidebar that displays the customer account options on screen

    Parameters
    ----------
    parent : any
        The parent widget in which the sidebar is contained

    app : any
        The main window of the application which acts as a controller for the application
    """
    def __init__(self,
                 parent: any,
                 app: any):
        # Inherit attributes from the sidebar class
        super().__init__(parent,
                         emerge_from="right",
                         animation_type="glide",
                         width=0.27,
                         fg_color=colours.get_primary_colour())
        self.app = app

        # Widgets
        title_frame = Frame(self,
                            fg_color=colours.get_primary_colour())
        title_frame.pack(padx=(10, 0), pady=10, fill="x")
        title_frame.grid_columnconfigure(0, weight=4, uniform="uniform")
        title_frame.grid_columnconfigure(1, weight=2, uniform="uniform")
        title_label = Label(title_frame,
                            text="Your    account",
                            font=("Poppins Regular", 20),
                            fg_color=colours.get_primary_colour(),
                            max_line_length=7)
        title_label.grid(row=0, column=0, sticky="W")

        back_button = FilledButton(title_frame,
                                   command=lambda: self.collapse(),
                                   image_file="back_icon_to_right.png",
                                   image_width=30,
                                   image_height=30,
                                   border_width=0)
        back_button.grid(row=0, column=1)

        turtle_image = Label(self,
                             image_file="happy_turtle.png",
                             image_width=100,
                             image_height=100,
                             fg_color=colours.get_primary_colour())
        turtle_image.pack(pady=(5, 15))

        details_button = FilledButton(self,
                                      command=lambda: self.app.load_frame("MyProfileFrame"),
                                      text="My profile")
        details_button.pack(pady=(0, 15))
        card_button = FilledButton(self,
                                   command=lambda: self.app.load_frame("MyCardsFrame"),
                                   text="My cards")
        card_button.pack(pady=(0, 15))
        orders_button = FilledButton(self,
                                     command=lambda: self.app.load_frame("MyOrdersFrame"),
                                     text="My orders")
        orders_button.pack()

        logout_button = FilledButton(self,
                                     command=lambda: self.app.logout(),
                                     text="Logout")
        logout_button.pack(side="bottom", pady=15)


# UPDATE WITH NEWEST VERSION
class ImageProgressBar(tk.Frame):
    # Custom progress bar designed by myself but inspired by the progress bar designed by https://github.com/TomSchimansky
    def __init__(self,
                 parent: any,
                 image_width: int = 100,
                 image_height: int = 100,
                 span: int = 500,
                 border_width: int = 2,
                 border_color: str = "Black",
                 fg_color: str = "White",
                 orientation: Literal["horizontal", "vertical"] = "horizontal",
                 mode: Literal["determinate", "indeterminate"] = "determinate",
                 indeterminate_style: Literal["bounce", "loop"] = "bounce",
                 start_off: bool = False,
                 end_off: bool = False,
                 reverse: bool = False,
                 trail_colour: str = "Red"):
        """
        An animated Tkinter progress bar widget that display images.

        Parameters
        ----------
        parent : any
            The widget which contains the progress bar

        image_file : str
            The file path of the image

        image_width : int
            The width of the image in pixels

        image_height : int
            The height of the image in pixels

        span : int
            The distance in pixels that the progress bar spans (width for horizontal bar and height for vertical bar)

        border_width: int
            The border width

        border_color : str
            The border colour

        fg_color : str
            The foreground colour

        orientation : str
            The orientation, either "horizontal" or "vertical"

        mode : str
            The mode, either "determinate" (definite progress) or "indeterminate" (indefinite progress)

        indeterminate_style : str
            The style of indefinite progress, either "loop" (go from side A to side B, jump back to side A and
            repeat) or "bounce" (bounce between side A and side B)

        start_off : bool
            Whether the image should start off-screen, either True or False

        end_off : bool
            Whether the image should end off-screen, either True or False

        reverse : bool
            Reverse the direction of the progress bar (default is left to right / up to down), either True or False

        trail_colour : str
            The colour of the trail left by a "determinate" bar
        """
        # Argument and keyword argument validation
        if orientation not in ["horizontal", "vertical"]:
            raise ValueError(f"'{orientation}' is not a valid value for 'orientation'. 'orientation' must be either 'horizontal' or 'vertical'.")
        else:
            self.orientation = orientation

        int_dict = {"image_width": image_width,
                    "image_height": image_height,
                    "border_width": border_width,
                    "span": span}
        for key, value in int_dict.items():
            current_key = key
            if int(value) < value:
                raise ValueError(f"'{current_key}' must be an integer.")
        self.image_width = image_width
        self.image_height = image_height

        if mode not in ["determinate", "indeterminate"]:
            raise ValueError(f"'{mode}' is not a valid value for 'mode'. 'mode' must be 'determinate' or 'indeterminate'.")
        else:
            self.mode = mode

        if indeterminate_style not in ["loop", "bounce"]:
            raise ValueError(
                f"'{indeterminate_style}' is not a valid value for 'indeterminate_style'. 'indeterminate_style' must be 'loop' or 'bounce'.")
        else:
            self.indeterminate_style = indeterminate_style

        bool_dict = {"start_off": start_off,
                     "end_off": end_off,
                     "reverse": reverse}
        for key, value in bool_dict.items():
            if type(value) != bool:
                raise ValueError(f"'{value}' is not a valid value for '{key}'. '{key}' must be either True or False.")
        self.start_off = start_off
        self.end_off = end_off
        self.reverse = reverse

        try:
            resized_image = Image.open(f"{backend.get_directory('images')}happy_turtle_flipped.png").resize((image_width, image_height))
        except FileNotFoundError:
            resized_image = Image.open(backend.get_directory("images") + "placeholder.png").resize((image_width, image_height))

        # Initialise outer frame
        if orientation == "horizontal":
            height = image_height
            width = span
        else:
            height = span
            width = image_width
        super().__init__(parent,
                         width=width,
                         height=height,
                         bg=fg_color,
                         highlightthickness=border_width,
                         highlightcolor=border_color,
                         highlightbackground=border_color)
        self.propagate(False)

        # Initialise inner frame
        inner_frame = tk.Frame(self,
                               width=width,
                               height=height,
                               bg=fg_color,
                               highlightthickness=0)
        inner_frame.pack(padx=1,
                         pady=1,
                         fill="both",
                         expand=True)
        inner_frame.propagate(False)

        self.fg_color = fg_color

        self.trail_colour = trail_colour

        self.is_active = False
        self.animation_loop_id = None
        self.trail = None

        if self.orientation == "horizontal":
            # Allow the image to go off-screen on the left side if needed
            if (not self.reverse and self.start_off) or (self.reverse and self.end_off):
                start_of_canvas = 0 - self.image_width
                width += self.image_width
            else:
                start_of_canvas = 0
            # Allow the image to go off-screen on the right side if needed
            if (not self.reverse and self.end_off) or (self.reverse and self.start_off):
                end_of_canvas = width
            else:
                end_of_canvas = width - self.image_width
            self.bar_span = abs(end_of_canvas)

            # Place image in the vertical center
            self.y_pos = (height / 2) - (self.image_height / 2)
            if reverse:
                # Start image at right side
                self.starting_degrees = 90
                self.starting_coords = (end_of_canvas, self.y_pos)
            else:
                # Start image at left side
                self.starting_degrees = -90
                self.starting_coords = (start_of_canvas, self.y_pos)
        else:
            # Allow the image to go off-screen on the top side if needed
            if (not self.reverse and self.start_off) or (self.reverse and self.end_off):
                # Set start to be offset at the top
                start_of_canvas = 0 - self.image_height
                height += self.image_height
            else:
                start_of_canvas = 0
            # Allow the image to go off-screen on the bottom side if needed
            if (not self.reverse and self.end_off) or (self.reverse and self.start_off):
                end_of_canvas = height
            else:
                # Set end to be just before the bottom side so the image is flush against the side
                end_of_canvas = height - self.image_height
            # How far the bar spans i.e. the bar's height
            self.bar_span = abs(end_of_canvas)

            # Place image in horizontal center
            self.x_pos = (width / 2) - (self.image_width / 2)
            if reverse:
                # Start image at bottom side
                self.starting_coords = (self.x_pos, end_of_canvas)
                self.starting_degrees = 90
            else:
                # Start image at top side
                self.starting_coords = (self.x_pos, start_of_canvas)
                self.starting_degrees = -90

        self.current_degrees = self.starting_degrees
        # Create canvas which contains the bar
        self.canvas = tk.Canvas(inner_frame,
                                bg=self.fg_color,
                                highlightcolor=self.fg_color,
                                highlightthickness=0,
                                width=width,
                                height=height)
        # Place canvas
        if self.orientation == "horizontal":
            self.canvas.place(x=start_of_canvas, y=0)
        else:
            self.canvas.place(x=0, y=start_of_canvas)
        # Create reference to avoid image being dumped by garbage collector
        parent.image = self.image = ImageTk.PhotoImage(resized_image)
        # Create image
        self.image_id = self.canvas.create_image(self.starting_coords, anchor="nw", image=self.image)

    def start(self,
              percentage_to_move: float = 0.01,
              interval: int = 20):
        """
        Starts the progress bar, moving by a percentage of the width each step with each step being interval ms apart.

        Parameters
        ----------
        percentage_to_move : float
            The percentage of the progress bar each step should move, defaults to 0.01 (1%)

        interval : int
            The number of ms between each step
        """
        if not self.is_active:
            self.is_active = True
            # Enter recursive function
            self._animation_loop(percentage_to_move, interval)

    def _draw_trail(self):
        """
        Draws the trail left by the 'determinate' mode.
        """
        if self.trail:
            self.canvas.delete(self.trail)
        if self.orientation == "horizontal":
            if self.reverse:
                # Rectangle will start at right and move left
                rect_coords = (self._get_current_coord() + self.image_width,
                               self.starting_coords[1],
                               self.bar_span + (2 * self.image_width),
                               self.starting_coords[1] + self.image_height)
            else:
                # Rectangle will start at left and move right
                rect_coords = (self.starting_coords[0],
                               self.starting_coords[1],
                               self._get_current_coord(),
                               self.starting_coords[1] + self.image_height)
            self.trail = self.canvas.create_rectangle(rect_coords,
                                                      outline=self.trail_colour,
                                                      fill=self.trail_colour)
        else:
            if self.reverse:
                # Rectangle will start at bottom and move up
                rect_coords = (self.starting_coords[0],
                               self._get_current_coord() + self.image_height,
                               self.starting_coords[0] + self.image_width,
                               self.bar_span + (2 * self.image_height))
            else:
                # Rectangle will start at top and move down
                rect_coords = (self.starting_coords[0],
                               self.starting_coords[1],
                               self.starting_coords[0] + self.image_width,
                               self._get_current_coord())
            self.trail = self.canvas.create_rectangle(rect_coords,
                                                      outline=self.trail_colour,
                                                      fill=self.trail_colour)

    def step(self,
             percentage_to_move):
        """
        Performs one step of the progress bar animation, moving by a percentage of the width.
        A step will conform to rules stated when initialising.

        Parameters
        ----------
        percentage_to_move : float
            The percentage of the progress bar each step should move, defaults to 0.01 (1%)
        """
        if self.current_degrees is None:
            self.current_degrees = self.starting_degrees

        stop = False

        if self.mode == "determinate":
            if self.reverse:
                stopping_degrees = 270
            else:
                stopping_degrees = 90
            # If adding the percentage to move would cause the bar to exceed its stopping point
            if self.current_degrees + (180 * percentage_to_move) > stopping_degrees:
                # Set degrees to stop the bar at its stopping point
                self.current_degrees = stopping_degrees
                stop = True
            else:
                # Move the bar by the percentage to move
                self.current_degrees += (180 * percentage_to_move)

            self._draw_trail()

        if self.mode == "indeterminate":
            if self.indeterminate_style == "bounce":
                # Move bar by percentage
                self.current_degrees += (180 * percentage_to_move)
                # Flip image when it reaches the end
                if self.current_degrees >= 90:
                    self.image = ImageTk.PhotoImage(Image.open(f"{backend.get_directory('images')}happy_turtle.png").resize((self.image_width, self.image_height)))
                else:
                    self.image = ImageTk.PhotoImage(Image.open(f"{backend.get_directory('images')}happy_turtle_flipped.png").resize((self.image_width, self.image_height)))
                # Refresh counter in order to avoid counting to infinity
                if self.current_degrees > 270:
                    self.current_degrees -= 360
            else:
                if self.reverse:
                    stopping_point = 270
                else:
                    stopping_point = 90

                # If the bar is at its stopping point
                if self.current_degrees == stopping_point:
                    # Reset progressbar
                    self.reset(stop=False)
                # If adding the percentage to move would cause the bar to exceed its stopping point
                elif self.current_degrees + (180 * percentage_to_move) > stopping_point:
                    # Set degrees to stop the bar at its stopping point
                    self.current_degrees = stopping_point
                else:
                    # Move the bar by the percentage to move
                    self.current_degrees += (180 * percentage_to_move)

        # Delete image
        self.canvas.delete(self.image_id)
        # Redraw image
        if self.orientation == "horizontal":
            self.image_id = self.canvas.create_image(self._get_current_coord(),
                                                     self.y_pos,
                                                     anchor="nw",
                                                     image=self.image)
        else:
            self.image_id = self.canvas.create_image(self.x_pos,
                                                     self._get_current_coord(),
                                                     anchor="nw",
                                                     image=self.image)

        if stop:
            self.stop()

    def _get_current_coord(self):
        """
        Gets the current variable coordinates for the progressbar.
        On horizontal mode, this returns the x coordinate for the bar.
        On vertical mode, this returns the y coordinate for the bar

        Returns
        -------
        float
            The variable coordinates of the bar
        """
        # Use formula based on transformed sin wave that returns a value from 0 to 1
        # Let this value become the percentage that the bar has moved
        percentage_of_bar = (math.sin(math.radians(self.current_degrees)) + 1) / 2
        return percentage_of_bar * self.bar_span

    def get_current_percentage(self,
                               dp: int = 2):
        """
        Gets the current percentage of a "determinate" progress bar.
        Performs no action if mode is set to "indeterminate".

        Parameters
        ----------
        dp : int
            The number of decimal places the percentage should be rounded to
        """
        return round((math.sin(math.radians(self.current_degrees)) + 1) / 2, dp)

    def _animation_loop(self,
                        percentage_to_move: float = 0.01,
                        interval: int = 20):
        """
        Recursive method used to loop the progress bar until stopped.

        Parameters
        ----------
        percentage_to_move : float
            The percentage of the progress bar each step should move.
            Defaults to 0.01 (1%)

        interval : int
            The number of ms between each step
        """
        if self.is_active:
            self.step(percentage_to_move)
            self.animation_loop_id = self.after(interval, self._animation_loop, percentage_to_move, interval)

    def reset(self, stop=True):
        """
        Returns the bar to its default state, and stops the bar if stop is True.

        Parameters
        ----------
        stop : bool
            Whether the progress bar should stop after resetting
        """
        if stop:
            self.stop()
        if self.trail:
            self.canvas.delete(self.trail)
        self.canvas.delete(self.image_id)
        self.current_degrees = self.starting_degrees
        self.image_id = self.canvas.create_image(self.starting_coords,
                                                 anchor="nw",
                                                 image=self.image)

    def stop(self):
        """
        Stops the progress bar.
        """
        if self.animation_loop_id is not None:
            self.after_cancel(self.animation_loop_id)
        self.is_active = False


class FilledButton(ctk.CTkButton):
    """
    Format for CTkButton that is yellow and bordered
    """
    def __init__(self,
                 parent,
                 height=45,
                 border_width=1,
                 border_color="Black",
                 corner_radius=15,
                 fg_color=colours.get_button_colour(),
                 bg_color="",
                 hover_color=colours.get_hover_colour(),
                 text="",
                 image_file="",
                 image_width=100,
                 image_height=100,
                 text_color="Black",
                 font=("Inter Regular", 20),
                 **kwargs):
        # Make background the same as foreground unless specified not to
        if bg_color == "":
            bg_color = fg_color

        # Load custom image
        if image_file != "":
            new_image = backend.load_and_resize_image(image_file, image_width, image_height)
        else:
            new_image = None

        super().__init__(parent,
                         image=new_image,
                         text=text,
                         text_color=text_color,
                         font=font,
                         height=height,
                         border_width=border_width,
                         border_color=border_color,
                         corner_radius=corner_radius,
                         fg_color=fg_color,
                         bg_color=bg_color,
                         **kwargs)
        self.image = new_image
        self.configure(hover_color=hover_color)


class BlankButton(FilledButton):
    """
    Format for CTkButton that is white and unbordered
    """
    def __init__(self, parent: any, **kwargs):
        super().__init__(parent,
                         fg_color=colours.get_bg_colour(),
                         border_width=0,
                         **kwargs)


class UnborderedFilledButton(FilledButton):
    """
    Format for CTkButton that is yellow and unbordered
    """
    def __init__(self, parent: any, **kwargs):
        super().__init__(parent, border_width=0, **kwargs)


class ToggleableButton(BlankButton):
    """
    Custom toggleable button class

    Parameters
    ----------
    parent : any
        The parent widget in which the toggleable button is contained

    on_image_file : str
        The name of the image file when the button is toggled on

    off_image_file : str
        The name of the image file when the button is toggled off

    image_width : int
        The width of the image

    image_height : int
        The height of the image

    width : int
        The width of the button

    height : int
        The height of the button

    fg_color : str
        The foreground colour of the button

    And any other keywords accepted by the CTkButton class
    """
    def __init__(self,
                 parent: any,
                 on_image_file: str,
                 off_image_file: str,
                 image_width: int = 30,
                 image_height: int = 30,
                 width: int = 30,
                 height: int = 30,
                 **kwargs):
        self.on = False
        self.off_image = backend.load_and_resize_image(off_image_file,
                                                       image_width,
                                                       image_height)
        self.on_image = backend.load_and_resize_image(on_image_file,
                                                      image_width,
                                                      image_height)
        super().__init__(parent,
                         height=height,
                         width=width,
                         image_file=off_image_file,
                         image_width=image_width,
                         image_height=image_height,
                         hover=False,
                         **kwargs)

    def get_state(self):
        """
        Get the state of the button

        Returns
        -------
        bool
            Whether the button is on or off.
            The value will be True if the button is on and False if not
        """
        return self.on

    def switch_on(self):
        """
        Toggle the button on
        """
        self.configure(image=self.on_image)
        self.image = self.on_image
        self.on = True

    def switch_off(self):
        """
        Toggle the button off
        """
        self.configure(image=self.off_image)
        self.image = self.off_image
        self.on = False

    def switch_state(self):
        """
        Switch the state of the button
        """
        if self.on:
            self.switch_off()
        else:
            self.switch_on()


class ProductCompareButton(ToggleableButton):
    """
    Custom toggleable button for the product compare icon

    Parameters
    ----------
    parent : any
        The parent widget in which the product compare button is contained

    app : any
        The main window of the application that acts as the controller for the application

    product : dict
        The product for which the product compare button is linked to.
        Keys should state the product attribute names.
        Values should state the values of said attributes

    command : callable
        The command triggered when the button is clicked
    """
    def __init__(self,
                 parent: any,
                 app: any,
                 product: dict = None,
                 command: callable = None):
        self.app = app
        self.product = product
        super().__init__(parent,
                         command=command,
                         off_image_file="product_compare_icon.png",
                         on_image_file="product_compare_icon_blue.png",
                         image_width=20,
                         image_height=20)
        # If the product is already in the compare system
        if self.app.get_current_user().get_compare_bucket().search(product.get("product_id")):
            # Automatically switch the button on
            self.switch_on()
        else:
            self.switch_off()

    def get_product(self):
        """
        Get the linked product

        Returns
        -------
        dict
            The product linked to the product compare button
        """
        return self.product


class StarButton(ToggleableButton):
    """
    Custom toggleable button in the shape of the star that is used for rating products

    Parameters
    ----------
    parent : any
        The parent widget in which the star button is contained

    score : int
        The score that this star button represents when clicked

    command : callable
        The command triggered when the button is clicked
    """
    def __init__(self,
                 parent: any,
                 score: int = 1,
                 command: callable = None):
        self.score = score
        super().__init__(parent,
                         command=command,
                         off_image_file="star_icon.png",
                         on_image_file="star_icon_on.png",
                         image_width=20,
                         image_height=20)

    def get_score(self):
        """
        Get the score that the button represents when clicked

        Returns
        -------
        int
            The score, out of 5, that the button represents when clicked
        """
        return self.score


class HideableLabel(Frame):
    """
    Custom label which allows its text to be hidden when needed

    Parameters
    ----------
    parent : any
        The parent in which the hideable label is contained

    fg_color : str
        The foreground colour for the hideable label

    And any other keywords accepted by the CTkLabel class
    """
    def __init__(self,
                 parent: any,
                 fg_color: str = colours.get_bg_colour(),
                 **kwargs):
        super().__init__(parent, fg_color=fg_color)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=2, uniform="uniform")
        self.grid_columnconfigure(1, weight=1, uniform="uniform")

        self.hidden = False

        self.details_label = Label(self,
                                   fg_color=fg_color,
                                   **kwargs)
        self.current_text = self.details_label.cget("text")
        self.details_label.grid(row=0, column=0, padx=2, pady=2, sticky="NSW")

        self.visibility_button = ToggleableButton(self,
                                                  width=30,
                                                  command=lambda: self.switch_visibility(),
                                                  off_image_file="hidden_icon.png",
                                                  on_image_file="not_hidden_icon.png",
                                                  image_width=20,
                                                  image_height=20)
        self.visibility_button.grid(row=0, column=1, padx=2, pady=2, sticky="NSE")

    def set_text(self, new_text):
        """
        Set the text of the label

        Parameters
        ----------
        new_text : str
            The
        """
        # A custom method is needed here to set the text as CTkLabel's configure method
        # would override the hidden state when invoked
        self.current_text = new_text

    def get_state(self):
        """
        Gets whether the text is hidden

        Returns
        -------
        bool
            Whether the text is hidden or not.
            The value will be True if the hidden and False if not
        """
        return self.hidden

    def reveal(self):
        """
        Reveals any hidden text
        """
        self.details_label.configure(text=self.current_text)
        self.visibility_button.switch_off()
        self.hidden = False

    def hide(self, mask_character: str = "*", static_mask: bool = False, static_mask_length: int = 8):
        """
        Hides any visible text

        Parameters
        ----------
        mask_character : str
            The character that makes up the mask

        static_mask : bool
            A value that indicates whether the mask's length is static no matter the text length.
            A value will be True if the mask should always be a set length or False if it follows the text's length

        static_mask_length : int
            The length that a static (independent of the current text) mask should be
        """
        if static_mask:
            self.details_label.configure(text=mask_character*static_mask_length)
        else:
            self.details_label.configure(text=mask_character*len(self.current_text))
        self.visibility_button.switch_on()
        self.hidden = True

    def switch_visibility(self):
        """
        Switches the visibility of the text
        """
        if self.hidden:
            self.reveal()
        else:
            self.hide()


class Entry(Frame):
    """
    Custom format for the CTkEntry widget which enables visibility to be toggled on / off and
    the widget to be used as both output and input

    Parameters
    ----------
    parent : any
        The parent widget in which the entry widget is contained

    hideable : bool
        Whether the input in the entry widget can be hidden.
        The value will be True if input can be hidden and False if not

    height : int
        The height of the widget

    bg_color : str
        The background colour

    border_width : int
        The width of the border

    corner_radius : int
        The radius of any circular corner

    placeholder_text : str
        Help text that should be visible when the widget is not in focus

    font : tuple
        The font name and size that the widget should use

    hideable : bool
        A value used to indicate whether the input should be hideable.
        The value will be True is it can be hidden and False if not

    mask_character : str
        The character used to hide any input

    toggleable : bool
        A value used to indicate whether the input should be toggled from view mode to edit mode.
        The value will be True is it can be toggled and False if not

    current_text : str
        The value displayed when the widget is in view mode
    """
    def __init__(self,
                 parent: any,
                 bg_color: str = "White",
                 border_width: int = 1,
                 corner_radius: int = 10,
                 font: tuple = ("Inter Regular", 14),
                 placeholder_text: str = "",
                 
                 hideable: bool = False,
                 mask_character: str = "*",
                 toggleable: bool = False,
                 current_text: str = "",
                 validated: bool = True,
                 table_name: str = "",
                 field_name: str = "",
                 **kwargs):
        if validated:
            height = 50
        else:
            height = 35
        super().__init__(parent,
                         height=height,
                         border_width=0,
                         corner_radius=corner_radius,
                         fg_color=bg_color)
        self.grid_propagate(False)
        if validated:
            self.grid_rowconfigure(0, weight=2, uniform="uniform")
            self.grid_rowconfigure(1, weight=1, uniform="uniform")
        else:
            self.grid_rowconfigure(0, weight=999, uniform="uniform")
            self.grid_rowconfigure(1, weight=1, uniform="uniform")
        self.grid_columnconfigure(0, weight=1)

        self.entry_frame = Frame(self,
                                 border_width=border_width,
                                 bg_color=bg_color,
                                 corner_radius=corner_radius,
                                 **kwargs)
        self.entry_frame.grid(row=0, column=0, sticky="NSEW")
        self.entry_frame.grid_propagate(False)
        self.entry_frame.grid_rowconfigure(0, weight=1)
        self.entry_frame.grid_columnconfigure(0, weight=200, uniform="uniform")
        self.entry_frame.grid_columnconfigure(1, weight=100, uniform="uniform")
        self.entry_frame.grid_columnconfigure(2, weight=100, uniform="uniform")
        self.entry_frame.grid_columnconfigure(3, weight=1)
        
        # Attributes
        self.parent = parent
        self.hideable = hideable
        self.mask_character = mask_character
        self.toggleable = toggleable
        self.mode = None
        self.current_text = current_text
        self.validated = validated
        self.is_valid = not validated
        self.table_name = table_name
        self.field_name = field_name
        self.previous_input = ""

        # Define three widgets
        self.entry_var = ctk.StringVar()
        self.entry_widget = ctk.CTkEntry(self.entry_frame,
                                         fg_color="White",
                                         border_width=0,
                                         corner_radius=corner_radius,
                                         placeholder_text=placeholder_text,
                                         font=font)

        self.visibility_button = ToggleableButton(self.entry_frame,
                                                  width=30,
                                                  command=lambda: self.switch_visibility(),
                                                  off_image_file="hidden_icon.png",
                                                  on_image_file="not_hidden_icon.png",
                                                  image_width=15,
                                                  image_height=15,
                                                  corner_radius=corner_radius)

        self.edit_icon = ToggleableButton(self.entry_frame,
                                          width=30,
                                          command=lambda: self.switch_mode(),
                                          on_image_file="close_icon.png",
                                          off_image_file="edit_icon.png",
                                          image_width=15,
                                          image_height=15)

        self.info_label = Label(self,
                                fg_color=bg_color,
                                font=("Inter Regular", 10),
                                text_color="Red",
                                anchor="w")
        self.info_label.grid(row=1, column=0, pady=3, sticky="NSEW")

        if validated:
            self.maximum_length = crud.get_max_length(self.field_name)
            self.entry_widget.configure(textvariable=self.entry_var)
            self.entry_var.trace_add("write", self.validate)
        else:
            self.maximum_length = None

        if hideable:
            self.hidden = True
            if toggleable:
                # Toggleable and hideable, place all three widgets (entry, hide icon, toggle icon)
                self.entry_widget.grid(row=0, column=0, padx=6, pady=6, sticky="EW")
                self.visibility_button.grid(row=0, column=1, padx=6, pady=6, sticky="NSE")
                self.edit_icon.grid(row=0, column=2, padx=6, pady=6, sticky="NSE")
                # Default mode is view
                self.set_to_view()
            else:
                # Not toggleable but hideable, place entry and hide icon only
                self.entry_widget.grid(row=0, column=0, padx=6, pady=6, columnspan=2, sticky="EW")
                self.visibility_button.grid(row=0, column=2, padx=6, pady=6, sticky="NSE")
                # The only mode available here is the edit mode
                self.set_to_edit()
                self.clear()
        else:
            self.hidden = False
            if toggleable:
                # Toggleable but not hideable, place entry and toggle icon only
                self.entry_widget.grid(row=0, column=0, padx=6, pady=6, columnspan=2, sticky="EW")
                self.edit_icon.grid(row=0, column=2, padx=6, pady=6, sticky="NSE")
                # Default mode is view
                self.set_to_view()
            else:
                # Neither toggleable nor hideable, place entry only
                self.entry_widget.grid(row=0, column=0, padx=6, pady=6, columnspan=3, sticky="NSEW")
                # The only mode available here is the edit mode
                self.set_to_edit()
                self.clear()

    def get(self):
        """
        Gets the input currently present in entry widget.
        Mimics the CTkEntry's get method

        Returns
        -------
        str
            The input currently present in the entry widget
        """
        if self.mode == "view":
            return self.current_text
        else:
            return self.entry_widget.get()

    def focus_set(self):
        """
        Set the text cursor to be active within the entry widget.
        Mimics the CTkEntry's focus_set method
        """
        self.entry_widget.focus_set()

    def clear(self):
        """
        Clear the widget
        """
        self.entry_widget.focus_set()
        if self.toggleable:
            self.set_to_view()
        else:
            # Fill the widget with nothing
            self.fill_with("")
        if self.hideable:
            self.hide()
        self.is_valid = False
        self.set_as_neutral()
        # Focus on another widget to allow placeholder text to pop up
        self.parent.focus_set()

    def fill_with(self, text: str):
        """
        Fill the entry widget with text

        Parameters
        ----------
        text : str
            The text to insert into the entry widget
        """
        original_state = self.entry_widget.cget("state")
        # Enable the entry widget so that text can be disabled
        self.entry_widget.configure(state="normal")
        self.entry_widget.delete(0, "end")
        self.entry_widget.insert(0, text)
        # Ensure no maximum character message is displayed in view mode after tampering with the input
        if original_state == "disabled":
            self.set_as_neutral()
        self.entry_widget.configure(state=original_state)

    def configure(self, **kwargs):
        """
        Mimics the CTkEntry's configure method
        """
        self.entry_widget.configure(**kwargs)

    def hide(self):
        """
        Hide any visible input
        """
        if self.mode == "view":
            text_input = self.current_text
        else:
            self.entry_widget.configure(show="")
            text_input = self.entry_widget.get()
        self.entry_widget.configure(show=self.mask_character)
        self.fill_with(text_input)
        self.visibility_button.switch_on()
        self.hidden = True

    def reveal(self):
        """
        Reveal any hidden input
        """
        self.entry_widget.configure(show="")
        if self.mode == "view":
            text_input = self.current_text
        else:
            text_input = self.entry_widget.get()
        self.fill_with(text_input)
        self.visibility_button.switch_off()
        self.hidden = False

    def switch_visibility(self):
        """
        Switch the visibility of the input
        """
        if self.hidden:
            self.reveal()
        else:
            self.hide()

    def set_to_view(self):
        """
        Switch the widget's mode to view
        """
        # Switch mode, prevent further input and toggle icon
        self.mode = "view"
        self.entry_widget.configure(state="disabled")
        self.edit_icon.switch_off()

        # Hide or unhide according to the visibility currently selected
        if self.hidden:
            self.hide()
        else:
            self.reveal()

    def set_to_edit(self):
        """
        Enable the widget to be edited
        """
        # Switch mode, allow input and toggle icon
        self.mode = "edit"
        self.entry_widget.configure(state="normal")
        self.edit_icon.switch_on()
        self.entry_widget.focus_set()

        # Hide or unhide according to the visibility currently selected
        if self.hidden:
            self.hide()
        else:
            self.reveal()

    def switch_mode(self):
        """
        Switch the widget's mode between viewing and editing
        """
        if self.mode == "view":
            self.set_to_edit()
        else:
            self.set_to_view()

    def validate(self, var=None, index=None, mode=None):
        """
        Controls entry validation and ensure a maximum length is not breached
        """
        # If there is a max length and the input is greater than it
        if self.maximum_length and len(self.entry_var.get()) > self.maximum_length:
            self.entry_var.set(self.previous_input)

        self.is_valid = True
        if self.validated:
            # If entry is not blank
            if self.entry_var.get() != "":
                # Validate according to table name and field name
                if self.table_name == "Customer":
                    is_valid, error_message = backend.validate_customer(self.field_name, self.entry_var.get())
                elif self.table_name == "Payment_Card":
                    is_valid, error_message = backend.validate_payment_card(self.field_name, self.entry_var.get())
                elif self.table_name == "Orders":
                    is_valid, error_message = backend.validate_order(self.field_name, self.entry_var.get())
                elif self.table_name == "Supplier":
                    is_valid, error_message = backend.validate_supplier(self.field_name, self.entry_var.get())
                elif self.table_name == "Staff":
                    is_valid, error_message = backend.validate_staff(self.field_name, self.entry_var.get())
                else:
                    is_valid, error_message = backend.validate_product(self.field_name, self.entry_var.get())

                if not is_valid:
                    self.is_valid = False
                    self.set_as_invalid(error_message)
                else:
                    self.is_valid = True
                    self.set_as_neutral()
            else:
                # Blank input is not valid but the user is not alerted to this
                self.is_valid = False
                self.set_as_neutral()

        # Do not overwrite any validation messages present
        if self.maximum_length and len(self.entry_var.get()) >= self.maximum_length and self.is_valid:
            print(self.is_valid)
            self.set_info("Maximum character length reached")

        self.previous_input = self.entry_var.get()

    def set_as_neutral(self):
        """
        Set the widget to display that its input is not invalid 
        """
        self.entry_frame.configure(border_color="Black")
        self.set_info("")

    def set_as_invalid(self, error_message: str):
        """
        Set the widget to display that its input is invalid

        Parameters
        ----------
        error_message : str
            The message to be displayed as an error
        """
        self.entry_frame.configure(border_color="Red")
        self.set_info(error_message, "Red")

    def set_info(self, message: str, text_colour: str = "Black"):
        """
        Display a message below the entry widget

        Parameters
        ----------
        message : str
            The message to display

        text_colour : str
            The colour of the message
        """
        self.info_label.configure(text=message, text_color=text_colour)

    def check_if_valid(self):
        """
        Check if the input is valid
        """
        if self.validated:
            return self.is_valid


class Label(ctk.CTkLabel):
    """
    Format for the CTkLabel widget

    Parameters
    ----------
    parent : any
        The parent widget in which the label is contained

    fg_color : str
        The foreground colour of the label

    text : str
        The value of the text which is to be displayed

    font : tuple
        The font of the label.
        The first value should specify the font name and the second value should specify the font size

    text_color : str
        The colour of the text

    max_line_length : int
        The maximum number of characters allowed per line

    justify : str
        The side which multi-line text should be aligned to

    image_file : str
        The name of the image file

    image_width : int
        The width of the image

    image_height : int
        The height of the image

    compound : str
        The side which text should be placed on if an image is also present

    And any other keyword accepted by the CTkLabel class
    """
    def __init__(self,
                 parent: any,
                 fg_color: str = colours.get_bg_colour(),

                 text: str = "",
                 font: tuple = ("Inter Regular", 20),
                 text_color: str = "Black",
                 max_line_length: int = 50,
                 justify: str = "left",

                 image_file: str = "",
                 image_width: int = 100,
                 image_height: int = 100,
                 compound="left",
                 **kwargs):
        # Ensure text conforms with max line length
        new_text = textwrap.fill(str(text), max_line_length)
        super().__init__(parent,
                         text=new_text,
                         font=font,
                         text_color=text_color,
                         fg_color=fg_color,
                         bg_color=fg_color,
                         compound=compound,
                         justify=justify,
                         **kwargs)
        if image_file != "":
            # Create image
            new_image = backend.load_and_resize_image(image_file,
                                                      width=image_width,
                                                      height=image_height)
            self.configure(image=new_image)
            self.image = new_image


class ParentFrame(Frame):
    """
    Custom frame used in to hold different screens within the frontend

    Parameters
    ----------
    parent : any
        The parent widget in which the frame is contained.
        In all cases, this will be the application controller

    fg_color : str
        The foreground colour of the frame
    """
    def __init__(self,
                 parent: any,
                 fg_color: str = colours.get_bg_colour()):
        super().__init__(parent,
                         fg_color=fg_color,
                         width=900,
                         height=600)
        self.grid_propagate(False)


class Treeview(ttk.Treeview):
    """
    Format for ttkTreeview

    Parameters
    ----------
    parent : any
        The parent widget in which the treeview is contained

    columns : list
        The column names
    """
    def __init__(self, parent: any, columns: list):
        super().__init__(parent,
                         columns=columns,
                         show="headings",
                         selectmode="browse")
        # Set column headings
        for column in columns:
            # Use dynamic scaling depending on the number of columns
            self.column(column, width=int(round(225/len(columns), 0)))
            self.heading(column, text=column)

    def _get_selected_record(self):
        """
        Gets the record that is currently in focus

        Returns
        -------
        list | None
            A list of all field values from the selected values
        """
        if not self.focus():
            return None
        else:
            return self.selection()[0]

    def get_selected_values(self):
        """
        Gets the values of the record currently in focus

        Returns
        -------
        list
            The field values for the record
        """
        if self._get_selected_record():
            return self.item(self._get_selected_record())["values"]

    def delete_selected_record(self):
        """
        Delete the record that is currently in focus
        """
        if self._get_selected_record():
            self.delete(self._get_selected_record())

    def clear_tree(self):
        """
        Clears all records from the treeview
        """
        for record in self.get_children():
            self.delete(record)
        
    def populate_tree(self, records: dict):
        """
        Populates a treeview with a set of records

        Parameters
        ----------
        records : tuple
            A tuple whose elements consist of lists of field values
            corresponding to a record
        """
        # Clear the treeview
        self.clear_tree()
        for record in records:
            self.insert('', "end", values=tuple(record.values()))


class Dropdown(ctk.CTkOptionMenu):
    """
    Format for CTkOptionMenu widget

    Parameters
    ----------
    parent : any
        The parent widget in which the frame is contained.

    var_default : str
        The starting option for the dropdown menu

    fg_color : str
        The colour of the dropdown menu itself

    button_color : str
        The colour of the dropdown menu's button

    font : tuple
        The font of the label.
        The first value should specify the font name and the second value should specify the font size

    text_color : str
        The colour of the dropdown text

    And any other keywords accepted by the CTkOptionMenu class
    """
    def __init__(self,
                 parent: any,
                 var_default: Union[str, int],

                 fg_color: str = "White",
                 button_color: str = "#BDBDBD",

                 font: tuple = ("Inter Regular", 16),
                 text_color: str = "Black",
                 **kwargs):
        self.var_default = var_default
        self.dropdown_var = tk.StringVar(parent, value=var_default)
        super().__init__(parent,
                         corner_radius=0,
                         variable=self.dropdown_var,
                         fg_color=fg_color,
                         button_color=button_color,
                         font=font,
                         text_color=text_color,
                         **kwargs)

    def reset(self):
        """
        Reset the dropdown menu to its default state
        """
        self.set(self.var_default)

    def set_default(self, value: str):
        """
        Sets the starting value for the dropdown menu

        Parameters
        ----------
        value : str
            The value which is to be set as the default
        """
        self.dropdown_var.set(value)

    def get_default(self):
        """
        Get the starting value for the dropdown menu
        """
        return self.var_default


class MainLogo(FilledButton):
    """
    Custom button in the form of a logo which redirects to the Browsing Frame

    Parameters
    ----------
    parent : any
        The parent widget in which the back button is contained

    app : any
        The main window of the application which acts as a controller for the application
    """
    def __init__(self,
                 parent: any,
                 app: any):
        super().__init__(parent,
                         image_file="turtle_tennis_icon_ICON_AND_TEXT.png",
                         image_width=100,
                         image_height=100,
                         command=lambda: app.load_frame("BrowsingFrame"),
                         border_width=0,
                         hover=False)


class Topbar(Frame):
    """
    Custom top-bar widget

    Parameters
    ----------
    parent : any
        The parent widget in which the back button is contained

    app : any
        The main window of the application which acts as a controller for the application

    title : str
        The title of the screen
    """
    def __init__(self,
                 parent: any,
                 app: any,
                 title: str = ""):
        super().__init__(parent, fg_color=colours.get_primary_colour())
        self.grid(row=0, column=0, columnspan=2, sticky="NSEW")
        self.grid_columnconfigure(0, weight=2, uniform="uniform")
        self.grid_columnconfigure(1, weight=8, uniform="uniform")
        self.grid_columnconfigure(2, weight=4, uniform="uniform")
        self.grid_rowconfigure(0, weight=1)
        self.parent = parent
        self.app = app

        # Place main logo button in the top left
        mainlogo = MainLogo(self, app)
        mainlogo.grid(row=0, column=0, sticky="W")

        self.title_label = Label(self,
                                 text=title,
                                 font=("Poppins Regular", 20),
                                 fg_color=colours.get_primary_colour())
        self.title_label.grid(row=0, column=1, sticky="E")

        # Defining the buttons
        button_frame = Frame(self, fg_color=colours.get_primary_colour())
        button_frame.grid(row=0, column=2, padx=15, sticky="NSEW")
        button_frame.grid_rowconfigure(0, weight=1)
        button_frame.grid_columnconfigure(0, weight=1, uniform="uniform")
        button_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
        button_frame.grid_columnconfigure(2, weight=1, uniform="uniform")

        basket_button = FilledButton(button_frame,
                                     image_file="basket_icon.png",
                                     image_width=30,
                                     image_height=30,
                                     command=lambda: self.app.load_frame("BasketFrame"),
                                     border_width=0)
        basket_button.grid(row=0, column=0, sticky="EW")

        product_compare_button = FilledButton(button_frame,
                                              image_file="product_compare_icon.png",
                                              image_width=30,
                                              image_height=30,
                                              command=lambda: self.app.load_frame("ProductComparisonFrame"),
                                              border_width=0)
        product_compare_button.grid(row=0, column=1, sticky="EW")

        account_button = FilledButton(button_frame,
                                      command=lambda: self.app.expand_customer_sidebar(),
                                      image_file="account_icon.png",
                                      image_width=30,
                                      image_height=30,
                                      border_width=0)
        account_button.grid(row=0, column=2, sticky="EW")

    def change_title(self, new_title: str):
        """
        Change the title of the screen

        Parameters
        ----------
        new_title : str
            The new title for the screen
        """
        self.title_label.configure(text=new_title)


class StaffSidebar(Sidebar):
    """
    Custom sidebar that displays the different entity choices for staff stakeholders

    Parameters
    ----------
    parent : any
        The parent widget in which the sidebar is contained

    app : any
        The main window of the application which acts as a controller for the application
    """
    def __init__(self, parent, app):
        super().__init__(parent,
                         emerge_from="left",
                         width=0.25,
                         animation_type="glide",
                         fg_color=colours.get_primary_colour())
        self.grid_propagate(False)
        self.parent = parent
        self.app = app
        self.grid_rowconfigure(0, weight=1, uniform="uniform")
        self.grid_rowconfigure(1, weight=6, uniform="uniform")
        self.grid_rowconfigure(2, weight=1, uniform="uniform")
        self.grid_columnconfigure(0, weight=1, uniform="uniform")

        # Widgets
        topbar = Frame(self, fg_color=colours.get_primary_colour())
        topbar.grid(row=0, column=0, sticky="NSEW")
        topbar.grid_rowconfigure(0, weight=1)
        topbar.grid_columnconfigure(0, weight=1, uniform="uniform")
        topbar.grid_columnconfigure(1, weight=2, uniform="uniform")

        back_button = FilledButton(topbar,
                                   command=lambda: self.collapse(increment=10),
                                   image_file="back_icon.png",
                                   image_width=20,
                                   image_height=20,
                                   border_width=0)
        back_button.grid(row=0, column=0)

        logo = Label(topbar,
                     image_file="turtle_tennis_icon_ICON_AND_TEXT.png",
                     image_width=75,
                     image_height=75,
                     fg_color=colours.get_primary_colour())
        logo.grid(row=0, column=1, sticky="NSEW")

        # Define the different entities available
        self.entity_info = {"Customer": {"text": "Customers", "image_file": "account_icon.png"},
                            "Staff": {"text": "Staff", "image_file": "badge_icon.png"},
                            "Orders": {"text": "Orders", "image_file": "delivery_icon.png"},
                            "Payment_Card": {"text": "Payment Cards", "image_file": "card_icon.png"},
                            "Product": {"text": "Products", "image_file": "racket_icon.png"},
                            "Ratings": {"text": "Ratings", "image_file": "star_icon.png"},
                            "Supplier": {"text": "Suppliers", "image_file": "forklift_icon.png"}}

        self.button_frame = Frame(self, fg_color=colours.get_primary_colour())
        self.button_frame.grid(row=1, column=0, columnspan=2, sticky="NSEW")
        for count, entity in enumerate(self.entity_info):
            self.button_frame.grid_rowconfigure(count, weight=1, uniform="uniform")
        self.button_frame.grid_columnconfigure(0, weight=1)

        for count, (key, value) in enumerate(list(self.entity_info.items())):
            # Set the first entity (button) as the active one
            if count == 0:
                entity_button = BlankButton(self.button_frame,
                                            text=value.get("text"),
                                            image_file=value.get("image_file"),
                                            image_width=20,
                                            image_height=20,
                                            font=("Inter Regular", 16),
                                            compound="top",
                                            bg_color=colours.get_primary_colour(),
                                            corner_radius=10)
            else:
                entity_button = FilledButton(self.button_frame,
                                             text=value.get("text"),
                                             image_file=value.get("image_file"),
                                             image_width=20,
                                             image_height=20,
                                             font=("Inter Regular", 16),
                                             compound="top",
                                             bg_color=colours.get_primary_colour(),
                                             border_width=0,
                                             corner_radius=10)
            entity_button.grid(row=count, column=0, sticky="E")
            value["button"] = entity_button
            entity_button.configure(command=lambda k=key: self.change_table(k))

        self.active_table = list(self.entity_info.keys())[0]

        logout_button = FilledButton(self,
                                     command=lambda: app.logout(),
                                     font=("Inter Regular", 16),
                                     text="Logout")
        logout_button.grid(row=2, column=0)

    def get_current_table(self):
        """
        Get the name of the database table currently in focus

        Returns
        -------
        str
            The name of the active table
        """
        return self.active_table

    def get_entity_name(self):
        """
        Get the name of the entity currently in focus

        Returns
        -------
        str
            The name of the active entity
        """
        return self.entity_info.get(self.get_current_table()).get("text")

    def change_table(self, table_name: str, trigger_command: bool = True):
        """
        Change the entity / table in focus

        Parameters
        ----------
        table_name : str
            The name of the new table

        trigger_command : bool
            Whether the database management screen should update to reflect this change
        """
        # If the user can access the table
        if backend.check_access(access_level=self.app.get_current_user().get_access_level(),
                                table_name=table_name,
                                mode="S"):
            self.active_table = table_name
            for key, values in self.entity_info.items():
                button = values.get("button")
                # Turn only the active entity button white (to signify it is active)
                if table_name == key:
                    button.configure(fg_color=colours.get_bg_colour())
                else:
                    button.configure(fg_color=colours.get_primary_colour())
            if trigger_command:
                self.collapse(increment=10)
                self.app.frames["DatabaseManagementFrame"].change_table(self.active_table)
        else:
            mbox.showerror("Error!", "You do not have access to view this entity!")


class Basket(Frame):
    """
    Custom widget which displays the user's basket

    Parameters
    ----------
    parent : any
        The parent widget in which the basket is contained

    view_only : bool
        Whether items in the basket can be altered.
        The value will be True if it cannot be altered and False if it can be
    """
    def __init__(self, parent: any, app: any, view_only: bool = False):
        super().__init__(parent,
                         border_width=1)
        self.controller = parent
        self.app = app
        self.basket = None
        self.view_only = view_only
        product_row_width = 3
        self.grid_columnconfigure(0, weight=2, uniform="uniform")
        self.grid_columnconfigure(1, weight=2, uniform="uniform")
        self.grid_columnconfigure(2, weight=3, uniform="uniform")
        self.grid_columnconfigure(3, weight=2, uniform="uniform")
        self.grid_columnconfigure(4, weight=3, uniform="uniform")
        self.grid_columnconfigure(5, weight=2, uniform="uniform")

        max_products = 5
        self.grid_rowconfigure(0, weight=3, uniform="uniform")
        for count in range(max_products):
            self.grid_rowconfigure(count+1,
                                   weight=product_row_width,
                                   uniform="uniform")
        self.cost_label = None

    def refresh(self, overwrite_with=None):
        """
        Update the basket to its most recent state
        """
        for widget in self.winfo_children():
            widget.destroy()

        if self.view_only:
            headings = ["ID", "Image", "Name", "Unit Cost", "Quantity", "Total Cost"]
        else:
            headings = ["", "Image", "Name", "Unit Cost", "Quantity", "Total Cost"]

        heading_frame = Frame(self,
                              fg_color=colours.get_primary_colour(),
                              bg_color="White",
                              border_width=1)
        heading_frame.grid(row=0, column=0, columnspan=6, sticky="NSEW")
        heading_frame.grid_rowconfigure(0, weight=1)
        heading_frame.grid_columnconfigure(0, weight=2, uniform="uniform")
        heading_frame.grid_columnconfigure(1, weight=2, uniform="uniform")
        heading_frame.grid_columnconfigure(2, weight=3, uniform="uniform")
        heading_frame.grid_columnconfigure(3, weight=2, uniform="uniform")
        heading_frame.grid_columnconfigure(4, weight=3, uniform="uniform")
        heading_frame.grid_columnconfigure(5, weight=2, uniform="uniform")

        # Display basket headings
        for count, heading in enumerate(headings):
            heading_label = Label(heading_frame,
                                  text=heading,
                                  fg_color=colours.get_primary_colour(),
                                  max_line_length=8,
                                  justify="left")
            # Define case for ID where heading is on the left rather than center
            if heading != "ID":
                heading_label.grid(row=0, column=count, padx=1, pady=2, sticky="W")
            else:
                heading_label.grid(row=0, column=count, padx=1, pady=2)

        if overwrite_with:
            products_bought = overwrite_with
        else:
            self.basket = self.app.get_current_user().get_basket()
            products_bought = self.basket.get_products()

        for count, product in enumerate(products_bought):
            # Display products in basket
            row = count + 1
            image_label = Label(self,
                                image_file=product.get("image_file"),
                                image_width=70,
                                image_height=70)
            image_label.grid(row=row, column=1, sticky="W")

            name_label = Label(self,
                               text=product.get("name"),
                               max_line_length=12,
                               justify="left",
                               anchor="w")
            name_label.grid(row=row, column=2, sticky="W")

            price = product.get("sale_price")
            price_label = Label(self,
                                text=f"£{price:.2f}")
            price_label.grid(row=row, column=3, sticky="W")

            quantity = product.get("quantity")
            self.cost_label = Label(self,
                                    text=f"£{(price * quantity):.2f}")
            self.cost_label.grid(row=row, column=5, padx=(0, 5), sticky="W")

            if not self.view_only:
                # Only allow the user to alter quantities and delete items if the basket can be altered
                if product.get("current_stock") < 10:
                    maximum = product.get("current_stock")
                else:
                    maximum = 10
                quantity_tracker = Counter(self,
                                           style="+-",
                                           minimum=1,
                                           maximum=maximum,
                                           width=40)
                quantity_tracker.grid(row=row, column=4, sticky="W")
                quantity_tracker.set_count(quantity)
                quantity_tracker.set_change_action(lambda arg,
                                                   p=product: self.update_quantity(arg, p))

                delete_button = BlankButton(self,
                                            image_file="bin_icon.png",
                                            image_width=30,
                                            image_height=30,
                                            command=lambda p=product: self.controller.refresh_basket_and_costs(
                                                    bin_product=p),
                                            width=50)
                delete_button.grid(row=row, column=0)
            else:
                quantity_label = Label(self,
                                       text=product.get("quantity"),
                                       fg_color="White")
                quantity_label.grid(row=row, column=4, sticky="W")

                id_label = Label(self,
                                 text=product.get("product_id"))
                id_label.grid(row=row, column=0)

    def update_quantity(self, new_quantity: int, product: dict):
        """
        Method that updates the quantity of an item in a basket and adjusts cost outputs accordingly

        Parameters
        ----------
        new_quantity : int
            The updated quantity for the item

        product : dict
            The product whose quantity is to be updated
        """
        price = product.get("sale_price")

        # Update quantity value in basket object
        product["quantity"] = new_quantity
        self.basket.update_quantity(product.get("product_id"),
                                    new_quantity)

        # Adjust cost outputs
        new_cost = price * new_quantity
        self.cost_label.configure(text=f"£{new_cost:.2f}")
        self.controller.refresh_cost_frame()


class CostsFrame(Frame):
    """
    Custom widget for displaying the cost of a basket

    Parameters
    ----------
    parent : any
        The parent widget in which the basket is contained

    continue_message : str
        The text displayed in the button that leads to the next screen

    back_message : str
        The text displayed in the button that goes back to the previous screen

    continue_action : callable
        The action that leads to the next screen

    back_action : callable
        The action that leads to the previous screen
    """
    def __init__(self,
                 parent: any,
                 continue_message: str = "Checkout",
                 back_message: str = "Continue shopping",
                 continue_action: callable = None,
                 back_action: callable = None):
        basket_bg = colours.get_bg_colour()
        super().__init__(parent,
                         fg_color=basket_bg,
                         border_width=1)
        self.basket = None
        self.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.grid_columnconfigure(1, weight=1, uniform="uniform")

        continue_button = FilledButton(self,
                                       text=continue_message,
                                       command=continue_action,
                                       bg_color="White")
        continue_button.grid(row=0, column=0, padx=5, pady=(10, 5), columnspan=2, sticky="EW")

        back_button = FilledButton(self,
                                   text=back_message,
                                   command=back_action,
                                   bg_color="White")
        back_button.grid(row=1, column=0, padx=5, pady=(5, 10), columnspan=2, sticky="EW")

        # Set initial cost values to 0
        subtotal_title = Label(self,
                               fg_color=basket_bg,
                               text="Subtotal:",
                               anchor="w")
        subtotal_title.grid(row=2, column=0, padx=(10, 0), sticky="W")

        self.subtotal_label = Label(self,
                                    fg_color=basket_bg,
                                    text=f"£0",
                                    anchor="e")
        self.subtotal_label.grid(row=2, column=1, padx=(0, 10), sticky="E")

        delivery_title = Label(self,
                               fg_color=basket_bg,
                               text="Delivery:",
                               anchor="w")
        delivery_title.grid(row=3, column=0, padx=(10, 0), sticky="W")

        self.delivery_label = Label(self,
                                    fg_color=basket_bg,
                                    text=f"£0",
                                    anchor="e")
        self.delivery_label.grid(row=3, column=1, padx=(0, 10), sticky="E")

        separator = ttk.Separator(self,
                                  orient="horizontal")
        sep_style = ttk.Style(separator)
        sep_style.configure('TSeparator', background="Black")
        separator.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="EW")

        total_title = Label(self,
                            fg_color=basket_bg,
                            text="Total:",
                            anchor="w")
        total_title.grid(row=5, column=0, padx=(10, 5), pady=(0, 10), sticky="W")
        self.total_label = Label(self,
                                 fg_color=basket_bg,
                                 text=f"£0",
                                 anchor="e")
        self.total_label.grid(row=5, column=1, padx=(0, 10), pady=(0, 10), sticky="E")

    def link_basket(self, basket: object):
        """
        Link a basket object to the display

        Parameters
        ----------
        basket : object
            The basket data structure
        """
        self.basket = basket

    def update_totals(self):
        """
        Update the total costs to their most recent state
        """
        self.subtotal_label.configure(text=f"£{self.basket.get_subtotal():.2f}")
        self.delivery_label.configure(text=f"£{self.basket.get_delivery_cost():.2f}")
        self.total_label.configure(text=f"£{self.basket.get_total():.2f}")


class Searchbar(Frame):
    """
    Custom search bar widget

    Parameters
    ----------
    parent : any
        The parent widget in which the search bar is contained

    search_command : callable
        The command that should be called when the search button is clicked
    """
    def __init__(self,
                 parent: any,
                 search_command: callable = None):
        super().__init__(parent, border_width=1, bg_color=colours.get_primary_colour())
        self.search_command = search_command
        self.grid_columnconfigure(0, weight=7, uniform="uniform")
        self.grid_columnconfigure(1, weight=1, uniform="uniform")

        # Widgets
        # Search entry widget for input
        self.search_entry = Entry(self,
                                  corner_radius=0,
                                  border_width=0,
                                  hideable=False,
                                  validated=False,
                                  placeholder_text="Search for a name, supplier or ID")
        self.search_entry.grid(row=0, column=0, padx=2, pady=2, sticky="NSEW")

        search_button = BlankButton(self,
                                    command=self.call_search_command,
                                    image_file="search_icon.png",
                                    image_width=30,
                                    image_height=30,
                                    hover=False,
                                    corner_radius=0)
        search_button.grid(row=0, column=1, padx=2, pady=2, sticky="NSEW")

    def call_search_command(self):
        """
        Call the search command with the search input entered
        """
        if self.search_command is not None:
            self.search_command()

    def reset_searchbar(self):
        """
        Reset the search bar to its default state
        """
        self.search_entry.clear()

    def set_search_command(self,
                           search_command: callable):
        """
        Set the search command that is activated when the search button is clicked

        Parameters
        ----------
        search_command : callable
            The command that should be called when the search button is clicked
        """
        self.search_command = search_command

    def get_current_search(self):
        """
        Get the search input

        Returns
        -------
        str
            The search input
        """
        return self.search_entry.get()


class Counter(Frame):
    """
    Custom counter widget

    Parameters
    ----------
    parent : any
        The parent widget in which the search bar is contained

    style : str
        The style of the counter buttons
        <> will display < for decrement and > for increment
        +- will display - for decrement and + for increment

    minimum : int
        The minimum value allowed for the counter

    maximum : int
        The maximum value allowed for the counter

    width : int
        The width of the counter
    """
    def __init__(self,
                 parent: any,
                 style: str = "<>",
                 minimum: int = 1,
                 maximum: int = None,
                 width: int = 80):
        super().__init__(parent)

        # Attributes
        self.count = minimum
        self.configure(fg_color="White")
        self.minimum = minimum
        self.maximum = maximum
        self.change_function = None

        if style == "<>":
            increase_text = ">"
            decrease_text = "<"
        else:
            increase_text = "+"
            decrease_text = "-"

        # Widgets
        self.decrease_button = ctk.CTkButton(self,
                                             command=lambda: self.decrement(),
                                             text=decrease_text,
                                             text_color="Black",
                                             fg_color="#BDBDBD",
                                             bg_color="White",
                                             width=25,
                                             height=25)
        self.decrease_button.grid(row=0, column=0)

        self.increase_button = ctk.CTkButton(self,
                                             command=lambda: self.increment(),
                                             text=increase_text,
                                             text_color="Black",
                                             fg_color="#BDBDBD",
                                             bg_color="White",
                                             width=25,
                                             height=25)
        self.increase_button.grid(row=0, column=2)

        self.count_label = Label(self,
                                 text="",
                                 fg_color="White",
                                 width=width)
        self.count_label.grid(row=0, column=1)

        self.reset()

    def reset(self):
        """
        Reset counter
        """
        self.set_count(self.minimum)

    def increment(self):
        """
        Increment counter by one
        """
        new_count = self.count+1
        self.set_count(new_count)
        if self.change_function:
            # Trigger command
            self.change_function(new_count)

    def decrement(self):
        """
        Decrement counter by one
        """
        new_count = self.count-1
        self.set_count(new_count)
        if self.change_function:
            # Trigger command with count passed through
            self.change_function(new_count)

    def set_change_action(self, new_func: callable):
        """
        Set command that will be triggered when the count changes

        Parameters
        ----------
        new_func : callable
            The command to be triggered
        """
        self.change_function = new_func

    def set_count(self, new_count: int):
        """
        Set the counter to a new value

        Parameters
        ----------
        new_count : int
            The new value for the counter
        """
        self.count = new_count
        self.count_label.configure(text=self.count)
        if self.minimum:
            # If the new value is at the counter's minimum
            if self.count < self.minimum+1:
                self.disable_decrement()
            else:
                self.enable_decrement()
        if self.maximum:
            # If the new value is at the counter's maximum
            if self.count == self.maximum:
                self.disable_increment()
            else:
                self.enable_increment()

    def get_count(self):
        """
        Get the counter value

        Returns
        -------
        int
            The value of the counter
        """
        return self.count

    def set_maximum(self, maximum: int):
        """
        Set the maximum of the counter

        Parameters
        ----------
        maximum : int
            The maximum value the counter can be
        """
        self.maximum = maximum

    def disable_decrement(self):
        """
        Disable the decrement button
        """
        self.decrease_button.configure(state="disabled")

    def enable_decrement(self):
        """
        Enable the decrement button
        """
        self.decrease_button.configure(state="normal")

    def disable_increment(self):
        """
        Disable the increment button
        """
        self.increase_button.configure(state="disabled")

    def enable_increment(self):
        """
        Enable the increment button
        """
        self.increase_button.configure(state="normal")


class PageTracker(Counter):
    """
    Custom counter for tracking pages in a slideshow

    Parameters
    ----------
    parent : any
        The parent widget in which the page tracker is contained
    """
    def __init__(self, parent: any):
        super().__init__(parent, minimum=1)
        self.parent = parent
        self.slideshow = None
        self.previous_page = None
        self.next_page = None

    def increment(self):
        """
        Increment the page tracker by one
        """
        if not self.slideshow.get_is_active():
            new_count = self.count + 1
            self.set_count(new_count)
            # Load the next slide in the slideshow
            self.slideshow.slide_left(percentage_to_move=0.02, tail_frame=self.next_page)
            self.parent.update_adjacent_pages()

    def decrement(self):
        """
        Decrement the page tracker by one
        """
        if not self.slideshow.get_is_active():
            new_count = self.count - 1
            self.set_count(new_count)
            # Load the previous slide in the slideshow
            self.slideshow.slide_right(percentage_to_move=0.02, tail_frame=self.previous_page)
            self.parent.update_adjacent_pages()

    def set_next_page(self, next_page: any):
        """
        Set the next page of the slideshow

        Parameters
        ----------
        next_page : CTkFrame
            The next page of the slideshow
        """
        self.next_page = next_page

    def set_previous_page(self, previous_page: any):
        """
        Set the previous page of the slideshow

        Parameters
        ----------
        previous_page : CTkFrame
            The previous page of the slideshow
        """
        self.previous_page = previous_page

    def link_slideshow(self, slideshow: any):
        """
        Link a slideshow widget to the page tracker

        Parameters
        ----------
        slideshow : cWidget.Slideshow
            The slideshow to be linked
        """
        self.slideshow = slideshow


class Slideshow(tk.Canvas):
    """
    Custom slideshow widget which slides frames onto and off screen

    Parameters
    ----------
    parent : any
        The parent widget in which the slideshow is contained

    fg_color : str
        The foreground colour for the slideshow

    width : int
        The width of the slideshow.
        If no value is specified, then the slideshow will expand to fit its parent's width

    height : int
        The height of the slideshow
        If no value is specified, then the slideshow will expand to fit its parent's height
    """
    def __init__(self,
                 parent: any,
                 fg_color: str = "White",
                 width: int = None,
                 height: int = None):
        if width is None:
            # Expand to fit parent's width
            self.width = parent.winfo_width()
        else:
            self.width = width
        if height is None:
            # Expand to fit parent's height
            self.height = parent.winfo_height()
        else:
            self.height = height
        super().__init__(parent,
                         width=self.width,
                         height=self.height,
                         bg=fg_color,
                         borderwidth=0,
                         highlightthickness=0)
        self.fg_color = fg_color
        self.current_id = None
        self.tail_id = False
        self.is_active = False
        self.stopping_x = 0

    def get_is_active(self):
        """
        Gets whether the slideshow is currently actively animating

        Returns
        -------
        bool
            Whether the slideshow animation is active.
            The value will be True if the slideshow is active and False if not
        """
        return self.is_active

    def set_current_frame(self,
                          frame: any = None):
        """
        Set the frame that should be currently on screen

        Parameters
        ----------
        frame : CTkFrame
            The frame widget which should be displayed in the slideshow
        """
        if self.current_id:
            self.delete(self.current_id)
        if not frame:
            frame = Frame(self, fg_color=self.fg_color)
        self.current_id = self.create_window(0,
                                             0,
                                             anchor="nw",
                                             width=self.width,
                                             height=self.height,
                                             window=frame)

    def _move_left(self, percentage_to_move: float):
        """
        Moves the slideshow left by a percentage of the width

        Parameters
        ----------
        percentage_to_move : float
            The percentage of the width that the slideshow should move
        """
        increment = percentage_to_move * self.width
        # If currently displayed frame (previous) is still on-screen
        if self._current_get_x() > self.stopping_x:
            # If moving the currently displayed frame by the increment would place it further off-screen then needed
            if self._current_get_x() - increment < self.stopping_x:
                # Move it so that it is just barely off-screen
                movement_amount = self.stopping_x - self._current_get_x()
            else:
                movement_amount = -increment
            # Move the currently displayed (previous) frame and the tailing (next) frame by the same amount
            self.move(self.current_id, movement_amount, 0)
            self.move(self.tail_id, movement_amount, 0)
        else:
            self.stop()

    def _move_right(self, percentage_to_move: float):
        """
        Moves the slideshow right by a percentage of the width

        Parameters
        ----------
        percentage_to_move : float
            The percentage of the width that the slideshow should move
        """
        increment = percentage_to_move * self.width
        # If currently displayed frame (previous) is still on-screen
        if self._current_get_x() < self.stopping_x:
            # If moving the currently displayed frame by the increment would place it further off-screen then needed
            if self._current_get_x() + increment > self.stopping_x:
                movement_amount = self.stopping_x - self._current_get_x()
            else:
                movement_amount = increment
            # Move the currently displayed (previous) frame and the tailing (next) frame by the same amount
            self.move(self.current_id, movement_amount, 0)
            self.move(self.tail_id, movement_amount, 0)
        else:
            self.stop()

    def slide_left(self,
                   tail_frame: any = None,
                   percentage_to_move: float = 0.01,
                   interval: int = 10):
        """
        Slide the currently displayed frame left and slide the next frame on-screen from the right

        Parameters
        ----------
        tail_frame : CTkFrame
            The frame which is to be slided on-screen

        percentage_to_move : float
            The percentage of the slideshow each step should move.
            Defaults to 0.01 (1%)

        interval : int
            The number of ms between each step
        """
        if not self.is_active:
            if tail_frame:
                # Stop one frame's distance off-screen to the left
                self.stopping_x = -self.width
                self.tail_id = self.create_window(self.width,
                                                  0,
                                                  anchor="nw",
                                                  width=self.width,
                                                  height=self.height,
                                                  window=tail_frame)
                self.is_active = True
                self._animation_loop(percentage_to_move, interval, "left")

    def slide_right(self,
                    tail_frame: any = None,
                    percentage_to_move: float = 0.01,
                    interval: int = 10):
        """
        Slide the currently displayed frame right and slide the next frame on-screen from the left

        Parameters
        ----------
        tail_frame : CTkFrame
            The frame which is to be slided on-screen

        percentage_to_move : float
            The percentage of the slideshow each step should move.
            Defaults to 0.01 (1%)

        interval : int
            The number of ms between each step
        """
        if not self.is_active:
            if tail_frame:
                # Stop one frame's distance off-screen to the right
                self.stopping_x = self.width
                self.tail_id = self.create_window(-self.width,
                                                  0,
                                                  anchor="nw",
                                                  width=self.width,
                                                  height=self.height,
                                                  window=tail_frame)
                self.is_active = True
                self._animation_loop(percentage_to_move, interval, "right")

    def stop(self):
        """
        Stop the slideshow animation
        """
        if self.loop_id is not None:
            self.delete(self.current_id)
            # Set the frame most recently slided on-screen to be the currently displayed frame
            frame = self.itemcget(self.tail_id, option="window")
            self.set_current_frame(frame)
            self.delete(self.tail_id)
            self.after_cancel(self.loop_id)
            self.is_active = False

    def _animation_loop(self,
                        percentage_to_move: float,
                        interval: int,
                        direction: str):
        """
        Keep looping until the sliding animation is complete

        Parameters
        ----------
        percentage_to_move : float
            The percentage each frame should move

        interval : int
            The number of ms between each frame

        direction : str
            The direction of sliding, either 'left' or 'right'
        """
        if self.is_active:
            if direction == "left":
                self._move_left(percentage_to_move)
            else:
                self._move_right(percentage_to_move)
            self.loop_id = self.after(interval, self._animation_loop, percentage_to_move, interval, direction)

    def _current_get_x(self):
        """
        Get the x coordinate of the sliding frame

        Returns
        -------
        float
            The x coordinate
        """
        return self.coords(self.current_id)[0]


class ProductView(Frame):
    """
    Custom frame for holding the product slideshow, page tracker and items found label found in the Browsing Frame

    Parameters
    ----------
    parent : any
        The parent widget in which the back button is contained

    app : any
        The main window of the application which acts as a controller for the application
    """
    def __init__(self,
                 parent: any,
                 app: any):
        super().__init__(parent)
        self.grid_rowconfigure(0, weight=6, uniform="uniform")
        self.grid_rowconfigure(1, weight=1, uniform="uniform")
        self.grid_columnconfigure(0, weight=1, uniform="uniform")
        self.grid_columnconfigure(1, weight=1, uniform="uniform")
        self.grid_columnconfigure(2, weight=1, uniform="uniform")

        # Define attributes
        self.app = app
        self.products = []
        self.paged_products = []
        self.current_compare_buttons = []

        # Define slideshow and encompassing frame
        self.slideshow_frame = Frame(self)
        self.slideshow_frame.grid(row=0, column=0, columnspan=3, sticky="NSEW")
        self.slideshow_frame.grid_rowconfigure(0, weight=1)
        self.slideshow_frame.grid_columnconfigure(0, weight=1)
        self.slideshow = None

        # Define frame that displays message if no products are found
        self.info_frame = Frame(self)

        self.items_found_label = Label(self,
                                       text=f"Items found: {len(self.products)}",
                                       fg_color="White")
        self.items_found_label.grid(row=1, column=1)

        # Define page tracker
        self.page_tracker = PageTracker(self)
        self.page_tracker.grid(row=1, column=2)
        self.page_tracker.link_slideshow(self.slideshow)

    def refresh_pockets(self, products: list):
        """
        Refresh the products displayed on screen

        Parameters
        ----------
        products : list
            The products to be displayed
        """
        self.current_compare_buttons = []
        self.products = products

        # Lifted from GeekForGeeks: https://www.geeksforgeeks.org/break-list-chunks-size-n-python/
        n = 3
        self.paged_products = [self.products[i * n:(i + 1) * n] for i in range((len(self.products) + n - 1) // n)]
        # End of copied snippet

        self.slideshow = Slideshow(self.slideshow_frame)
        self.slideshow.grid(row=0, column=0, sticky="NSEW")
        self.page_tracker.link_slideshow(self.slideshow)

        # Reset page tracker
        self.page_tracker.set_count(1)
        self.page_tracker.set_maximum(len(self.paged_products))

        # If only one page of products (3 per page) can exist
        if len(self.products) <= 3:
            self.page_tracker.disable_increment()
        else:
            self.page_tracker.enable_increment()

        if self.paged_products:
            # Hide error message
            self.info_frame.grid_forget()
            self.items_found_label.configure(text=f"Items found: {len(self.products)}")
            current_frame = self.create_page(page_num=1)
            self.slideshow.set_current_frame(current_frame)
            self.update_adjacent_pages()
        else:
            self.items_found_label.configure(text="Items found: 0")
            self.info_frame.grid(row=0, column=0, rowspan=3, columnspan=3)
            self.info_frame.grid_rowconfigure(0, weight=1, uniform="uniform")
            self.info_frame.grid_rowconfigure(1, weight=1, uniform="uniform")
            self.info_frame.grid_columnconfigure(0, weight=1)
            no_items_found = Label(self.info_frame,
                                   fg_color="White",
                                   text="No products found.")
            no_items_found.grid(row=0, column=0, sticky="S")
            solution_label = Label(self.info_frame,
                                   fg_color="White",
                                   text="Expecting results? Check for any spelling errors in your search!",
                                   justify="center")
            solution_label.grid(row=1, column=0, sticky="N")

    def create_page(self,
                    page_num: int):
        """
        Create frame of 1-3 products for display within the product slideshow

        Parameters
        ----------
        page_num : int
            The page number of the frame being created

        Returns
        -------
        CTkFrame
            The frame of 1-3 products
        """
        three_products_frame = Frame(self.slideshow)
        three_products_frame.grid_rowconfigure(0, weight=1)
        three_products_frame.grid_columnconfigure(0, weight=1, uniform="uniform")
        three_products_frame.grid_columnconfigure(1, weight=1, uniform="uniform")
        three_products_frame.grid_columnconfigure(2, weight=1, uniform="uniform")
        for count, product in enumerate(self.paged_products[page_num-1]):
            # Display product information for all products on the page
            product_bg_colour = "White"
            product_pocket = Frame(three_products_frame, border_width=1)
            product_pocket.grid_rowconfigure(0, weight=8, uniform="uniform")
            product_pocket.grid_rowconfigure(1, weight=2, uniform="uniform")
            product_pocket.grid_rowconfigure(2, weight=2, uniform="uniform")
            product_pocket.grid_rowconfigure(3, weight=2, uniform="uniform")
            product_pocket.grid_rowconfigure(4, weight=2, uniform="uniform")
            product_pocket.grid_rowconfigure(5, weight=2, uniform="uniform")
            product_pocket.grid_rowconfigure(6, weight=4, uniform="uniform")
            product_pocket.grid_columnconfigure(0, weight=3, uniform="uniform")
            product_pocket.grid_columnconfigure(1, weight=2, uniform="uniform")

            product_image_label = Label(product_pocket,
                                        image_file=product.get("image_file"),
                                        image_width=110,
                                        image_height=130)
            product_image_label.configure(fg_color=product_bg_colour)
            product_image_label.grid(row=0, column=0, pady=5)

            add_to_compare = ProductCompareButton(product_pocket,
                                                  app=self.app,
                                                  product=product)
            add_to_compare.configure(command=lambda p=product, b=add_to_compare: self.toggle_compare_icon(p, b))
            add_to_compare.grid(row=0, column=1, pady=5, sticky="N")
            self.current_compare_buttons.append(add_to_compare)

            supplier_label = Label(product_pocket,
                                   text=product.get("company_name"),
                                   font=("Inter Regular", 16),
                                   fg_color=product_bg_colour)
            supplier_label.grid(row=1, column=0, columnspan=2, padx=(10, 0), sticky="W")

            product_name_label = Label(product_pocket,
                                       text=product.get("name"),
                                       font=("Poppins Regular", 20),
                                       fg_color=product_bg_colour)
            product_name_label.grid(row=2, column=0, columnspan=2, padx=(10, 0), sticky="W")

            sale_price = product.get("sale_price")
            product_price_label = Label(product_pocket,
                                        text=f"£{sale_price:.2f}",
                                        font=("Poppins Regular", 20),
                                        fg_color=product_bg_colour)
            product_price_label.grid(row=3, column=0, columnspan=2, padx=(10, 0), sticky="W")

            product_rating_label = Label(product_pocket,
                                         image_file="star_icon.png",
                                         image_height=15,
                                         image_width=15,
                                         text=product.get("average_rating"),
                                         font=("Inter Regular", 16),
                                         fg_color=product_bg_colour)
            product_rating_label.grid(row=4, column=0, columnspan=2, padx=(10, 0), sticky="SW")

            current_stock = product.get("current_stock")
            current_stock_label = Label(product_pocket,
                                        text=f"Available: {current_stock}",
                                        font=("Inter Regular", 16),
                                        fg_color=product_bg_colour)
            current_stock_label.grid(row=5, column=0, columnspan=2, padx=(10, 0), sticky="SW")

            view_button = FilledButton(product_pocket,
                                       height=25,
                                       text="View",
                                       command=lambda p=product: self.app.load_frame("ProductFrame", product_details=p),
                                       corner_radius=5)
            view_button.grid(row=6, column=0, columnspan=2)

            product_pocket.grid(row=0,
                                column=count,
                                padx=10,
                                sticky="NSEW")

        return three_products_frame

    def update_adjacent_pages(self):
        """
        Set the next and previous pages of orders (if they exist)
        """
        # If the user has not reached the last page
        if len(self.paged_products) > self.page_tracker.get_count():
            self.page_tracker.set_next_page(self.create_page(self.page_tracker.get_count()+1))
        else:
            self.page_tracker.set_next_page(None)

        # If the user is not on the first page
        if self.page_tracker.get_count() != 1:
            self.page_tracker.set_previous_page(self.create_page(self.page_tracker.get_count()-1))
        else:
            self.page_tracker.set_previous_page(None)

    def toggle_compare_icon(self, product: dict, add_to_compare_button: any):
        """
        Function called when the compare icon is triggered

        Parameters
        ----------
        product : dict
            The product linked to the compare icon

        add_to_compare_button : ctk.CTkButton
            The compare icon button
        """
        bucket = self.app.get_current_user().get_compare_bucket()
        error_code = bucket.add_product(product)
        # If product already in bucket
        if error_code == 1:
            # Switch button off
            add_to_compare_button.switch_state()
            # Delete product
            _ = bucket.delete_product(product.get("product_id"))
        # If basket has two OTHER products
        elif error_code == 2:
            # Warn user of consequences
            confirm = mbox.askyesno("Warning!", "Adding this product will delete the most recent product. Confirm?")
            if confirm:
                deleted_product = bucket.delete_product()
                # Switch off that product's compare icon
                for button in self.current_compare_buttons:
                    # If product linked to the button is the product to delete
                    if button.get_product() == deleted_product:
                        button.switch_state()
                add_to_compare_button.switch_state()
                _ = bucket.add_product(product)
        # If product WAS successfully added
        else:
            # Switch button on
            add_to_compare_button.switch_state()
            mbox.showinfo("Success!", "Item added successfully!")


class RatingBar(Frame):
    """
    Custom widget that acts as a star-based rating system

    Parameters
    ----------
    parent : any
        The parent widget in which the rating widget is contained

    app : any
        The main window of the application which acts as a controller for the application

    product_id : int
        The product id of the product that the ratings apply to
    """
    def __init__(self, parent: any, app: any, product_id: int):
        super().__init__(parent,
                         height=40)
        # Attributes
        self.app = app
        self.linked_product_id = product_id
        self.customer_id = self.app.get_current_user().get_personal_id()

        # Metadata
        self.grid_rowconfigure(0, weight=1, uniform="uniform")
        self.grid_rowconfigure(1, weight=1, uniform="uniform")
        self.grid_rowconfigure(2, weight=1, uniform="uniform")

        # Widgets
        self.score_label = Label(self,
                                 text="Average rating: 0.0 (0)",
                                 fg_color="White")
        self.score_label.grid(row=0, column=0, columnspan=5, sticky="W")

        your_rating_title = Label(self,
                                  text="Your rating:",
                                  fg_color="White")
        your_rating_title.grid(row=1, column=0, columnspan=5, sticky="W")

        self.star_buttons = []

        self.delete_button = BlankButton(self,
                                         command=lambda: self.delete_rating(),
                                         image_file="close_icon.png",
                                         image_width=10,
                                         image_height=10,
                                         width=15)
        # Display 5 star icons
        for count in range(5):
            star_button = StarButton(self,
                                     command=lambda score=count+1: self.update_rating(score),
                                     score=count+1)
            star_button.grid(row=2, column=count, sticky="W")
            self.star_buttons.append(star_button)

        self.refresh()

    def display_rating(self, user_score):
        """
        Displays the current rating

        Parameters
        ----------
        user_score : int
            The user's current rating
        """
        # Switch on all buttons left and including the current score
        for count in range(user_score):
            self.star_buttons[count].switch_on()
        # Turn off the remaining buttons
        for count in range(5 - user_score):
            self.star_buttons[-1-count].switch_off()
        if user_score > 0:
            self.delete_button.grid(row=2, column=5, sticky="W")
        else:
            self.delete_button.grid_forget()
        current_score = crud.search_table("ecommerce",
                                          "Product",
                                          "*",
                                          f"product_id = '{self.linked_product_id}'")[0].get("average_rating")
        ratings_count = backend.count_ratings(self.linked_product_id)
        self.score_label.configure(text=f"Average rating: {current_score} ({ratings_count})")

    def update_rating(self, new_score):
        """
        Updates the user's rating with a new score

        Parameters
        ----------
        new_score : int
            The new score
        """
        existing_rating = crud.search_table("ecommerce",
                                            "Ratings",
                                            ["score"],
                                            f"customer_id = '{self.customer_id}' AND product_id = '{self.linked_product_id}'")
        date = datetime.today().strftime('%Y-%m-%d')
        if existing_rating:
            crud.update_record("ecommerce",
                               "Ratings",
                               {"score": new_score,
                                "date": date},
                               f"customer_id = '{self.customer_id}' AND product_id = '{self.linked_product_id}'")
        # If no record exists, add a new one
        else:
            crud.add_record("ecommerce",
                            "Ratings",
                            {"score": new_score,
                             "date": date,
                             "customer_id": self.customer_id,
                             "product_id": self.linked_product_id})
        backend.update_product_rating(self.linked_product_id)
        self.display_rating(new_score)

    def delete_rating(self):
        crud.delete_record("ecommerce",
                           "Ratings",
                           f"customer_id = '{self.customer_id}' AND product_id = '{self.linked_product_id}'")
        backend.update_product_rating(self.linked_product_id)
        # Display a user rating of 0 i.e. N/A
        self.display_rating(0)

    def refresh(self):
        """
        Refresh the rating bar
        """
        existing_rating = crud.search_table("ecommerce",
                                            "Ratings",
                                            ["score"],
                                            f"customer_id = '{self.customer_id}' AND product_id = '{self.linked_product_id}'")
        if existing_rating:
            self.display_rating(existing_rating[0].get("score"))
        else:
            # Display a user rating of 0 i.e. N/A
            self.display_rating(0)
