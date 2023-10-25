"""Extra bits & helpers for data_colors and ColorFactory."""

from PIL import Image, ImageDraw
from data_colors import ColorFactory


def _visualize1d(factory, image_size: int, orientation:str = "horizontal"):
    """Create a bar image for 1D data, optionally vertical."""
    # Define the image size
    if orientation == "horizontal":
        vertical = False
    elif orientation == "vertical":
        vertical = True
    else:
        raise ValueError("orientation must be vertical or horizontal")
    extents = (20, image_size) if vertical else (image_size,20)

    # Create a new image with a white background
    image = Image.new("RGB", extents, "white")
    draw = ImageDraw.Draw(image)

    # Get the min and max values for x from ColorFactory's dimensions
    dmin = factory.dimensions[0].min
    dmax = factory.dimensions[0].max
    # Calculate the step size for x
    step = (dmax - dmin) / (image_size - 1)
    if vertical:
        for i in range(image_size):
            x = dmax-i*step
            draw.line([(0, i), (extents[1], i)], factory.get_color(x))
    else:
        for i in range(image_size):
            x = dmin+i*step
            draw.line([(i, 0), (i, extents[1])], factory.get_color(x))

    return image

def _visualize2d(factory, image_size: int) -> Image:
    """Make a 400x400 image of 2d data."""
    # Define the image size and canvas size
    extents = (image_size, image_size)
    canvas_size = (image_size, image_size)

    # Create a new image with a white background
    image = Image.new("RGB", canvas_size, "white")

    # Get the min and max values for x and y from ColorFactory's dimensions
    x_min = factory.dimensions[0].min
    x_max = factory.dimensions[0].max
    y_min = factory.dimensions[1].min
    y_max = factory.dimensions[1].max

    # Calculate the step size for x and y
    x_step = (x_max - x_min) / (extents[0] - 1)
    y_step = (y_max - y_min) / (extents[1] - 1)

    # Plot the values on the 400x400 canvas
    for i in range(extents[0]):
        for j in range(extents[1]):
            x = x_min + i * x_step
            y = (
                y_max - j * y_step
            )  # Inverted to match the image coordinates
            color = factory.get_color(x, y)
            image.putpixel((i, j), color)
    return image

def visualize(factory:ColorFactory,orientation:str="horizontal"):
    """Make a color-spectrum image to show the current config."""
    if not factory.ready:
        print("not ready")
        return
    if len(factory.dimensions) == 1:
        image = _visualize1d(factory,400,orientation)
    elif len(factory.dimensions) == 2:
        image = _visualize2d(factory,400)
    else:
        print(
            f"no visualization available for {len(factory.dimensions)}-D ColorFactory"
        )
        return

    filename = "tmp_plot.png"
    image.save(filename)
    print(f"Saved image as {filename}")


def testable_factory(obj_num: int = 0) -> ColorFactory:
    """Create a variety of ColorFactory objects, for testing & experimenting."""
    if obj_num == 0:
        cf = ColorFactory()
        d1 = cf.add_dimension()
        d1.add_config(-10, "blue")
        d1.add_config(5, "beige")
        d1.add_config(30, "red")
    elif obj_num == 1:
        cf = ColorFactory()
        d1 = cf.add_dimension()
        d1.add_config(-10, "blue")
        d1.add_config(5, "beige")
        d1.add_config(30, "red")
        d2 = cf.add_dimension()
        d2.add_config(0, "yellow")
        d2.add_config(100, "seagreen")
    else:
        print(f"no def for {obj_num}")
    cf.dump()
    return cf
