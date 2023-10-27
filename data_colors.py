"""Generate blended colors based on n-dimensional data inputs.

Copyright (c) 2023, tevpg@github.com

Conceptually, there is a
- data space: numeric data in one or more dimensions
- color space: the range of colors which are determined by the data points
- configuration space: configuration for how the data ranges are
    converted, how the colours are combined, etc

ColorFactory is the color factory. It exposes methods to configure the factory
and get a color based on dataspace parameters.

Each dataspace dimension determines a single color (dimension); when there
are multiple dimensions the resulting colors are then blended using any of
several blend methods.

ColorFactory is defined by the color blending method and one or more config dimensions
Each Dimension is defined by the interpolation_exponent of the relation between the
data parameter and the colorspace color range, and one or more ConfigPoints.
A ConfigPoint relates a single data value in one dimension to a single output color.
A Dimension with only one ConfigPoint simply always produces that color.
A Dimension with multiple ConfigPoints will interpolate colors along gradiants
defined by numerically adjacent ConfigPoints.  Out of range data values are
clamped to the min/max data values of the available ConfigPoints.

Example use:
factory = ColorFactory(LERP)
d1 = factory.add_dimension(interpolation_exponent=1)
d2 = factory.add_dimension(interpolation_exponent=0.5)
d1.add_config(-10,'blue')
d1.add_config(0,'beige')
d1.add_config(30,'orange')
d2.add_config(min_val,'white')
d2.add_config(max_val,'rgb(147,10,20)')

for (various x values, with text):
    print(f"<td style={factory.css_fg_bg(x)}>{x}</td>")

for (various x,y values with no text)
    print(f"<td style={factory.css_bg(x,y)}>&nbsp;<td>")


"""

import re
import math
from functools import lru_cache

from color_names import COLOR_NAMES

LERP_BLEND = "lerp"  # linear interpolation
ALPHA_BLEND = LERP_BLEND
ADDITIVE_BLEND = "additive"
SUBTRACTIVE_BLEND = "subtractive"
DIFFERENCE_BLEND = "difference"
MULTIPLICATIVE_BLEND = "multiplicative"
OVERLAY_BLEND = "overlay"


