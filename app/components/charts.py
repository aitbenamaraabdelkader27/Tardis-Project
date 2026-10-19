import plotly.express as px

COLORS = ["#166453", "#3b74a0", "#9bb8ae"]
px.defaults.template = "plotly_white"
px.defaults.color_discrete_sequence = COLORS


def polish(figure):
    figure.update_layout(font=dict(family="Arial, sans-serif", color="#243b43", size=13),
                         paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                         margin=dict(l=10, r=15, t=55, b=15), height=360,
                         title_font_size=17, legend_title_text="")
    figure.update_xaxes(showgrid=False)
    figure.update_yaxes(gridcolor="#e8eeeb", zerolinecolor="#d3dfda")
    return figure
