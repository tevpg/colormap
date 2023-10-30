"""Create an html table showing shades of a 2d ColorFactory."""

import data_colors as dc

##import data_color_extras as extras


class html_thing:
    def __init__(self) -> None:
        self.text = ""

    def print(self):
        print(self.text)
        self.text = ""

    def add(self, text_to_add):
        self.text += text_to_add

    @staticmethod
    def html_bottom():
        return "</body></html>"

    @staticmethod
    def html_top(cell_wid: int = 26):
        return """Content-type: text/html\n\n
            <!DOCTYPE html>
            <html>
            <head>

            </head>
            <body>
    """

    @staticmethod
    def style_sheet(cell_wid: int = 25) -> str:
        """Return a style sheet for the table."""
        return f"""<style>
            html {{
                font-family: sans-serif;
            }}
            table {{
                border-collapse: collapse;
                font-size: 0.8rem;
            }}
            table, th, td {{
                border: none;
            }}
            th, td {{
                width: {cell_wid}px;
                height: {cell_wid}px;
                padding: 0;
            }}
            .rotate {{
                text-align: center;
                white-space: nowrap;
                vertical-align: middle;
                width: 1.5em;
            }}
            .rotate div {{
                    -moz-transform: rotate(-90.0deg);  /* FF3.5+ */
                    -o-transform: rotate(-90.0deg);  /* Opera 10.5 */
                -webkit-transform: rotate(-90.0deg);  /* Saf3.1+, Chrome */
                            filter:  progid:DXImageTransform.Microsoft.BasicImage(rotation=0.083);  /* IE6,IE7 */
                        -ms-filter: "progid:DXImageTransform.Microsoft.BasicImage(rotation=0.083)"; /* IE8 */
                        margin-left: -10em;
                        margin-right: -10em;
            }}

            table {{border:1px solid #000;}}
            tr {{border-top:1px solid #000;}}
            tr + tr {{border-top:1px solid white;}}
            td {{border-left:1px solid #000;}}
            td + td {{border-left:1px solid white;}}

            </style>"""


def make_html_color_table(
    factory: dc.ColorFactory,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    num_rows: int = 20,
    num_columns: int = 20,
) -> str:
    """Create html color table for cf and return it as a string."""

    def top_color(dim: dc.Dimension) -> str:
        """Get html color of greatest ConfigPoint in this dimension."""
        clr: dc.Color = dim.configs[-1].color
        return clr.html_color

    def axis_label(dim: dc.Dimension) -> str:
        """Make a default label for this dimension."""
        lab = " => ".join([p.color.similar_to() for p in dim.configs])
        if dim.interpolation_exponent != 1:
            lab = f"{lab}  exp={dim.interpolation_exponent}"
        return lab

    def cell(factory: dc.ColorFactory, x_index, y_index) -> str:
        """Return a coloured html table cell."""
        c = factory.get_color(x_index, y_index).html_color
        return (
            f"<td style={factory.css_bg((x_index,y_index))} title='{c}'></td>"
        )

    x: dc.Dimension = factory.dimensions[0]
    y: dc.Dimension = factory.dimensions[1]
    if not x_label:
        x_label = axis_label(x)
    if not y_label:
        y_label = axis_label(y)
    if not title:
        title = f"Blend method: {factory.blend_method}"

    x_min = x.min
    x_max = x.max
    y_min = y.min
    y_max = y.max

    x_step = x.range / (num_columns - 1)
    y_step = y.range / (num_rows - 1)

    html = html_thing()

    # Generate the HTML code
    ##html.add(html_thing.style_sheet(cell_width))
    html.add(
        f"""    <table> {html_thing.style_sheet()}
            <tbody>
            <tr>
                <td colspan="{num_columns+1}" style="text-align: center">{title}</td>
            </tr>
    """
    )

    # Generate the data rows
    # top row (includes y_max)

    y_index = y.max
    rownum = 1
    html.add("            <tr>")
    html.add(
        f"               <td style='{y.css_fg_bg(y_max)}'>{round(y_max)}</td>"
    )
    x_index = x_min
    for _ in range(num_columns):
        html.add(cell(factory, x_index, y_index))
        x_index += x_step
    html.add("</tr>\n")
    rownum += 1
    y_index -= y_step

    html.add(
        f"""
            <tr>
                <td rowspan="{num_rows-1}" class="rotate" style="text-align: center"><div>{y_label}</div></td>
            </tr>
    """
    )

    while rownum < num_rows:
        html.add("            <tr>")
        x_index = x_min
        for _ in range(num_columns):
            html.add(cell(factory, x_index, y_index))
            x_index += x_step
        html.add("</tr>\n")
        rownum += 1
        y_index -= y_step

    # bottom row (includes y_min)
    html.add("            <tr>")
    html.add(
        f"               <td style='{y.css_fg_bg(y_min)}'>{round(y_min)}</td>"
    )
    x_index = x_min
    for _ in range(num_columns):
        html.add(cell(factory, x_index, y_index))
        x_index += x_step
    html.add("</tr>\n")

    # label row at the bottom
    bottom_row_merge = 2
    html.add("<tr>")
    html.add("<td></td>")
    html.add(
        f'<td colspan={bottom_row_merge} style="text-align: left;{x.css_fg_bg(x_min)};">{round(x_min)}</td>'
    )
    html.add(
        f'<td colspan={num_columns - 2 * bottom_row_merge} style="text-align: center">{x_label}</td>'
    )
    html.add(
        f'<td colspan={bottom_row_merge} style="text-align: right; {x.css_fg_bg(x_max)};">{round(x_max)}</td>'
    )
    html.add("</tr>")

    # Close the HTML
    html.add(
        """        </tbody>
        </table>
    """
    )
    return html.text


if __name__ == "__main__":
    rows = 15
    columns = 15
    cell_width = 30

    cf = dc.ColorFactory()  # dc.MULTIPLICATIVE_BLEND)
    d = cf.add_dimension(1)
    d.add_config(0, "white")
    d.add_config(50, "crimson")  # (100,255,255))
    d = cf.add_dimension(0.67)
    d.add_config(0, "white")
    d.add_config(100, "blue")  # "#4343d3")#"royalblue")

    print(html_thing.html_top(cell_wid=cell_width))
    for blend in [
        dc.MULTIPLICATIVE_BLEND,
        dc.MIN_BLEND,
        dc.MAX_BLEND,
        dc.ALPHA_BLEND,
        dc.SUBTRACTIVE_BLEND,
        dc.DIFFERENCE_BLEND,
        dc.OVERLAY_BLEND,
        dc.ADDITIVE_BLEND,
    ]:
        cf.blend_method = blend
        print(
            make_html_color_table(
                cf,
                #title="Legend for activity chart",
                #x_label="Busy (in+out)",
                #y_label="Full (bikes present)",
                num_columns=columns,
                num_rows=rows,
            )
        )

    print(html_thing.html_bottom)

    dump = cf.dump(quiet=True)
    print("\n\n<pre>")
    for l in dump:
        print(l)
    print("</pre>")
