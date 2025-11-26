import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def apply_shadcn_light_theme():
    """Apply shadcn-inspired light theme to matplotlib"""
    plt.style.use('default')
    
    # Colors inspired by shadcn
    primary_color = '#0078d4'
    background_color = '#ffffff'
    text_color = '#464646'
    border_color = '#e4e4e7'
    
    plt.rcParams.update({
        # Figure
        'figure.facecolor': background_color,
        'figure.edgecolor': 'none',
        
        # Axes
        'axes.facecolor': background_color,
        'axes.edgecolor': border_color,
        'axes.linewidth': 1,
        'axes.grid': True,
        'axes.grid.axis': 'y',
        'axes.labelcolor': text_color,
        'axes.prop_cycle': plt.cycler('color', [primary_color]),
        
        # Grid
        'grid.color': border_color,
        'grid.linestyle': '-',
        'grid.linewidth': 0.5,
        'grid.alpha': 0.3,
        
        # Lines
        'lines.linewidth': 2.5,
        'lines.solid_capstyle': 'round',
        
        # Text
        'font.size': 11,
        'font.family': 'sans-serif',
        'text.color': text_color,
        
        # Legend
        'legend.frameon': False,
        'legend.fancybox': False,
        
        # Ticks
        'xtick.color': text_color,
        'ytick.color': text_color,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
    })

def apply_shadcn_dark_theme():
    """Apply shadcn-inspired dark theme to matplotlib"""
    plt.style.use('default')
    
    # Colors for dark mode
    primary_color = '#6e14b4'
    background_color = '#2d2d2f'
    text_color = '#e0d9ff'
    border_color = '#555555'
    
    plt.rcParams.update({
        'figure.facecolor': background_color,
        'figure.edgecolor': 'none',
        'axes.facecolor': background_color,
        'axes.edgecolor': border_color,
        'axes.linewidth': 1,
        'axes.grid': True,
        'axes.grid.axis': 'y',
        'axes.labelcolor': text_color,
        'axes.prop_cycle': plt.cycler('color', [primary_color]),
        'grid.color': border_color,
        'grid.linestyle': '-',
        'grid.linewidth': 0.5,
        'grid.alpha': 0.3,
        'lines.linewidth': 2.5,
        'lines.solid_capstyle': 'round',
        'font.size': 11,
        'font.family': 'sans-serif',
        'text.color': text_color,
        'legend.frameon': False,
        'legend.fancybox': False,
        'xtick.color': text_color,
        'ytick.color': text_color,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
    })
