import plotly.figure_factory as ff
import json
import sys

# /path/to/df.json
df_path = sys.argv[1]

df = json.load(open(df_path))

# LightGray  #D3D3D3
# SkyBlue    #87CEEB
# Salmon     #FA8072
# LightGreen #90EE90
# DarkSlateGray #2F4F4F
colors = {
    'qw': '#D3D3D3',
    'success': '#87CEEB',
    'failure': '#FA8072',
    'running': '#90EE90',
    'stopped': '#2F4F4F',
}

fig = ff.create_gantt(
    df, 
    colors=colors, 
    index_col='Resource', 
    height=1000,
    show_colorbar=True, showgrid_x=True, showgrid_y=True, group_tasks=True, 
)
fig.show()
