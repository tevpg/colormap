# colormap

Map data points into a color space.

Conceptually, there is a
- data space: numeric data as x, xy, or xyz
- color space: the range of colors into which data points are mapped
- configuration/map space: configuration for how the data ranges are
    converted, how the colours are combined, etc


ColorMap is the color factory. It exposes methods to configure the factory
and get a color based on dataspace parameters.

Each dataspace dimension is mapped into a single color dimension; when there
are multiple dimensions the resulting colors are then blended using any of
several blend methods.

ColorMap is defined by the color blending method and one or more config dimensions
Each Dimension is defined by the linearity of the relation between the data parameter
and the colorspace color range, and one or more ConfigPoints.
A ConfigPoint maps a single data value in one dimension to a single output color.
A Dimension with only one ConfigPoint simply always maps to that color.
A Dimension with multiple ConfigPoints will interpolate colors along gradiants
defined by numerically adjacent ConfigPoints.  Out of range data values are
clamped to the min/max data values of the available ConfigPoints.


Example use:
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