class Color(tuple):
    """A single color and its behaviors."""

    # Regular expression pattern to match the rgb str format
    _rgb_pattern = re.compile(r"rgb\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)")

    # Reversed color names dict for similar_to()
    _reverse_color_names = {v: k for k, v in COLOR_NAMES.items()}

    def __new__(cls, color_init):
        """Create the color object.

        Initialize from any of
            Color object
            RGB tuple, e.g. (127, 0, 255)
            color name str, e.g. "seagreen"
            rgb string, e.g. "rgb(20, 56, 198)"
        """
        if isinstance(color_init, Color):
            return color_init

        rgb = None
        # if isinstance(color_init, Color):
        #    rgb = tuple(color_init)
        if isinstance(color_init, tuple):
            if len(color_init) == 3:
                rgb = color_init
            else:
                raise ValueError("RGB Tuple must have 3 elements")
        elif isinstance(color_init, str):
            color_init = color_init.lower().strip()
            if color_init.startswith("rgb("):
                rgb = cls._parse_rgb_str(color_init)
            elif color_init.startswith("#"):
                rgb = cls._parse_html_str(color_init)
            elif color_init in COLOR_NAMES:
                rgb = COLOR_NAMES[color_init]
            else:
                raise ValueError(f"Can not get color from '{color_init}'")
        else:
            raise ValueError("Color definition must be a string or RGB tuple")

        cls._validate_rgb_tuple(rgb)
        return super(Color, cls).__new__(cls, rgb)

    @property
    def red(self):
        """Get color band from tuple."""
        return self[0]

    @property
    def green(self):
        """Get color band from tuple."""
        return self[1]

    @property
    def blue(self):
        """Get color band from tuple."""
        return self[2]

    # @property
    # def rgb(self):
    #    """Return rgb -- FIXME placeholder until scrub out 'rgb' use elsewhere."""
    #    return tuple(self)

    @staticmethod
    def _validate_rgb_tuple(rgb):
        """Test that rgb is a valid RGB tuple."""
        if not all(0 <= c <= 255 for c in rgb):
            raise ValueError("RGB values must be between 0 and 255")

    @staticmethod
    def _parse_html_str(html_str: str) -> tuple:
        """Parse R,G,B from an html color str (e.g. "#ffe720").

        Precondition: already know it starts with "#".
        """
        try:
            r = int(html_str[1:3], 16)
            g = int(html_str[3:5], 16)
            b = int(html_str[5:7], 16)
        except ValueError:
            raise ValueError("Invalid HTML color string.")

        return (r, g, b)

    @staticmethod
    def _parse_rgb_str(rgb_str) -> tuple:
        """Get an RGB tuple from a str like 'rgb(30,77,220)'."""
        match = Color._rgb_pattern.match(rgb_str)
        if match:
            rgb = tuple(int(match.group(i)) for i in range(1, 4))
            Color._validate_rgb_tuple(rgb)
            return rgb
        raise ValueError("Invalid RGB string format")

    @staticmethod
    def _validate_rgb_tuple(color_tuple: tuple) -> bool:
        """Validate the RGB color tuple, raise error for any problems."""
        if color_tuple is None:
            raise ValueError("Can't get color from init parameter")
        if not isinstance(color_tuple, tuple) or len(color_tuple) != 3:
            raise ValueError("Color tuple must have exactly 3 elements.")
        if not all(isinstance(c, int) for c in color_tuple):
            raise TypeError("All elements of color tuple must be int.")
        if color_tuple != Color._clamp_tuple(color_tuple):
            raise ValueError(
                "All elements in the color tuple must be 0 to 255."
            )
        return True

    @staticmethod
    def _clamp_tuple(color_tuple: tuple) -> tuple:
        """Clamp the values of a color tuple to the range 0-255."""
        return tuple(max(0, min(255, value)) for value in color_tuple)

    @property
    def html_color(self):
        """Return color as an HTML color str (e.g. '#07f378')."""
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}"

    def luminance(self) -> float:
        """Calculate the color's luminance."""
        luminance = 0.299 * self.red + 0.587 * self.green + 0.114 * self.blue
        return luminance

    def css_bg(self) -> str:
        """Make a CSS background color style string component."""
        return f"background-color:{self.html_color};"

    def css_fg_bg(self) -> str:
        """Make CSS style background color component with contrasting text color."""
        fg = "black" if self.luminance() >= 0.5 else "white"
        return f"color:{fg};background-color:{self.html_color};"

    def __str__(self):
        """Str representation.

        This is such that can be used to init a Color.
        """
        return f"rgb({self.red},{self.green},{self.blue})"

    def __repr__(self):
        """Color representation."""
        return f"<Color ({self.red},{self.green},{self.blue})>"

    def __eq__(self, other):
        """Test equality as having same RGB."""
        return (
            self.red == other.red
            and self.green == other.green
            and self.blue == other.blue
        )

    def similar_to(self):
        """Get human-readable name for what this color is kinda like.

        Distance to nearest color is expressed as % of maximum color
        distance possible (ie distance from white to black).
        Uses the color dictionary and its reverse, initialized above.

        """
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

        # Closeness to the color is fraction of its distance compared
        # to max distance in the RGB color cube (dist from white to black)
        # pylint: disable-next=invalid-name
        WHITE_BLACK_DISTANCE = 441.67  # sqrt(3 * 255*255)
        closeness = closest_distance / WHITE_BLACK_DISTANCE
        return f"{closest_color} ({(1 - closeness)*100:.1f}% match)"

    @staticmethod
    def invert( color:'Color') -> 'Color':
        """Inverts the color."""
        r = 255-color[0]
        g = 255-color[1]
        b = 255-color[2]
        return Color(Color._clamp_tuple((r,g,b)))

    @staticmethod
    def blend(colors_list: list["Color"], blend_method=ALPHA_BLEND) -> tuple:
        """Blend unspecified number of colors together."""
        if not colors_list:
            raise ValueError("The list of colors must not be empty.")

        if len(colors_list) == 1:
            return colors_list[0]
        # Blend first two colors until only one color left
        while len(colors_list) > 2:
            # Reduce list by blending 1st 2 colors.
            colors_list = [
                Color.blend(colors_list[:2], blend_method)
            ] + colors_list[2:]

        # At this point, there are exactly two colors.
        color1, color2 = colors_list[0:2]
        if blend_method in [LERP_BLEND, ALPHA_BLEND]:
            result = Color.blend_lerp(color1, color2)
        elif blend_method == ADDITIVE_BLEND:
            result = Color._blend_additive(color1, color2)
        elif blend_method == SUBTRACTIVE_BLEND:
            result = Color._blend_subtractive(color1, color2)
        elif blend_method == DIFFERENCE_BLEND:
            result = Color._blend_difference(color1, color2)
        elif blend_method == MULTIPLICATIVE_BLEND:
            result = Color._blend_multiply(color1, color2)
        elif blend_method == OVERLAY_BLEND:
            result = Color._blend_overlay(color1, color2)
        else:
            raise ValueError(f"Invalid blend method: {blend_method}")

        return result

    @staticmethod
    def blend_lerp(
        base_color: "Color", blend_color: "Color", alpha: float = 0.5
    ) -> "Color":
        """Blend two colours using linear interpolation.

        This seems to be the same thing as ALPHA.
        """
        alpha = max(0.0, min(1.0, alpha))  # Ensure alpha is within [0, 1]
        blended_color = Color(
            (
                int(
                    base_color.red + (blend_color.red - base_color.red) * alpha
                ),
                int(
                    base_color.green
                    + (blend_color.green - base_color.green) * alpha
                ),
                int(
                    base_color.blue
                    + (blend_color.blue - base_color.blue) * alpha
                ),
            )
        )
        ##print(f"here in blend_lerp, {type(blended_color)=}")
        return blended_color

    @staticmethod
    def _blend_additive(base_color: "Color", blend_color: "Color") -> "Color":
        """Additive blending of two RGB color tuples."""
        blended_color = (
            min(255, base_color.red + blend_color.red),
            min(255, base_color.green + blend_color.green),
            min(255, base_color.blue + blend_color.blue),
        )
        return Color(blended_color)

    @staticmethod
    def _blend_subtractive(
        base_color: "Color", blend_color: "Color"
    ) -> "Color":
        """Subtractive blending of two RGB color tuples."""
        blended_color = (
            max(0, base_color.red - blend_color.red),
            max(0, base_color.green - blend_color.green),
            max(0, base_color.blue - blend_color.blue),
        )
        return Color(blended_color)

    @staticmethod
    def _blend_difference(
        base_color: "Color", blend_color: "Color"
    ) -> "Color":
        """Difference blending of two RGB color tuples."""
        blended_color = (
            abs(base_color.red - blend_color.red),
            abs(base_color.green - blend_color.green),
            abs(base_color.blue - blend_color.blue),
        )
        return Color(blended_color)

    @staticmethod
    def _blend_multiply(base_color: "Color", blend_color: "Color") -> "Color":
        """Multiplicative blending of two RGB color tuples."""
        blended_color = (
            (base_color.red * blend_color.red) // 255,
            (base_color.green * blend_color.green) // 255,
            (base_color.blue * blend_color.blue) // 255,
        )
        return Color(blended_color)

    @staticmethod
    def _blend_overlay(base_color: "Color", blend_color: "Color") -> "Color":
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
        return Color(blended_color)


