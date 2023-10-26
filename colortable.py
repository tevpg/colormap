import data_colors as dc

class html_thing:
    def __init__(self) -> None:
        self.text = ""

    def print(self):
        print(self.text)
        self.text = ""

    def add(self, text_to_add):
        self.text += text_to_add


def make_html_color_table(
    factory: dc.ColorFactory,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
) -> str:
    """Create html color table for cf and return it as a string."""


    # Define the dimensions of the table
    num_rows = 20
    num_columns = 20
    cell_width = 26  # Adjust this value for your desired cell width in pixels
    table_width = cell_width * num_columns

    x:dc.Dimension = factory.dimensions[0]
    y:dc.Dimension = factory.dimensions[1]
    if not x_label:
        x_label = x.configs[1].color.similar_to()
    if not y_label:
        x_label = y.configs[1].color.similar_to()
    if not title:
        title = f"Plot of {x_label} and {y_label}"

    x_min = x.min
    x_max = x.max
    y_min = y.min
    y_max = y.max

    x_step = x.range/num_columns
    y_step = y.range / num_rows

    html = html_thing()

    # Generate the HTML code
    html.add(
        f"""Content-type: text/html

    <!DOCTYPE html>
    <html>
    <head>
        <style>
            table {{
                border-collapse: collapse;
                width: {table_width};
            }}
            table, th, td {{
                border: none;
            }}
            th, td {{
                width: {cell_width}px;
                height: {cell_width}px;
                padding: 0;
            }}
            .vertical-text {{
                white-space: nowrap;
                transform: rotate(-90deg);
            }}
            .narrow-first-column {{
                width: 25px;  /* Set your desired width here */
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
            th:first-child, td:first-child {{
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
            }}
            th:last-child, td:last-child {{
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
            }}
            tr:first-child th {{
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
            }}
            tr:last-child th {{
                border-left: none;
                border-right: none;
                border-top: none;
                border-bottom: none;
            }}
        </style>
    </head>
    <body>
    """
    )

    html.add(
        f"""    <table>
            <tbody>
            <tr>
                <td colspan="{num_columns+1}" style="text-align: center">{title}</td>
            </tr>
    """
    )

    # Generate the data rows
    # top row (includes y_max)

    def one_cell(cf:dc.ColorFactory,x_index,y_index) -> str:
        """Return a style for this cell."""
        col = cf.css_bg((x_index,y_index))
        return
    y_index = y.max
    rownum = 1
    html.add("            <tr>")
    html.add(f"               <td>{y_max}</td>")
    for col in range(num_columns):
        html.add(f"<td style='background-color:grey'>{rownum}</td>")
    html.add("</tr>\n")
    rownum += 1

    html.add(
        f"""
            <tr>
                <td rowspan="{num_rows-1}" class="rotate" style="text-align: center"><div>{y_label}</div></td>
            </tr>
    """
    )

    while rownum < num_rows:
        html.add("            <tr>")
        for _ in range(num_columns):
            html.add(f"<td style='background-color:grey'>{rownum}</td>")
        html.add("</tr>\n")
        rownum += 1
    # bottom row (includes y_min)
    html.add("            <tr>")
    html.add(f"               <td>{y_min}</td>")
    for col in range(num_columns):
        html.add(f"<td style='background-color:grey'>{rownum}</td>")
    html.add("</tr>\n")

    # label row at the bottom
    html.add("<tr>")
    html.add("<td></td>")
    html.add(f'<td colspan=5 style="text-align: left">{x_min}</td>')
    html.add(
        f'<td colspan={num_columns - 5 - 5} style="text-align: center">{x_label}</td>'
    )
    html.add(f'<td colspan=5 style="text-align: right">{x_max}</td>')
    html.add("</tr>")

    # Close the HTML
    html.add(
        """        </tbody>
        </table>
    </body>
    </html>
    """
    )

    # Print the HTML, or you can save it to a file manually
    html.print()

if __name__ == "__main__":

    cf = dc.ColorFactory(dc.MULTIPLICATIVE_BLEND)
    d = cf.add_dimension()
    d.add_config(0, "white")
    d.add_config(100, "royalblue")
    d = cf.add_dimension()
    d.add_config(0, "white")
    d.add_config(100, "tomato")

    print(make_html_color_table(cf))