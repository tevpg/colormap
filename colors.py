"""


How I want to use this:
my_map = ColorMap(LERP)
d1 = my_map.add_dimension(linearity=1)
d2 = my_map.add_dimension(linearity=0.5)
d1.add_mapping(-10,'blue')
d1.add_mapping(0,'beige')
d1.add_mapping(30,'orange')
d2.add_mapping(min_val,'white')
d2.add_mapping(max_val,'rgb(147,10,20)')


for (various x values, with text):
    print(f"<td style={map_map.css_fg_bg(x)}>{x}</td>")


for (various x,y values with no text)
    print(f"<td style={my_map.css_bg(x,y)}>&nbsp;<td>")


----


BLEND_LERP
BLEND_ADDITIVE
BLEND_

COLOR_NAMES = {}
_reverse_color_names = {}

class Color(str):
    inititalize (__new__) from:
        Color object (return self)
        RGB tuple
        color name string
        color definition string
            "cmyk(c,,y,k)"
            "rgb(x,y,z)"
            "lab(l,a,b)"

    self: str that can be used to define itself. E.g. "rgb(x,y,z)"
    .red, .green, .blue - simple properties.  This is internal representation.
    .rgb - @property
    .hex: str eg #0345ff @property
    .css_fg_bg() @property
    .css_bg() @property
    .cmyk() @property
    .name(): cached @property reverse-calculated str eg "white" or "green(ish)" or ....
    .luminance cached @property
    internal representation: .r, .g, .b .. maybe Lab later

    @classmethod blend:
        constants for blend methods
        method for each blend method (list of colours)
        highest-level function (list of colours, blend_method)



class ConfigPoint(float):
    def __new__(cls, determiner, color):
        instance = super(ConfigPoint, cls).__new__(cls, determiner)
        instance.color = Color(color)
        if not instance.color:
            raise ValueError("Invalid color")
        return instance

    def __eq__(self, other):
        if isinstance(other, ConfigPoint):
            return (self.real == other.real) and (self.color == other.color)
        return False


class Dimension:
    def __init__( self,linearity:float=1):
        self.linearity=linearity
        self.mappings = [] # keep these sorted!
        self.ready = False

    def add_mapping( self, determiner:float, color:str) -> None:
        '''Create a ConfigPoint for a mapping in this dimension.'''
        pt = ConfigPoint(determiner,color)
        if pt is None:
            raise ValueError("Bad determiner of color")
        self.mappings.append(pt)
        self.mappings.sort()
        self.ready = True

class ColorMap:


    def __init__(blend_method:str=LERP):

    def add_dimension( linearity:float=1 ) -> int:
        add an empty dimension
        self.ready = False

    def map( determiner:tuple ) -> Color:

    .num_dimensions - number of dimensions
    .ready: bool # True if enough data to make work, ie >= 1 dimension and >= 1 mapping/dimension
    .dimensions:list

    @property
    def ready(self):
        return all(d.ready for d in self.dimensions) if self.dimensions else False

---
color_tools



---

color_map


dataspace:
- data points:
    - x [y,z..]

color map:
- blend method (=lerp)
- dimensions (1+):
    - linearity (default=1)
    - mapping points (1+):
        - data paremeter
        - color result

colorspace
- color points (colors)


map config point: color + determiner

each map:
    one or more dimensions
    a blend type


axes (dimensions):
    each axis has
        one or more config points
            stored in order sorted by determiner
        a linearity



"""

import re
import math
import statistics
from color_names import COLOR_NAMES

RGBTuple = tuple


