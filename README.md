

Generate blended colors based on n-dimensional data inputs.

Conceptually, there is a
- data space: numeric data in one or more dimensions
- color space: the range of colors which are determined by the data points
- configuration space: configuration for how the data ranges are
    converted, how the colours are combined, etc


MultiDimension is the color factory. It exposes methods to configure the factory
and get a color based on dataspace parameters.

Each dataspace dimension determines a single color (dimension); when there
are multiple dimensions the resulting colors are then blended using any of
several blend methods.

MultiDimension is defined by the color blending method and one or more config dimensions
Each Dimension is defined by the linearity of the relation between the data parameter
and the colorspace color range, and one or more ConfigPoints.
A MappingPoint relates a single data value in one dimension to a single output color.
A Dimension with only one MappingPoint simply always produces that color.
A Dimension with multiple ConfigPoints will interpolate colors along gradiants
defined by numerically adjacent ConfigPoints.  Out of range data values are
clamped to the min/max data values of the available ConfigPoints.


Example use:
factory = MultiDimension(LERP)
d1 = factory.add_dimension(linearity=1)
d2 = factory.add_dimension(linearity=0.5)
d1.add_config(-10,'blue')
d1.add_config(0,'beige')
d1.add_config(30,'orange')
d2.add_config(min_val,'white')
d2.add_config(max_val,'rgb(147,10,20)')


for (various x values, with text):
    print(f"<td style={factory.css_fg_bg(x)}>{x}</td>")


for (various x,y values with no text)
    print(f"<td style={factory.css_bg(x,y)}>&nbsp;<td>")