class ConfigPoint(float):
    """A single dataspace point to color definition.

    Each is essentially a value point (e.g. 37.6) and a Color
    If handled naively it will feel like a float.
    """

    def __new__(cls, determiner, color):
        """Create new float object for the instance."""
        instance = super(ConfigPoint, cls).__new__(cls, determiner)
        instance.color = Color(color)
        if not instance.color:
            raise ValueError("Invalid color")
        return instance

    def __eq__(self, other):
        """Test for equality: both value and color."""
        if isinstance(other, ConfigPoint):
            return (self.real == other.real) and (self.color == other.color)
        return False

    def dump(
        self, indent: str = "", index: int = None, quiet: bool = False
    ) -> list[str]:
        """Dump the contents of the ConfigPoint as readable text.

        Returns the contents as a list of strings (lines) and by default, prints.

        :index, if present, is just a courtesy number to add to the text
        :indent is what to put at the start of each line (e.g. "  ")
        :quiet, if True, suppresses printing.
        """
        index = "" if index is None else index
        lines = [
            f"{indent}ConfigPoint {index}:  {self.real:6.2f};  "
            f"{str(self.color):16s} --> {self.color.similar_to()}"
        ]
        if not quiet:
            for line in lines:
                print(line)
        return lines


class Dimension(int):
    """Dimension obects handle all the mappings for one data dimension.

    E.g. x, or y.  It has a collection of ConfigPoints and the exponent
    for the curve that is used in the interpolation between the ConfigPoints.
    Higher exponent (>1) emphasizes small differences at the top end of the
    range; low exponent (<1) emphasizes small differences at the bottom
    of the range.

    The int value is simply an id.
    """

    _current_value = 0

    def __new__(cls, interpolation_exponent: float = 1):
        """Create new instance."""
        instance = super(Dimension, cls).__new__(cls, cls._current_value)
        cls._current_value += 1
        return instance

    def __init__(self, interpolation_exponent: float = 1):
        """Set initial values for Dimension properties."""
        if interpolation_exponent < 0:
            raise ValueError("Interpolation exponent must be >= 0.")
        self.interpolation_exponent = interpolation_exponent
        self.configs = []
        self.ready = False
        self.min = None
        self.max = None
        self.range = None

    def add_config(self, determiner: float, color: str) -> None:
        """Add a ConfigPoint to this dimension."""
        pt = ConfigPoint(determiner, color)
        if pt is None:
            raise ValueError("Bad determiner of color")
        if pt.real in [cp.real for cp in self.configs]:
            raise ValueError(
                f"ConfigPoint with determiner {pt} already exists"
            )
        self.configs.append(pt)
        self.configs.sort()
        self.min = float(min(self.configs))
        self.max = float(max(self.configs))
        self.range = self.max - self.min
        self.ready = True

    def get_color(self, determiner: float) -> Color:
        """Blend within gradients to get a color for this determiner value."""
        if self.range <= 0:
            return self.configs[0].color

        # Clamp determiner to self's range
        determiner = max(self.min, min(self.max, determiner))
        # Adjust determiner according to the self's interpolation_exponent
        determiner_range = determiner - self.min
        adjusted_determiner = self.min + (
            determiner_range**self.interpolation_exponent
        ) * (self.range ** (1 - self.interpolation_exponent))

        # Find the two adjacent ConfigPoints for interpolation
        for j in range(len(self.configs) - 1):
            if adjusted_determiner <= self.configs[j + 1]:
                gradient_min = self.configs[j]
                gradient_max = self.configs[j + 1]
                break

        if gradient_min.real == gradient_max.real:
            raise ValueError("Gradient has the same min and max values.")

        # Interpolate between the two adjacent colors
        blend_factor = (adjusted_determiner - gradient_min.real) / float(
            gradient_max - gradient_min
        )
        return Color.blend_lerp(
            gradient_min.color, gradient_max.color, blend_factor
        )

    def css_bg(self, determiner: float) -> str:
        """Make a CSS background color style string component."""
        bg = self.get_color(determiner)
        bgcol = Color(bg)
        return f"background-color:{bgcol.html_color};"

    def css_fg_bg(self, determiner: float) -> str:
        """Make CSS style background color component with contrasting text color."""
        bg = self.get_color(determiner)
        fg = "black" if bg.luminance() >= 0.5 else "white"
        return f"color:{fg};background-color:{bg.html_color};"

    def dump(
        self, indent: str = "", index: int = None, quiet: bool = False
    ) -> list[str]:
        """Dump the contents of the Dimension as readable text.

        Returns the contents as a list of strings (lines) and by default, prints.

        :index, if present, is just a courtesy number to add to the Dimension text
        :indent is what to put at the start of each line (e.g. "  ")
        :quiet, if True, suppresses printing.

        """
        index = "" if index is None else index
        lines = []
        lines.append(f"{indent}Dimension {index}:")
        lines.append(
            f"{indent}  ready: {self.ready}; configs: {len(self.configs)}; "
            f"min/max/range: {self.min}/{self.max}/{self.range}; "
            f"interpolation_exponent: {self.interpolation_exponent}"
        )
        for j, pt in enumerate(self.configs):
            pt: ConfigPoint
            lines = lines + pt.dump("      ", j, quiet=True)
        if not quiet:
            for line in lines:
                print(line)
        return lines


