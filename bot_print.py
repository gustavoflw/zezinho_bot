def print_with_colors(string, color='white'):
    colors = {
        'bold': '\033[1m',
        'underline': '\033[4m',
        'end': '\033[0m',
        'white': '\033[97m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'magenta': '\033[95m'
    }
    print(f"{colors[color]}{string}{colors['end']}")
