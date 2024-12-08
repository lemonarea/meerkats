
# app title function
def get_app_title():
    return "Meerkat"

# Function to format positive and negative values
def format_value(value):
    if value >= 1e6:
        return f'{value/1e6:.1f}M'
    elif value >= 1e3:
        return f'{value/1e3:.1f}K'
    elif value <= -1e6:
        return f'{value/1e6:.1f}M'
    elif value <= -1e3:
        return f'{value/1e3:.1f}K'
    else:
        return f'{value:.1f}'