class ColorFactory:
    """ColorFactory looks after n-dimensional mappings their colors."""

    def __init__(self, blend_method: str = ALPHA_BLEND):
        """Initialize empty ColorFactory (not much to it)."""
        self.blend_method = blend_method
        self.dimensions = []  # Each is a Dimension
        self._config_hash = 0

    def add_dimension(self, interpolation_exponent: float = 1) -> Dimension:
        """Add an empty Dimension to the ColorFactory."""
        d = Dimension(interpolation_exponent)
        self.dimensions.append(d)
        return d

    def _get_hash(self):
        """Get a hash of the ColorFactory config (for change detection)."""
        return hash(str(self.unload()))

    def get_color(self, *determiner_tuple: tuple) -> Color:
        """Wrap _chached_get_color so can clear its lru cache if needed."""
        current_config_hash = self._get_hash()
        if current_config_hash != self._config_hash:
            self._cached_get_color.cache_clear()
            self._config_hash = current_config_hash
        return self._cached_get_color(determiner_tuple)

    @lru_cache(maxsize=100)  # Guessing cachesize that woule be about right
    def _cached_get_color(self, determiner_tuple: tuple) -> Color:
        if not self.ready:
            raise ValueError("ColorFactory is not ready")

        if len(determiner_tuple) != self.num_dimensions:
            raise ValueError(
                f"Different number of dimensions in determiner ({len(determiner_tuple)}) "
                f"and configuration ({self.num_dimensions})."
            )

        # Calculate colors for each dimension
        colors_list = []
        for i, dimension in enumerate(self.dimensions):
            colors_list.append(dimension.get_color(determiner_tuple[i]))

        # Blend the dimensions' colors into one
        final_color = Color.blend(colors_list, self.blend_method)
        return final_color

    @property
    def num_dimensions(self):
        """Count number of dimensions in this configuration."""
        return len(self.dimensions)

    @property
    def ready(self):
        """Test if the ColorFactory has enough configuration to work."""
        return (
            all(d.ready for d in self.dimensions) if self.dimensions else False
        )

    def css_bg(self, determiner: tuple) -> str:
        """Make a CSS background color style string component."""
        bg = self.get_color(*determiner)
        #print(f"{(type(bg))=}")
        bgcol = Color(bg)
        return f"background-color:{bgcol.html_color};"

    def css_fg_bg(self, determiner: tuple) -> str:
        """Make CSS style background color component with contrasting text color."""
        bg = self.get_color(*determiner)
        fg = "black" if bg.luminance() >= 0.5 else "white"
        return f"color:{fg};background-color:{bg.html_color};"

    def unload(self) -> list:
        """Unload the full factory configuration info (only) into simple list.

        This list could be used to load a factory.

        Structure:
        returns: [blend_method, dimension_list, dimension_list..]
            dimension_list: [interpolation_exponent, configlist]
            config_list: [ConfigPoint, ConfigPoint..]
            ConfigPoint: [value, color_as_html_hex_string]

        Notes for later:  to use this as a way to save configurations...
        - str() can be saved, then turned back into this structure using eval()
        """
        dimlist = []
        for dim in self.dimensions:
            conlist = []
            dim:Dimension
            for con in dim.configs:
                conlist.append([con.real,con.color.html_color])
            thisdim = [dim.interpolation_exponent,conlist]
            dimlist.append(thisdim)
        faclist = [self.blend_method,dimlist]
        return faclist

    def dump(self, quiet: bool = False) -> list[str]:
        """Dump the contents of the ColorFactory.

        Returns the contents as a list of strings (lines).
        By default it also prints the info; quiet flag
        will suppress printing.
        """
        lines = []
        lines.append(f"ColorFactory {self}")
        lines.append(
            f"  ready: {self.ready}; dimensions: {len(self.dimensions)}; "
            f"blend method: {self.blend_method}"
        )
        for i, d in enumerate(self.dimensions):
            d: Dimension
            lines = lines + d.dump("  ", i, quiet=True)

        if not quiet:
            for line in lines:
                print(line)
        return lines