class Color:
    # Regular expression pattern to match the rgb str format
    _rgb_pattern = re.compile(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")

    ALPHA_BLEND = "alpha"
    ADDITIVE_BLEND = "additive"
    SUBTRACTIVE_BLEND = "subtractive"
    DIFFERENCE_BLEND = "difference"
    MULTIPLICATIVE_BLEND = "multiplicative"
    OVERLAY_BLEND = "overlay"

    # Calculate _distances among colors
    # _distances = [
    #    math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))
    #    for rgb1 in COLOR_NAMES.values() for rgb2 in COLOR_NAMES.values()
    # ]

    # _distances = []
    # for rgb1 in COLOR_NAMES.values():
    #    for rgb2 in COLOR_NAMES.values():
    #        distance = math.sqrt(sum((a - b) ** 2 for a, b in zip(rgb1, rgb2)))
    #        _distances.append(distance)

    ## Calculate mean and standard deviation
    # _mean_distance = statistics.mean(_distances)
    # _std_deviation = statistics.stdev(_distances)

    # Calculate thresholds based on mean and standard deviation
    # exact_match_threshold = _mean_distance / 3
    # nearly_match_threshold = _mean_distance + _std_deviation
    # moderately_match_threshold = _mean_distance + _std_deviation * 2

    # These are expressed as a distance index, where white<->black is 1.0
    # and identical is 0.0
    exact_match_threshold = 0.01
    nearly_match_threshold = 0.10
    moderately_match_threshold = 0.20

    _reverse_color_names = {v: k for k, v in COLOR_NAMES.items()}

    def __init__(self, color_init):
        """Create the color object.

        Initialize from any of
            Color
            RGB tuple
            color name str
            string like "rgb(20,56,198)"

        """

        rgb: RGBTuple = None
        if isinstance(color_init, Color):
            rgb = color_init.rgb
        elif isinstance(color_init, RGBTuple):
            if len(color_init) == 3:
                rgb = color_init
            else:
                raise ValueError("RGB Tuple must have 3 elements")
        elif isinstance(color_init, str):
            color_init = color_init.lower().strip()
            if color_init.startswith("rgb("):
                rgb = self._parse_rgb_str(color_init)
            elif color_init in COLOR_NAMES:
                rgb = COLOR_NAMES[color_init]
            else:
                raise ValueError(f"Can not get color from '{color_init}'")
        else:
            raise ValueError("Color definition must be string or RGB tuple")
        self._validate_rgb_tuple(rgb)

        self.red, self.green, self.blue = rgb

    @classmethod
    def _parse_rgb_str(cls, color_init) -> RGBTuple:
        # Use re.search to find the values in the string
        match = cls._rgb_pattern.search(color_init)

        if match:
            # Extract the red, green, and blue values as integers
            red = int(match.group(1))
            green = int(match.group(2))
            blue = int(match.group(3))

            # Check if the values are in the valid range (0 to 255)
            if 0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255:
                color_tuple: RGBTuple = (red, green, blue)
                return color_tuple
            else:
                raise ValueError("Color values are out of range (0-255).")
        else:
            raise ValueError("Invalid format in the color_init string.")

    @staticmethod
    def _validate_rgb_tuple(color_tuple: RGBTuple) -> bool:
        """Validate the RGB color tuple, raise error for any problems."""
        if color_tuple is None:
            raise ValueError("Can't get color from init parameter")
        if not isinstance(color_tuple, RGBTuple) or len(color_tuple) != 3:
            raise ValueError("Color tuple must have exactly 3 elements.")
        if not all(isinstance(c, int) for c in color_tuple):
            raise TypeError("All elements of color tuple must be int.")
        if color_tuple != Color._clamp(color_tuple):
            raise ValueError(
                "All elements in the color tuple must be 0 to 255."
            )
        return True

    @property
    def html_color(self):
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"

    @property
    def rgb(self) -> RGBTuple:
        """Return the RGB as a tuple."""
        return (self.red, self.green, self.blue)

    def luminance(self) -> float:
        luminance = 0.299 * self.red + 0.587 * self.green + 0.114 * self.blue
        return luminance

    def __str__(self):
        return f"rgb({self.red},{self.green},{self.blue})"

    def __repr__(self):
        return f"<Color ({self.red},{self.green},{self.blue})>"

    def __eq__(self, other):
        return (
            self.red == other.red
            and self.green == other.green
            and self.blue == other.blue
        )

    def closest_color_name(self):
        if (self.red, self.green, self.blue) in self._reverse_color_names:
            return self._reverse_color_names[(self.red, self.green, self.blue)]

        # Find the name and distance of closest color.
        closest_distance = float("inf")
        closest_color = None
        for this_name, this_rgb in COLOR_NAMES.items():
            this_r, this_g, this_b = this_rgb
            this_distance = math.sqrt(
                (self.red - this_r) ** 2
                + (self.green - this_g) ** 2
                + (self.blue - this_b) ** 2
            )
            closest_distance, closest_color = min(
                (closest_distance, closest_color), (this_distance, this_name)
            )

        # Make a pretty string of the result.

        WHITE_BLACK_DISTANCE = 442.58  # Euclidean dist from white to black
        closeness = closest_distance / WHITE_BLACK_DISTANCE
        if closeness <= Color.exact_match_threshold:
            return f"{closest_color} ({closeness:.3f})"
        elif closeness <= Color.nearly_match_threshold:
            return f"nearly {closest_color} ({closeness:.3f})"
        elif closeness <= Color.moderately_match_threshold:
            return f"{closest_color}(ish) ({closeness:.3f})"
        else:
            return f"vaguely {closest_color} ({closeness:.3f})"

    @staticmethod
    def blend(colors, blend_method=None):
        blend_method = blend_method if blend_method else Color.ALPHA_BLEND
        if not colors:
            raise ValueError("The list of colors must not be empty.")
        elif len(colors) == 1:
            return colors[0]

        result: RGBTuple = (0, 0, 0)

        for color in colors:
            if blend_method == Color.ALPHA_BLEND:
                result = Color._blend_alpha(result, color)
            elif blend_method == Color.ADDITIVE_BLEND:
                result = Color._blend_additive(result, color)
            elif blend_method == Color.SUBTRACTIVE_BLEND:
                result = Color._blend_subtractive(result, color)
            elif blend_method == Color.DIFFERENCE_BLEND:
                result = Color._blend_subtractive(result, color)
            elif blend_method == Color.MULTIPLICATIVE_BLEND:
                result = Color._blend_multiply(result, color)
            elif blend_method == Color.OVERLAY_BLEND:
                result = Color._blend_overlay(result, color)
            else:
                raise ValueError(f"Invalid blend method: {blend_method}")

        return result

    @staticmethod
    def _blend_alpha(base_color: RGBTuple, blend_color: RGBTuple) -> RGBTuple:
        """Alpha blending of two RGB color tuples."""
        alpha = blend_color[3] / 255.0  # Alpha value in the range 0-1
        blended_color = (
            int(base_color[0] + (blend_color[0] - base_color[0]) * alpha),
            int(base_color[1] + (blend_color[1] - base_color[1]) * alpha),
            int(base_color[2] + (blend_color[2] - base_color[2]) * alpha),
        )
        return Color._clamp(blended_color)

    @staticmethod
    def _blend_additive(
        base_color: RGBTuple, blend_color: RGBTuple
    ) -> RGBTuple:
        """Additive blending of two RGB color tuples."""
        blended_color = (
            min(255, base_color[0] + blend_color[0]),
            min(255, base_color[1] + blend_color[1]),
            min(255, base_color[2] + blend_color[2]),
        )
        return Color._clamp(blended_color)

    @staticmethod
    def _blend_subtractive(
        base_color: RGBTuple, blend_color: RGBTuple
    ) -> RGBTuple:
        """Subtractive blending of two RGB color tuples."""
        blended_color = (
            max(0, base_color[0] - blend_color[0]),
            max(0, base_color[1] - blend_color[1]),
            max(0, base_color[2] - blend_color[2]),
        )
        return Color._clamp(blended_color)

    @staticmethod
    def _blend_difference(
        base_color: RGBTuple, blend_color: RGBTuple
    ) -> RGBTuple:
        """Difference blending of two RGB color tuples."""
        blended_color = (
            abs(base_color[0] - blend_color[0]),
            abs(base_color[1] - blend_color[1]),
            abs(base_color[2] - blend_color[2]),
        )
        return Color._clamp(blended_color)

    @staticmethod
    def _blend_multiply(
        base_color: RGBTuple, blend_color: RGBTuple
    ) -> RGBTuple:
        """Multiplicative blending of two RGB color tuples."""
        blended_color = (
            (base_color[0] * blend_color[0]) // 255,
            (base_color[1] * blend_color[1]) // 255,
            (base_color[2] * blend_color[2]) // 255,
        )
        return Color._clamp(blended_color)

    @staticmethod
    def _blend_overlay(
        base_color: RGBTuple, blend_color: RGBTuple
    ) -> RGBTuple:
        """Overlay blending of two RGB color tuples."""

        def overlay_channel(base, blend):
            if base <= 127:
                return (2 * base * blend) // 255
            else:
                return 255 - (2 * (255 - base) * (255 - blend)) // 255

        blended_color = (
            overlay_channel(base_color[0], blend_color[0]),
            overlay_channel(base_color[1], blend_color[1]),
            overlay_channel(base_color[2], blend_color[2]),
        )
        return Color._clamp(blended_color)

    @staticmethod
    def _clamp(color_tuple: RGBTuple) -> RGBTuple:
        """Clamp the values of a color tuple to the range 0-255."""
        return tuple(max(0, min(255, value)) for value in color_tuple)

    # And here, where it is easy to lose track of, is initialization.
