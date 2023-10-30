"""Extra bits & helpers for data_colors and MultiDimension."""

from PIL import Image, ImageDraw

from datacolors import MultiDimension

def visualize_dimension(
    dimension, image_size: tuple, orientation: str = "horizontal"
):
    """Create a bar image for one dimension of data, optionally vertical."""
    # Define the image size
    if orientation == "horizontal":
        vertical = False
        extents = image_size
    elif orientation == "vertical":
        vertical = True
        extents = (image_size[1],image_size[0])
    else:
        raise ValueError("orientation must be vertical or horizontal")


    # Create a new image with a white background
    image = Image.new("RGB", extents, "white")
    draw = ImageDraw.Draw(image)

    # Get the min and max values for x from MultiDimension's dimensions
    dmin = dimension.min
    dmax = dimension.max
    # Calculate the step size for x
    step = (dmax - dmin) / (image_size[0] - 1)
    if vertical:
        for i in range(image_size[0]):
            x = dmax - i * step
            draw.line([(0, i), (extents[1], i)], dimension.get_color(x))
    else:
        for i in range(image_size[0]):
            x = dmin + i * step
            draw.line([(i, 0), (i, extents[1])], dimension.get_color(x))

    return image


def _visualize2d(factory, image_size: tuple) -> Image:
    """Make an image of 2d data.

    image_size is (width,height)
    """
    # Create a new image with a white background
    image = Image.new("RGB", image_size, "white")

    # Get the min and max values for x and y from MultiDimension's dimensions
    x_min = factory.dimensions[0].min
    x_max = factory.dimensions[0].max
    y_min = factory.dimensions[1].min
    y_max = factory.dimensions[1].max

    # Calculate the step size for x and y
    x_step = (x_max - x_min) / (image_size[0] - 1)
    y_step = (y_max - y_min) / (image_size[1] - 1)

    # Plot the values on the 400x400 canvas
    for i in range(image_size[0]):
        for j in range(image_size[1]):
            x = x_min + i * x_step
            y = y_max - j * y_step  # Inverted to match the image coordinates
            color = factory.get_color(x, y)
            image.putpixel((i, j), color)
    return image


def visualize(factory: MultiDimension, orientation: str = "horizontal"):
    """Make a color-spectrum image to show the current config."""
    if not factory.ready:
        print("not ready")
        return
    if len(factory.dimensions) == 1:
        image = visualize_dimension(factory.dimensions[0], (400,20), orientation)
    elif len(factory.dimensions) == 2:
        gap = 5
        main_size = 400
        bar_width = 20
        main_image = _visualize2d(factory, (main_size, main_size))
        x_image = visualize_dimension(
            factory.dimensions[0], (main_size, bar_width)
        )
        y_image = visualize_dimension(
            factory.dimensions[1],
            (main_size, bar_width),
            orientation="vertical",
        )
        image = Image.new(
            "RGB",
            (main_size + gap + bar_width, main_size + gap + bar_width),
            "white",
        )
        image.paste(main_image, (gap + bar_width, 0))
        image.paste(x_image, (gap + bar_width, gap + main_size))
        image.paste(y_image, (0, 0))

    else:
        print(
            f"no visualization available for {len(factory.dimensions)}-D MultiDimension"
        )
        return

    filename = "tmp_plot.png"
    image.save(filename)
    print(f"Saved image as {filename}")


def testable_factory(obj_num: int = 0) -> MultiDimension:
    """Create a variety of MultiDimension objects, for testing & experimenting."""
    if obj_num == 0:
        cf = MultiDimension()
        d1 = cf.add_dimension()
        d1.add_config(-10, "blue")
        d1.add_config(5, "beige")
        d1.add_config(30, "red")
    elif obj_num == 1:
        cf = MultiDimension()
        d1 = cf.add_dimension()
        d1.add_config(-10, "blue")
        d1.add_config(5, "beige")
        d1.add_config(30, "red")
        d2 = cf.add_dimension()
        d2.add_config(0, "yellow")
        d2.add_config(100, "seagreen")
    elif obj_num == 2:
        cf = MultiDimension()
        d1 = cf.add_dimension()
        d1.add_config(0, "white")
        d1.add_config(100, "red")
        d2 = cf.add_dimension()
        d2.add_config(0, "white")
        d2.add_config(100, "blue")
    else:
        print(f"no def for {obj_num}")
    cf.dump()
    return cf

