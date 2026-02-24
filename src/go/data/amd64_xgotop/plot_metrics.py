#!/usr/bin/env python3
"""
Neobrutalistic metric visualization script
Generates plots from multiple metric JSON files with bold, geometric styling
"""

import json
import argparse
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.gridspec as gridspec
import numpy as np
from pathlib import Path
import sys

# Neobrutalistic color palettes
PALETTES = {
    'vibrant': {
        'primary': '#FF006E',      # Hot pink
        'secondary': '#FB5607',    # Orange
        'tertiary': '#FFBE0B',     # Yellow
        'quaternary': '#8338EC',   # Purple
        'quinary': '#3A86FF',      # Blue
        'senary': '#06FFB4',       # Mint green
        'septenary': '#FF1744',    # Red
        'octonary': '#00E676',     # Green
        'nonary': '#651FFF',       # Deep purple
        'denary': '#00BCD4',       # Cyan
        'color11': '#FF6F00',      # Amber
        'color12': '#1DE9B6',      # Teal
        'color13': '#F50057',      # Pink accent
        'color14': '#76FF03',      # Light green
        'color15': '#536DFE',      # Indigo
        'color16': '#FF3D00',      # Deep orange
        'color17': '#00B0FF',      # Light blue
        'color18': '#C6FF00',      # Lime
        'color19': '#AA00FF',      # Purple accent
        'color20': '#00C853',      # Green accent
        'background': '#F3F3F3',   # Light gray
        'text': '#000000',         # Black
        'border': '#000000'        # Black borders
    },
    'cyberpunk': {
        'primary': '#FF0080',      # Neon pink
        'secondary': '#00FF88',    # Neon green
        'tertiary': '#00E5FF',     # Cyan
        'quaternary': '#FFD700',   # Gold
        'quinary': '#FF00FF',      # Magenta
        'background': '#0A0A0A',   # Near black
        'text': '#FFFFFF',         # White
        'border': '#FF0080'        # Neon pink borders
    },
    'brutalist': {
        'primary': '#D32F2F',      # Red
        'secondary': '#388E3C',    # Green
        'tertiary': '#1976D2',     # Blue
        'quaternary': '#FBC02D',   # Yellow
        'quinary': '#7B1FA2',      # Purple
        'background': '#ECEFF1',   # Light gray
        'text': '#212121',         # Dark gray
        'border': '#212121'        # Dark gray borders
    }
}

# Default colors
COLORS = PALETTES['vibrant']

LINESTYLES = [
    dot + line 
    for dot in ('.', 'o', '^', 'v', '+', 'x')
    for line in ('-', '--', '-.', ':')
]

def load_metrics(json_path):
    """Load metrics from JSON file"""
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

def get_time_values(data_length, interval_ms=1000):
    """Convert sample indices to time in seconds based on the stats interval"""
    # Assuming samples are taken at regular intervals (default 1000ms from xgotop)
    return np.arange(data_length) * (interval_ms / 1000.0)

def add_line_label(ax, x_values, y_values, label, color, fontsize=8, offset_factor=0.5):
    """Add a label directly on the line at its midpoint"""
    # Find a good position for the label (middle of the line)
    mid_idx = len(x_values) // 2

    # Try to find a relatively flat region near the middle
    window = min(10, len(x_values) // 4)
    start_idx = max(0, mid_idx - window)
    end_idx = min(len(x_values) - 1, mid_idx + window)

    if start_idx < end_idx:
        # Find the index with minimum local variation
        min_var = float('inf')
        best_idx = mid_idx
        for i in range(start_idx, end_idx):
            if i > 0 and i < len(y_values) - 1:
                local_var = abs(y_values[i+1] - y_values[i-1])
                if local_var < min_var:
                    min_var = local_var
                    best_idx = i
    else:
        best_idx = mid_idx

    # Get position
    x_pos = x_values[best_idx]
    y_pos = y_values[best_idx]

    # Calculate angle of the line at this point
    if best_idx > 0 and best_idx < len(x_values) - 1:
        dx = x_values[best_idx + 1] - x_values[best_idx - 1]
        dy = y_values[best_idx + 1] - y_values[best_idx - 1]
        angle = np.arctan2(dy, dx) * 180 / np.pi

        # Normalize angle to [-90, 90]
        if angle > 90:
            angle = angle - 180
        elif angle < -90:
            angle = angle + 180
    else:
        angle = 0

    # Add background box for better readability
    bbox_props = dict(boxstyle="round,pad=0.3", facecolor='white',
                     edgecolor=color, linewidth=1.5, alpha=0.9)

    # Add the label
    ax.text(x_pos, y_pos, label, fontsize=fontsize, color=color,
           ha='center', va='center', rotation=angle,
           bbox=bbox_props, weight='bold', zorder=1000)

def setup_neobrutalistic_style():
    """Configure matplotlib for neobrutalistic aesthetic"""
    plt.rcParams.update({
        'font.family': 'monospace',
        'font.weight': 'bold',
        'font.size': 12,
        'axes.linewidth': 4,
        'axes.edgecolor': COLORS['border'],
        'axes.facecolor': COLORS['background'],
        'figure.facecolor': COLORS['background'],
        'lines.linewidth': 3,
        'xtick.major.width': 3,
        'ytick.major.width': 3,
        'xtick.major.size': 8,
        'ytick.major.size': 8,
        'axes.grid': False,
    })

def create_rps_pps_comparison(metrics_data, labels, output_path, palette_name='vibrant'):
    """Create RPS vs PPS comparison plots with area between them"""
    global COLORS
    COLORS = PALETTES.get(palette_name, PALETTES['vibrant'])
    setup_neobrutalistic_style()
    
    # Create figure with subplots (one per dataset)
    n_datasets = len(metrics_data)
    # Special handling for single dataset - use 2x1 layout
    if n_datasets == 1:
        fig = plt.figure(figsize=(12, 12))
        n_rows = 2
    else:
        fig = plt.figure(figsize=(12, 6 * n_datasets))
        n_rows = n_datasets
    
    # Add a bold title with shadow effect
    fig.suptitle('RPS vs PPS COMPARISON', 
                 fontsize=36, weight='black', y=0.98, color=COLORS['text'])
    
    # Create subplot for each dataset
    for idx, (data, label) in enumerate(zip(metrics_data, labels)):
        ax = plt.subplot(n_rows, 1, idx + 1)
        
        if 'rps' in data and 'pps' in data:
            # Create x-axis values
            x_values = np.arange(len(data['rps']))
            
            # Get RPS and PPS data
            rps_data = np.array(data['rps'])
            pps_data = np.array(data['pps'])
            
            # Add shadows
            shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
            shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
            x_offset = len(x_values) * 0.003
            y_offset_rps = (max(rps_data) - min(rps_data)) * 0.01
            y_offset_pps = (max(pps_data) - min(pps_data)) * 0.01
            
            # Plot shadows
            ax.plot(x_values + x_offset, rps_data - y_offset_rps,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)
            ax.plot(x_values + x_offset, pps_data - y_offset_pps,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)
            
            # Plot RPS and PPS
            rps_line = ax.plot(x_values, rps_data, 
                              color=COLORS['primary'], linewidth=4, 
                              label='RPS (Reads)', zorder=3)
            pps_line = ax.plot(x_values, pps_data, 
                              color=COLORS['secondary'], linewidth=4, 
                              label='PPS (Processed)', zorder=3)
            
            # Fill area between RPS and PPS
            ax.fill_between(x_values, rps_data, pps_data, 
                           alpha=0.3, color=COLORS['tertiary'], 
                           label='Read-Process Gap', zorder=2)
            
            # Styling
            ax.set_title(f'{label} - RPS vs PPS', 
                        fontsize=20, weight='black', pad=20, color=COLORS['text'])
            ax.set_xlabel('SAMPLE', fontsize=14, weight='bold', color=COLORS['text'])
            ax.set_ylabel('OPERATIONS/SEC', fontsize=14, weight='bold', color=COLORS['text'])
            ax.tick_params(colors=COLORS['text'], which='both')
            
            # Add grid for better readability
            ax.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')
            
            # Legend
            legend = ax.legend(loc='upper right', frameon=True, 
                             fancybox=False, shadow=False,
                             edgecolor=COLORS['border'], 
                             facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                             prop={'weight': 'bold', 'size': 12})
            legend.get_frame().set_linewidth(3)
            
            # Set legend text color
            for text in legend.get_texts():
                text.set_color('black' if palette_name != 'cyberpunk' else 'white')
            
            # Add decorative corner brackets
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            bracket_size = 0.03
            
            # Top-left corner bracket
            ax.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size], 
                   [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
            ax.plot([xlim[0], xlim[0]], 
                   [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size], 
                   color=COLORS['border'], linewidth=6)
            
            # Bottom-right corner bracket
            ax.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]], 
                   [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
            ax.plot([xlim[1], xlim[1]], 
                   [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size], 
                   color=COLORS['border'], linewidth=6)
            
            # Make spines thicker
            for spine in ax.spines.values():
                spine.set_linewidth(4)
    
    # If single dataset, add summary statistics in second subplot
    if n_datasets == 1 and len(metrics_data) > 0:
        ax2 = plt.subplot(2, 1, 2)
        data = metrics_data[0]
        
        if 'rps' in data and 'pps' in data:
            rps_data = np.array(data['rps'])
            pps_data = np.array(data['pps'])
            
            # Calculate statistics
            avg_rps = np.mean(rps_data)
            avg_pps = np.mean(pps_data)
            max_rps = np.max(rps_data)
            max_pps = np.max(pps_data)
            min_rps = np.min(rps_data)
            min_pps = np.min(pps_data)
            avg_gap = np.mean(rps_data - pps_data)
            
            # Clear axis
            ax2.clear()
            ax2.set_xlim(0, 10)
            ax2.set_ylim(0, 10)
            ax2.axis('off')
            
            # Create neobrutalistic info boxes
            box_width = 4
            box_height = 1.5
            
            # Title box
            title_rect = patches.Rectangle((1, 8), 8, 1.5, 
                                         facecolor=COLORS['primary'], 
                                         edgecolor=COLORS['border'],
                                         linewidth=4)
            ax2.add_patch(title_rect)
            ax2.text(5, 8.75, 'PERFORMANCE SUMMARY', 
                    ha='center', va='center', fontsize=20, 
                    weight='black', color='white')
            
            # RPS Stats box
            rps_rect = patches.Rectangle((0.5, 5.5), box_width, box_height,
                                       facecolor=COLORS['secondary'],
                                       edgecolor=COLORS['border'],
                                       linewidth=3)
            ax2.add_patch(rps_rect)
            ax2.text(2.5, 6.8, 'RPS STATS', ha='center', va='center',
                    fontsize=14, weight='black', color='white')
            ax2.text(2.5, 6.2, f'AVG: {avg_rps:.2f}', ha='center', va='center',
                    fontsize=12, weight='bold', color='white')
            ax2.text(2.5, 5.8, f'MIN: {min_rps:.2f} | MAX: {max_rps:.2f}', 
                    ha='center', va='center', fontsize=10, weight='bold', color='white')
            
            # PPS Stats box
            pps_rect = patches.Rectangle((5.5, 5.5), box_width, box_height,
                                       facecolor=COLORS['tertiary'],
                                       edgecolor=COLORS['border'],
                                       linewidth=3)
            ax2.add_patch(pps_rect)
            ax2.text(7.5, 6.8, 'PPS STATS', ha='center', va='center',
                    fontsize=14, weight='black', color=COLORS['border'])
            ax2.text(7.5, 6.2, f'AVG: {avg_pps:.2f}', ha='center', va='center',
                    fontsize=12, weight='bold', color=COLORS['border'])
            ax2.text(7.5, 5.8, f'MIN: {min_pps:.2f} | MAX: {max_pps:.2f}', 
                    ha='center', va='center', fontsize=10, weight='bold', color=COLORS['border'])
            
            # Gap Analysis box
            gap_rect = patches.Rectangle((2, 3), 6, box_height,
                                       facecolor=COLORS['quaternary'],
                                       edgecolor=COLORS['border'],
                                       linewidth=3)
            ax2.add_patch(gap_rect)
            ax2.text(5, 4.3, 'READ-PROCESS GAP', ha='center', va='center',
                    fontsize=14, weight='black', color=COLORS['border'])
            ax2.text(5, 3.5, f'AVERAGE GAP: {avg_gap:.2f} ops/sec', 
                    ha='center', va='center', fontsize=12, weight='bold', color=COLORS['border'])
            
            # Add decorative elements
            # Shadow effects
            shadow_offset = 0.1
            for rect in [title_rect, rps_rect, pps_rect, gap_rect]:
                shadow = patches.Rectangle((rect.get_x() + shadow_offset, 
                                          rect.get_y() - shadow_offset),
                                         rect.get_width(), rect.get_height(),
                                         facecolor='black', alpha=0.3, zorder=0)
                ax2.add_patch(shadow)
    
    # Adjust layout
    plt.tight_layout()
    
    # Add decorative border around entire figure
    border_ax = fig.add_subplot(111, frameon=False)
    border_ax.tick_params(labelcolor='none', top=False, bottom=False, 
                         left=False, right=False)
    for spine in border_ax.spines.values():
        spine.set_linewidth(8)
        spine.set_edgecolor(COLORS['border'])
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor=COLORS['background'], edgecolor=COLORS['border'])
    print(f"Plot saved to: {output_path}")


def create_individual_file_plot(data, label, output_path, palette_name='vibrant'):
    """Create a plot for a single metrics file with RPS vs PPS, event counts, and other metrics"""
    global COLORS
    COLORS = PALETTES.get(palette_name, PALETTES['vibrant'])
    setup_neobrutalistic_style()

    # Check what data we have
    has_event_counts = 'event_counts' in data
    has_ewp = 'ewp' in data
    has_lat = 'lat' in data
    has_prc = 'prc' in data
    has_bps = 'bps' in data
    has_bfl = 'bfl' in data
    has_qwl = 'qwl' in data

    # Determine layout based on available data
    # Row 1: RPS vs PPS and Event Counts (if available)
    # Row 2: EWP, Latency, Processing Time (if available)
    # Row 3: BPS, BFL, QWL (if available)
    n_rows = 3 if any([has_bps, has_bfl, has_qwl]) else 2

    # For top row: max 2 columns (RPS/PPS and Event Counts)
    top_row_cols = 2 if has_event_counts else 1
    # For middle row: count of available metrics
    middle_row_cols = sum([has_ewp, has_lat, has_prc])
    # For bottom row: count of available batch/queue metrics
    bottom_row_cols = sum([has_bps, has_bfl, has_qwl])
    n_cols = max(top_row_cols, middle_row_cols, bottom_row_cols)

    # Better figure size to prevent squished plots - double the width
    fig_width = 12 * n_cols  # 12 inches per column for much wider plots
    fig_height = 6 * n_rows  # 6 inches per row
    fig = plt.figure(figsize=(fig_width, fig_height))

    # Add a bold title with shadow effect - moved higher up
    fig.suptitle(f'{label} - COMPLETE PERFORMANCE METRICS',
                 fontsize=20, weight='black', y=0.98, color=COLORS['text'])

    # Create GridSpec for better control with more top margin to avoid title collision
    gs = gridspec.GridSpec(n_rows, n_cols, figure=fig, hspace=0.35, wspace=0.15, top=0.88, bottom=0.05)

    # Plot 1: RPS vs PPS (top left)
    if n_cols > top_row_cols and top_row_cols == 1:
        # If bottom row has more columns, span RPS/PPS across multiple columns
        ax1 = fig.add_subplot(gs[0, :])
    else:
        ax1 = fig.add_subplot(gs[0, 0])

    if 'rps' in data and 'pps' in data:
        # Create x-axis values in seconds
        x_values = get_time_values(len(data['rps']))

        # Get RPS and PPS data
        rps_data = np.array(data['rps'])
        pps_data = np.array(data['pps'])

        # Add shadows
        shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
        shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
        x_offset = len(x_values) * 0.003
        y_offset_rps = (max(rps_data) - min(rps_data)) * 0.01 if len(rps_data) > 0 else 0
        y_offset_pps = (max(pps_data) - min(pps_data)) * 0.01 if len(pps_data) > 0 else 0

        # Plot shadows
        ax1.plot(x_values + x_offset, rps_data - y_offset_rps,
               color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)
        ax1.plot(x_values + x_offset, pps_data - y_offset_pps,
               color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)

        # Plot RPS and PPS
        ax1.plot(x_values, rps_data,
               color=COLORS['primary'], linewidth=4,
               label='RPS (Reads)', zorder=3)
        ax1.plot(x_values, pps_data,
               color=COLORS['secondary'], linewidth=4,
               label='PPS (Processed)', zorder=3)

        # Fill area between RPS and PPS
        ax1.fill_between(x_values, rps_data, pps_data,
                       alpha=0.3, color=COLORS['tertiary'],
                       label='Read-Process Gap', zorder=2)

        # Styling
        ax1.set_title('RPS vs PPS',
                    fontsize=14, weight='black', pad=10, color=COLORS['text'])
        ax1.set_xlabel('TIME (seconds)', fontsize=10, weight='bold', color=COLORS['text'])
        ax1.set_ylabel('OPERATIONS/SEC', fontsize=10, weight='bold', color=COLORS['text'])
        ax1.tick_params(colors=COLORS['text'], which='both')
        ax1.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

        # Legend
        legend = ax1.legend(loc='upper right', frameon=True,
                         fancybox=False, shadow=False,
                         edgecolor=COLORS['border'],
                         facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                         prop={'weight': 'bold', 'size': 11})
        legend.get_frame().set_linewidth(3)

        # Set legend text color
        for text in legend.get_texts():
            text.set_color('black' if palette_name != 'cyberpunk' else 'white')

        # Add decorative corner brackets
        xlim = ax1.get_xlim()
        ylim = ax1.get_ylim()
        bracket_size = 0.03

        # Top-left corner bracket
        ax1.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size],
               [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
        ax1.plot([xlim[0], xlim[0]],
               [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size],
               color=COLORS['border'], linewidth=6)

        # Bottom-right corner bracket
        ax1.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]],
               [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
        ax1.plot([xlim[1], xlim[1]],
               [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size],
               color=COLORS['border'], linewidth=6)

        # Make spines thicker
        for spine in ax1.spines.values():
            spine.set_linewidth(4)

    # Plot 2: Event Counts (if available, top right)
    if has_event_counts:
        if n_cols > top_row_cols:
            # If bottom row has more columns, don't use full grid
            ax2 = fig.add_subplot(gs[0, 1])
        else:
            ax2 = fig.add_subplot(gs[0, 1])
        event_counts = data['event_counts']

        if event_counts:
            # Event type mapping from main.go
            event_name_map = {
                '0': 'casGStatus',
                '1': 'makeSlice',
                '2': 'makeMap',
                '3': 'newObject',
                '4': 'newGoroutine',
                '5': 'goExit'
            }

            # Extract keys and values, converting to proper types
            event_types = []
            counts = []
            for k, v in sorted(event_counts.items(), key=lambda x: int(x[0])):
                event_name = event_name_map.get(str(k), f"Type {k}")
                event_types.append(event_name)
                counts.append(v)

            # Cycle through colors
            color_list = [COLORS['primary'], COLORS['secondary'], COLORS['tertiary'],
                         COLORS['quaternary'], COLORS['quinary'], COLORS.get('senary', '#06FFB4'),
                         COLORS.get('septenary', '#FF1744'), COLORS.get('octonary', '#00E676'),
                         COLORS.get('nonary', '#651FFF'), COLORS.get('denary', '#00BCD4')]
            pie_colors = [color_list[i % len(color_list)] for i in range(len(event_types))]

            # Calculate explode values - slightly separate each slice for 3D effect
            explode = [0.05] * len(counts)  # Explode all slices slightly

            # Find the largest slice and explode it more
            max_idx = counts.index(max(counts))
            explode[max_idx] = 0.1

            # Create the pie chart with 3D-like appearance
            wedges, texts, autotexts = ax2.pie(counts, labels=event_types, colors=pie_colors,
                                                autopct='%1.1f%%', startangle=45,
                                                shadow=True, explode=explode,
                                                labeldistance=1.15, pctdistance=0.85,
                                                textprops={'weight': 'bold', 'size': 10},
                                                wedgeprops={'linewidth': 3, 'edgecolor': COLORS['border']})

            # Make percentage text bold with contrasting colors
            for i, autotext in enumerate(autotexts):
                autotext.set_color('white')
                autotext.set_weight('black')
                autotext.set_fontsize(10)
                # Add a background for better readability
                autotext.set_bbox(dict(boxstyle='round,pad=0.3',
                                      facecolor=pie_colors[i % len(pie_colors)],
                                      alpha=0.8, edgecolor='none'))

            # Style the labels
            for text in texts:
                text.set_fontsize(11)
                text.set_weight('bold')
                text.set_color(COLORS['text'])

            # Add decorative depth effect by drawing shadow wedges
            for wedge in wedges:
                wedge.set_linewidth(3)
                wedge.set_edgecolor(COLORS['border'])
                # Create gradient-like effect with alpha
                wedge.set_alpha(0.9)

            # Title with shadow effect
            ax2.set_title('EVENT TYPE DISTRIBUTION',
                        fontsize=14, weight='black', pad=10, color=COLORS['text'])

            # Equal aspect ratio ensures circular pie
            ax2.axis('equal')

            # Add a detailed legend with counts and percentages
            total_count = sum(counts)
            legend_labels = [f'{et}: {c:,} ({c/total_count*100:.1f}%)'
                            for et, c in zip(event_types, counts)]
            legend = ax2.legend(legend_labels, loc='center left', bbox_to_anchor=(1.05, 0.5),
                              frameon=True, fancybox=False, shadow=True,
                              edgecolor=COLORS['border'],
                              facecolor='white' if palette_name != 'cyberpunk' else COLORS['background'],
                              prop={'weight': 'bold', 'size': 9})
            legend.get_frame().set_linewidth(3)

            # Add total count annotation
            ax2.text(0.5, -1.3, f'Total Events: {total_count:,}',
                    transform=ax2.transAxes,
                    fontsize=12, weight='bold', ha='center',
                    bbox=dict(boxstyle='round,pad=0.5',
                             facecolor=COLORS['tertiary'],
                             edgecolor=COLORS['border'],
                             linewidth=2))

    # Bottom row: Additional metrics
    bottom_plot_idx = 0  # Start from the first position in second row

    # Plot EWP (Events Waiting to be Processed)
    if has_ewp:
        ax_ewp = fig.add_subplot(gs[1, bottom_plot_idx])
        bottom_plot_idx += 1

        x_values = get_time_values(len(data['ewp']))
        ewp_values = np.array(data['ewp'])

        # Add shadows for individual plot
        shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
        shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
        x_offset = len(x_values) * 0.003
        y_offset_ewp = (max(ewp_values) - min(ewp_values)) * 0.01 if len(ewp_values) > 0 else 0

        # Plot shadow
        ax_ewp.plot(x_values + x_offset, ewp_values - y_offset_ewp,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)

        # Main plot
        ax_ewp.plot(x_values, ewp_values,
                   color=COLORS['quaternary'], linewidth=4, zorder=2)

        # Fill under the curve for visual appeal
        ax_ewp.fill_between(x_values, 0, ewp_values,
                           alpha=0.3, color=COLORS['quaternary'], zorder=1)

        ax_ewp.set_title('EVENTS WAITING TO BE PROCESSED',
                        fontsize=14, weight='black', pad=10, color=COLORS['text'])
        ax_ewp.set_xlabel('TIME (seconds)', fontsize=10, weight='bold', color=COLORS['text'])
        ax_ewp.set_ylabel('COUNT', fontsize=10, weight='bold', color=COLORS['text'])
        ax_ewp.tick_params(colors=COLORS['text'], which='both')
        ax_ewp.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

        # Add stats annotation
        avg_ewp = np.mean(ewp_values)
        max_ewp = np.max(ewp_values)
        ax_ewp.text(0.02, 0.98, f'AVG: {avg_ewp:.1f}\nMAX: {max_ewp:.1f}',
                   transform=ax_ewp.transAxes,
                   fontsize=10, weight='bold',
                   verticalalignment='top',
                   bbox=dict(boxstyle='round,pad=0.5',
                            facecolor='white', alpha=0.8,
                            edgecolor=COLORS['quaternary'], linewidth=2))

        # Add corner brackets
        xlim = ax_ewp.get_xlim()
        ylim = ax_ewp.get_ylim()
        bracket_size = 0.03
        ax_ewp.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size],
                   [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
        ax_ewp.plot([xlim[0], xlim[0]],
                   [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size],
                   color=COLORS['border'], linewidth=6)
        ax_ewp.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]],
                   [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
        ax_ewp.plot([xlim[1], xlim[1]],
                   [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size],
                   color=COLORS['border'], linewidth=6)

        for spine in ax_ewp.spines.values():
            spine.set_linewidth(4)

    # Plot Latency
    if has_lat:
        ax_lat = fig.add_subplot(gs[1, bottom_plot_idx])
        bottom_plot_idx += 1

        x_values = get_time_values(len(data['lat']))
        # Values are already in nanoseconds
        lat_values = np.array(data['lat'])

        # Add shadows for individual plot
        shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
        shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
        x_offset = len(x_values) * 0.003
        y_offset_lat = (max(lat_values) - min(lat_values)) * 0.01 if len(lat_values) > 0 else 0

        # Plot shadow
        ax_lat.plot(x_values + x_offset, lat_values - y_offset_lat,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)

        # Main plot
        ax_lat.plot(x_values, lat_values,
                   color=COLORS.get('septenary', '#FF1744'), linewidth=4, zorder=2)

        # Fill under the curve
        ax_lat.fill_between(x_values, 0, lat_values,
                           alpha=0.3, color=COLORS.get('septenary', '#FF1744'), zorder=1)

        ax_lat.set_title('AVG eBPF HOOK LATENCY (ns)',
                        fontsize=14, weight='black', pad=10, color=COLORS['text'])
        ax_lat.set_xlabel('TIME (seconds)', fontsize=10, weight='bold', color=COLORS['text'])
        ax_lat.set_ylabel('NANOSECONDS', fontsize=10, weight='bold', color=COLORS['text'])
        ax_lat.tick_params(colors=COLORS['text'], which='both')
        ax_lat.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

        # Add stats annotation
        avg_lat = np.mean(lat_values)
        max_lat = np.max(lat_values)
        min_lat = np.min(lat_values)
        ax_lat.text(0.02, 0.98, f'AVG: {avg_lat:.1f} ns\nMIN: {min_lat:.1f} ns\nMAX: {max_lat:.1f} ns',
                   transform=ax_lat.transAxes,
                   fontsize=10, weight='bold',
                   verticalalignment='top',
                   bbox=dict(boxstyle='round,pad=0.5',
                            facecolor='white', alpha=0.8,
                            edgecolor=COLORS.get('septenary', '#FF1744'), linewidth=2))

        # Add corner brackets
        xlim = ax_lat.get_xlim()
        ylim = ax_lat.get_ylim()
        bracket_size = 0.03
        ax_lat.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size],
                   [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
        ax_lat.plot([xlim[0], xlim[0]],
                   [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size],
                   color=COLORS['border'], linewidth=6)
        ax_lat.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]],
                   [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
        ax_lat.plot([xlim[1], xlim[1]],
                   [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size],
                   color=COLORS['border'], linewidth=6)

        for spine in ax_lat.spines.values():
            spine.set_linewidth(4)

    # Plot Processing Time
    if has_prc:
        ax_prc = fig.add_subplot(gs[1, bottom_plot_idx])

        x_values = get_time_values(len(data['prc']))
        prc_values = np.array(data['prc'])

        # Add shadows for individual plot
        shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
        shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
        x_offset = len(x_values) * 0.003
        y_offset_prc = (max(prc_values) - min(prc_values)) * 0.01 if len(prc_values) > 0 else 0

        # Plot shadow
        ax_prc.plot(x_values + x_offset, prc_values - y_offset_prc,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)

        # Main plot
        ax_prc.plot(x_values, prc_values,
                   color=COLORS.get('octonary', '#00E676'), linewidth=4, zorder=2)

        # Fill under the curve
        ax_prc.fill_between(x_values, 0, prc_values,
                           alpha=0.3, color=COLORS.get('octonary', '#00E676'), zorder=1)

        ax_prc.set_title('PROCESSING TIME (ns/event)',
                        fontsize=14, weight='black', pad=10, color=COLORS['text'])
        ax_prc.set_xlabel('TIME (seconds)', fontsize=10, weight='bold', color=COLORS['text'])
        ax_prc.set_ylabel('NANOSECONDS', fontsize=10, weight='bold', color=COLORS['text'])
        ax_prc.tick_params(colors=COLORS['text'], which='both')
        ax_prc.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

        # Add stats annotation
        avg_prc = np.mean(prc_values)
        max_prc = np.max(prc_values)
        min_prc = np.min(prc_values)
        ax_prc.text(0.02, 0.98, f'AVG: {avg_prc:.1f} ns\nMIN: {min_prc:.1f} ns\nMAX: {max_prc:.1f} ns',
                   transform=ax_prc.transAxes,
                   fontsize=10, weight='bold',
                   verticalalignment='top',
                   bbox=dict(boxstyle='round,pad=0.5',
                            facecolor='white', alpha=0.8,
                            edgecolor=COLORS.get('octonary', '#00E676'), linewidth=2))

        # Add corner brackets
        xlim = ax_prc.get_xlim()
        ylim = ax_prc.get_ylim()
        bracket_size = 0.03
        ax_prc.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size],
                   [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
        ax_prc.plot([xlim[0], xlim[0]],
                   [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size],
                   color=COLORS['border'], linewidth=6)
        ax_prc.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]],
                   [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
        ax_prc.plot([xlim[1], xlim[1]],
                   [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size],
                   color=COLORS['border'], linewidth=6)

        for spine in ax_prc.spines.values():
            spine.set_linewidth(4)

    # Plot Batch Metrics (Row 3) - only if we have batch metrics
    if n_rows > 2:
        batch_plot_idx = 0


        # Plot BPS (Batches Per Second)
        if has_bps:
            ax_bps = fig.add_subplot(gs[2, batch_plot_idx])
            batch_plot_idx += 1

            x_values = get_time_values(len(data['bps']))
            bps_values = np.array(data['bps'])

            # Add shadows for individual plot
            shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
            shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
            x_offset = len(x_values) * 0.003
            y_offset_bps = (max(bps_values) - min(bps_values)) * 0.01 if len(bps_values) > 0 else 0

            # Plot shadow
            ax_bps.plot(x_values + x_offset, bps_values - y_offset_bps,
                       color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)

            # Main plot
            ax_bps.plot(x_values, bps_values,
                       color=COLORS.get('secondary', '#4ECDC4'), linewidth=4, zorder=2)

            # Fill under the curve
            ax_bps.fill_between(x_values, 0, bps_values,
                               alpha=0.3, color=COLORS.get('secondary', '#4ECDC4'), zorder=1)

            ax_bps.set_title('BATCHES PER SECOND',
                            fontsize=14, weight='black', pad=10, color=COLORS['text'])
            ax_bps.set_xlabel('TIME (seconds)', fontsize=10, weight='bold', color=COLORS['text'])
            ax_bps.set_ylabel('BATCHES/SEC', fontsize=10, weight='bold', color=COLORS['text'])
            ax_bps.tick_params(colors=COLORS['text'], which='both')
            ax_bps.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

            # Add stats annotation
            avg_bps = np.mean(bps_values)
            max_bps = np.max(bps_values)
            min_bps = np.min(bps_values)
            ax_bps.text(0.02, 0.98, f'AVG: {avg_bps:.2f}/s\nMIN: {min_bps:.2f}/s\nMAX: {max_bps:.2f}/s',
                       transform=ax_bps.transAxes,
                       fontsize=10, weight='bold',
                       verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.5',
                                facecolor='white', alpha=0.8,
                                edgecolor=COLORS.get('secondary', '#4ECDC4'), linewidth=2))

            for spine in ax_bps.spines.values():
                spine.set_linewidth(4)

        # Plot BFL (Batch Flush Latency)
        if has_bfl:
            ax_bfl = fig.add_subplot(gs[2, batch_plot_idx])
            batch_plot_idx += 1

            x_values = get_time_values(len(data['bfl']))
            bfl_values = np.array(data['bfl']) / 1e6  # Convert nanoseconds to milliseconds

            # Add shadows for individual plot
            shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
            shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
            x_offset = len(x_values) * 0.003
            y_offset_bfl = (max(bfl_values) - min(bfl_values)) * 0.01 if len(bfl_values) > 0 else 0

            # Plot shadow
            ax_bfl.plot(x_values + x_offset, bfl_values - y_offset_bfl,
                       color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)

            # Main plot
            ax_bfl.plot(x_values, bfl_values,
                       color=COLORS.get('tertiary', '#FFD93D'), linewidth=4, zorder=2)

            # Fill under the curve
            ax_bfl.fill_between(x_values, 0, bfl_values,
                               alpha=0.3, color=COLORS.get('tertiary', '#FFD93D'), zorder=1)

            ax_bfl.set_title('BATCH FLUSH LATENCY (ms/batch)',
                            fontsize=14, weight='black', pad=10, color=COLORS['text'])
            ax_bfl.set_xlabel('TIME (seconds)', fontsize=10, weight='bold', color=COLORS['text'])
            ax_bfl.set_ylabel('MILLISECONDS', fontsize=10, weight='bold', color=COLORS['text'])
            ax_bfl.tick_params(colors=COLORS['text'], which='both')
            ax_bfl.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

            # Add stats annotation
            avg_bfl = np.mean(bfl_values)
            max_bfl = np.max(bfl_values)
            min_bfl = np.min(bfl_values)
            ax_bfl.text(0.02, 0.98, f'AVG: {avg_bfl:.3f} ms\nMIN: {min_bfl:.3f} ms\nMAX: {max_bfl:.3f} ms',
                       transform=ax_bfl.transAxes,
                       fontsize=10, weight='bold',
                       verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.5',
                                facecolor='white', alpha=0.8,
                                edgecolor=COLORS.get('tertiary', '#FFD93D'), linewidth=2))

            for spine in ax_bfl.spines.values():
                spine.set_linewidth(4)

        # Plot QWL (Queue Wait Latency)
        if has_qwl:
            ax_qwl = fig.add_subplot(gs[2, batch_plot_idx])

            x_values = get_time_values(len(data['qwl']))
            qwl_values = np.array(data['qwl']) / 1e6  # Convert nanoseconds to milliseconds

            # Add shadows for individual plot
            shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
            shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
            x_offset = len(x_values) * 0.003
            y_offset_qwl = (max(qwl_values) - min(qwl_values)) * 0.01 if len(qwl_values) > 0 else 0

            # Plot shadow
            ax_qwl.plot(x_values + x_offset, qwl_values - y_offset_qwl,
                       color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)

            # Main plot
            ax_qwl.plot(x_values, qwl_values,
                       color=COLORS.get('error', '#FF4444'), linewidth=4, zorder=2)

            # Fill under the curve
            ax_qwl.fill_between(x_values, 0, qwl_values,
                               alpha=0.3, color=COLORS.get('error', '#FF4444'), zorder=1)

            ax_qwl.set_title('QUEUE WAIT LATENCY (ms/event)',
                            fontsize=14, weight='black', pad=10, color=COLORS['text'])
            ax_qwl.set_xlabel('TIME (seconds)', fontsize=10, weight='bold', color=COLORS['text'])
            ax_qwl.set_ylabel('MILLISECONDS', fontsize=10, weight='bold', color=COLORS['text'])
            ax_qwl.tick_params(colors=COLORS['text'], which='both')
            ax_qwl.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

            # Add stats annotation
            avg_qwl = np.mean(qwl_values)
            max_qwl = np.max(qwl_values)
            min_qwl = np.min(qwl_values)
            ax_qwl.text(0.02, 0.98, f'AVG: {avg_qwl:.3f} ms\nMIN: {min_qwl:.3f} ms\nMAX: {max_qwl:.3f} ms',
                       transform=ax_qwl.transAxes,
                       fontsize=10, weight='bold',
                       verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.5',
                                facecolor='white', alpha=0.8,
                                edgecolor=COLORS.get('error', '#FF4444'), linewidth=2))

            for spine in ax_qwl.spines.values():
                spine.set_linewidth(4)

    # GridSpec handles all layout now, no need for additional adjustment

    # Add decorative border around entire figure
    border_ax = fig.add_subplot(111, frameon=False)
    border_ax.tick_params(labelcolor='none', top=False, bottom=False,
                         left=False, right=False)
    for spine in border_ax.spines.values():
        spine.set_linewidth(8)
        spine.set_edgecolor(COLORS['border'])

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor=COLORS['background'], edgecolor=COLORS['border'])
    print(f"Individual plot saved to: {output_path}")
    plt.close(fig)  # Close figure to prevent memory issues


def create_aggregate_metrics_plot(metrics_data, labels, output_path, palette_name='vibrant'):
    """Create aggregate metrics plot with EWP, Latency, and Processing Time"""
    global COLORS
    COLORS = PALETTES.get(palette_name, PALETTES['vibrant'])
    setup_neobrutalistic_style()

    # Check which metrics are available
    has_ewp = any('ewp' in data for data in metrics_data)
    has_lat = any('lat' in data for data in metrics_data)
    has_prc = any('prc' in data for data in metrics_data)

    # Count available metrics
    n_metrics = sum([has_ewp, has_lat, has_prc])
    if n_metrics == 0:
        print("No aggregate metrics (EWP, Latency, Processing Time) found in data")
        return

    # Calculate appropriate figure height based on number of datasets
    n_datasets = len(metrics_data)
    # Increase height for many datasets to accommodate legend
    base_height = 10
    if n_datasets > 20:
        base_height = 14
    if n_datasets > 40:
        base_height = 18

    # Create figure with appropriate layout - triple width for better visibility
    fig = plt.figure(figsize=(30 * n_metrics, base_height))

    # Add a bold title with shadow effect
    fig.suptitle('AGGREGATE PERFORMANCE METRICS',
                 fontsize=32, weight='black', y=0.98, color=COLORS['text'])

    plot_idx = 1

    # Plot EWP if available
    if has_ewp:
        ax = plt.subplot(1, n_metrics, plot_idx)
        plot_idx += 1

        # Determine if we should use inline labels (when too many datasets)
        use_inline_labels = n_datasets > 15

        for i, (data, label) in enumerate(zip(metrics_data, labels)):
            if 'ewp' in data:
                color = list(COLORS.values())[i % len(COLORS)]
                linestyle = LINESTYLES[i % len(LINESTYLES)]
                x_values = np.arange(len(data['ewp']))
                ewp_values = np.array(data['ewp'])

                # Main plot (no shadow in aggregate)
                ax.plot(x_values, ewp_values, linestyle,
                       color=color, linewidth=4, label=label, zorder=2)

                # Add inline label if needed
                if use_inline_labels:
                    add_line_label(ax, x_values, ewp_values, label, color,
                                 fontsize=7 if n_datasets > 30 else 8)

        ax.set_title('EVENTS WAITING TO BE PROCESSED',
                    fontsize=18, weight='black', pad=20, color=COLORS['text'])
        ax.set_xlabel('SAMPLE', fontsize=14, weight='bold', color=COLORS['text'])
        ax.set_ylabel('COUNT', fontsize=14, weight='bold', color=COLORS['text'])
        ax.tick_params(colors=COLORS['text'], which='both')
        ax.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

        # Only show legend if not using inline labels
        if not use_inline_labels:
            # Legend with adaptive columns based on number of datasets
            n_cols = 1
            if n_datasets > 10:
                n_cols = 2
            if n_datasets > 20:
                n_cols = 3
            if n_datasets > 30:
                n_cols = 4
            if n_datasets > 40:
                n_cols = 5

            # Adjust font size for many datasets
            legend_fontsize = 10
            if n_datasets > 30:
                legend_fontsize = 8
            if n_datasets > 40:
                legend_fontsize = 7

            legend = ax.legend(loc='upper left', frameon=True,
                             fancybox=False, shadow=False,
                             edgecolor=COLORS['border'],
                             facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                             prop={'weight': 'bold', 'size': legend_fontsize},
                             ncol=n_cols,
                             bbox_to_anchor=(0.0, 0.98))
            legend.get_frame().set_linewidth(3)
            for text in legend.get_texts():
                text.set_color('black' if palette_name != 'cyberpunk' else 'white')

        # Add corner brackets
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        bracket_size = 0.05

        # Top-left corner bracket
        ax.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size],
               [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
        ax.plot([xlim[0], xlim[0]],
               [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)

        # Bottom-right corner bracket
        ax.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]],
               [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
        ax.plot([xlim[1], xlim[1]],
               [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)

        # Make spines thicker
        for spine in ax.spines.values():
            spine.set_linewidth(4)

    # Plot Latency if available
    if has_lat:
        ax = plt.subplot(1, n_metrics, plot_idx)
        plot_idx += 1

        for i, (data, label) in enumerate(zip(metrics_data, labels)):
            if 'lat' in data:
                color = list(COLORS.values())[i % len(COLORS)]
                linestyle = LINESTYLES[i % len(LINESTYLES)]
                x_values = np.arange(len(data['lat']))
                # Values are already in nanoseconds
                lat_values = np.array(data['lat'])

                # Main plot (no shadow in aggregate)
                ax.plot(x_values, lat_values, linestyle,
                       color=color, linewidth=4, label=label, zorder=2)

                # Add inline label if needed
                if use_inline_labels:
                    add_line_label(ax, x_values, lat_values, label, color,
                                 fontsize=7 if n_datasets > 30 else 8)

        ax.set_title('AVG eBPF HOOK LATENCY (ns)',
                    fontsize=18, weight='black', pad=20, color=COLORS['text'])
        ax.set_xlabel('SAMPLE', fontsize=14, weight='bold', color=COLORS['text'])
        ax.set_ylabel('NANOSECONDS', fontsize=14, weight='bold', color=COLORS['text'])
        ax.tick_params(colors=COLORS['text'], which='both')
        ax.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

        # Only show legend if not using inline labels
        if not use_inline_labels:
            # Legend with adaptive columns
            legend = ax.legend(loc='upper left', frameon=True,
                             fancybox=False, shadow=False,
                             edgecolor=COLORS['border'],
                             facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                             prop={'weight': 'bold', 'size': legend_fontsize},
                             ncol=n_cols,
                             bbox_to_anchor=(0.0, 0.98))
            legend.get_frame().set_linewidth(3)
            for text in legend.get_texts():
                text.set_color('black' if palette_name != 'cyberpunk' else 'white')

        # Add corner brackets
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        bracket_size = 0.05

        # Top-left corner bracket
        ax.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size],
               [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
        ax.plot([xlim[0], xlim[0]],
               [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)

        # Bottom-right corner bracket
        ax.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]],
               [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
        ax.plot([xlim[1], xlim[1]],
               [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)

        # Make spines thicker
        for spine in ax.spines.values():
            spine.set_linewidth(4)

    # Plot Processing Time if available
    if has_prc:
        ax = plt.subplot(1, n_metrics, plot_idx)

        for i, (data, label) in enumerate(zip(metrics_data, labels)):
            if 'prc' in data:
                color = list(COLORS.values())[i % len(COLORS)]
                linestyle = LINESTYLES[i % len(LINESTYLES)]
                x_values = np.arange(len(data['prc']))
                prc_values = np.array(data['prc'])

                # Main plot (no shadow in aggregate)
                ax.plot(x_values, prc_values, linestyle,
                       color=color, linewidth=4, label=label, zorder=2)

                # Add inline label if needed
                if use_inline_labels:
                    add_line_label(ax, x_values, prc_values, label, color,
                                 fontsize=7 if n_datasets > 30 else 8)

        ax.set_title('PROCESSING TIME (ns/event)',
                    fontsize=18, weight='black', pad=20, color=COLORS['text'])
        ax.set_xlabel('SAMPLE', fontsize=14, weight='bold', color=COLORS['text'])
        ax.set_ylabel('NANOSECONDS', fontsize=14, weight='bold', color=COLORS['text'])
        ax.tick_params(colors=COLORS['text'], which='both')
        ax.grid(True, alpha=0.3, color=COLORS['text'], linewidth=1, linestyle='--')

        # Only show legend if not using inline labels
        if not use_inline_labels:
            # Legend with adaptive columns
            legend = ax.legend(loc='upper left', frameon=True,
                             fancybox=False, shadow=False,
                             edgecolor=COLORS['border'],
                             facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                             prop={'weight': 'bold', 'size': legend_fontsize},
                             ncol=n_cols,
                             bbox_to_anchor=(0.0, 0.98))
            legend.get_frame().set_linewidth(3)
            for text in legend.get_texts():
                text.set_color('black' if palette_name != 'cyberpunk' else 'white')

        # Add corner brackets
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        bracket_size = 0.05

        # Top-left corner bracket
        ax.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size],
               [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
        ax.plot([xlim[0], xlim[0]],
               [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)

        # Bottom-right corner bracket
        ax.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]],
               [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
        ax.plot([xlim[1], xlim[1]],
               [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)

        # Make spines thicker
        for spine in ax.spines.values():
            spine.set_linewidth(4)

    # Adjust layout
    plt.tight_layout()

    # Add decorative border around entire figure
    border_ax = fig.add_subplot(111, frameon=False)
    border_ax.tick_params(labelcolor='none', top=False, bottom=False,
                         left=False, right=False)
    for spine in border_ax.spines.values():
        spine.set_linewidth(8)
        spine.set_edgecolor(COLORS['border'])

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor=COLORS['background'], edgecolor=COLORS['border'])
    print(f"Aggregate plot saved to: {output_path}")
    plt.close(fig)  # Close figure to prevent memory issues


def create_metric_plots(metrics_data, labels, output_path, palette_name='vibrant'):
    """Create neobrutalistic plots with RPS vs PPS for each dataset and other metrics"""
    global COLORS
    COLORS = PALETTES.get(palette_name, PALETTES['vibrant'])
    setup_neobrutalistic_style()
    
    # Create figure with 2x3 grid to accommodate processing time metric
    fig = plt.figure(figsize=(30, 14))
    
    # Add a bold title with shadow effect
    fig.suptitle('PERFORMANCE METRICS ANALYSIS', 
                 fontsize=36, weight='black', y=0.98, color=COLORS['text'])
    
    # Special handling for single dataset
    if len(metrics_data) == 1:
        # Single dataset: RPS vs PPS spans first three columns
        data = metrics_data[0]
        label = labels[0]
        ax = plt.subplot(2, 3, (1, 3))  # Span columns 1, 2, and 3
        
        if 'rps' in data and 'pps' in data:
            # Create x-axis values
            x_values = np.arange(len(data['rps']))
            
            # Get RPS and PPS data
            rps_data = np.array(data['rps'])
            pps_data = np.array(data['pps'])
            
            # Add shadows
            shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
            shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
            x_offset = len(x_values) * 0.003
            y_offset_rps = (max(rps_data) - min(rps_data)) * 0.01
            y_offset_pps = (max(pps_data) - min(pps_data)) * 0.01
            
            # Plot shadows
            ax.plot(x_values + x_offset, rps_data - y_offset_rps,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)
            ax.plot(x_values + x_offset, pps_data - y_offset_pps,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)
            
            # Plot RPS and PPS
            ax.plot(x_values, rps_data, 
                   color=COLORS['primary'], linewidth=4, 
                   label='RPS (Reads)', zorder=3)
            ax.plot(x_values, pps_data, 
                   color=COLORS['secondary'], linewidth=4, 
                   label='PPS (Processed)', zorder=3)
            
            # Fill area between RPS and PPS
            ax.fill_between(x_values, rps_data, pps_data, 
                           alpha=0.3, color=COLORS['tertiary'], 
                           label='Read-Process Gap', zorder=2)
            
            # Styling
            ax.set_title(f'{label} - RPS vs PPS', 
                        fontsize=18, weight='black', pad=20, color=COLORS['text'])
            ax.set_xlabel('SAMPLE', fontsize=14, weight='bold', color=COLORS['text'])
            ax.set_ylabel('OPERATIONS/SEC', fontsize=14, weight='bold', color=COLORS['text'])
            ax.tick_params(colors=COLORS['text'], which='both')
            
            # Double the x-axis ticks since plot spans two columns
            ax.xaxis.set_major_locator(plt.MaxNLocator(integer=True, nbins=20))
            
            # Legend
            legend = ax.legend(loc='upper right', frameon=True, 
                             fancybox=False, shadow=False,
                             edgecolor=COLORS['border'], 
                             facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                             prop={'weight': 'bold', 'size': 10})
            legend.get_frame().set_linewidth(3)
            
            # Set legend text color
            for text in legend.get_texts():
                text.set_color('black' if palette_name != 'cyberpunk' else 'white')
    else:
        # Multiple datasets: First three plots are RPS vs PPS for each dataset (up to 3)
        for idx, (data, label) in enumerate(zip(metrics_data[:3], labels[:3])):
            ax = plt.subplot(2, 3, idx + 1)
            
            if 'rps' in data and 'pps' in data:
                # Create x-axis values
                x_values = np.arange(len(data['rps']))
                
                # Get RPS and PPS data
                rps_data = np.array(data['rps'])
                pps_data = np.array(data['pps'])
                
                # Add shadows
                shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
                shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
                x_offset = len(x_values) * 0.003
                y_offset_rps = (max(rps_data) - min(rps_data)) * 0.01
                y_offset_pps = (max(pps_data) - min(pps_data)) * 0.01
                
                # Plot shadows
                ax.plot(x_values + x_offset, rps_data - y_offset_rps,
                       color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)
                ax.plot(x_values + x_offset, pps_data - y_offset_pps,
                       color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)
                
                # Plot RPS and PPS
                ax.plot(x_values, rps_data, 
                       color=COLORS['primary'], linewidth=4, 
                       label='RPS (Reads)', zorder=3)
                ax.plot(x_values, pps_data, 
                       color=COLORS['secondary'], linewidth=4, 
                       label='PPS (Processed)', zorder=3)
                
                # Fill area between RPS and PPS
                ax.fill_between(x_values, rps_data, pps_data, 
                               alpha=0.3, color=COLORS['tertiary'], 
                               label='Read-Process Gap', zorder=2)
                
                # Styling
                ax.set_title(f'{label} - RPS vs PPS', 
                            fontsize=18, weight='black', pad=20, color=COLORS['text'])
                ax.set_xlabel('SAMPLE', fontsize=14, weight='bold', color=COLORS['text'])
                ax.set_ylabel('OPERATIONS/SEC', fontsize=14, weight='bold', color=COLORS['text'])
                ax.tick_params(colors=COLORS['text'], which='both')
                
                # Legend
                legend = ax.legend(loc='upper right', frameon=True, 
                                 fancybox=False, shadow=False,
                                 edgecolor=COLORS['border'], 
                                 facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                                 prop={'weight': 'bold', 'size': 10})
                legend.get_frame().set_linewidth(3)
                
                # Set legend text color
                for text in legend.get_texts():
                    text.set_color('black' if palette_name != 'cyberpunk' else 'white')
    
    # Plot 4: Events Waiting to be Processed (EWP)
    ax = plt.subplot(2, 3, 4)
    for i, (data, label) in enumerate(zip(metrics_data, labels)):
        if 'ewp' in data:
            color = list(COLORS.values())[i % len(COLORS)]
            linestyle = LINESTYLES[i % len(LINESTYLES)]
            x_values = np.arange(len(data['ewp']))
            
            # Shadow
            shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
            shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
            x_offset = len(x_values) * 0.003
            y_offset = max(1, (max(data['ewp']) - min(data['ewp'])) * 0.01)
            
            ax.plot(x_values + x_offset, np.array(data['ewp']) - y_offset, linestyle,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)
            
            # Main plot
            ax.plot(x_values, data['ewp'], linestyle,
                   color=color, linewidth=4, label=label, zorder=2)
    
    ax.set_title('EVENTS WAITING TO BE PROCESSED', 
                fontsize=18, weight='black', pad=20, color=COLORS['text'])
    ax.set_xlabel('SAMPLE', fontsize=14, weight='bold', color=COLORS['text'])
    ax.set_ylabel('COUNT', fontsize=14, weight='bold', color=COLORS['text'])
    ax.tick_params(colors=COLORS['text'], which='both')
    
    # Legend
    legend = ax.legend(loc='upper right', frameon=True, 
                     fancybox=False, shadow=False,
                     edgecolor=COLORS['border'], 
                     facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                     prop={'weight': 'bold', 'size': 10})
    legend.get_frame().set_linewidth(3)
    for text in legend.get_texts():
        text.set_color('black' if palette_name != 'cyberpunk' else 'white')
    
    # Plot 5: Latency
    ax = plt.subplot(2, 3, 5)
    for i, (data, label) in enumerate(zip(metrics_data, labels)):
        if 'lat' in data:
            color = list(COLORS.values())[i % len(COLORS)]
            linestyle = LINESTYLES[i % len(LINESTYLES)]
            x_values = np.arange(len(data['lat']))
            # Values are already in nanoseconds
            lat_values = np.array(data['lat'])

            # Shadow
            shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
            shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
            x_offset = len(x_values) * 0.003
            y_offset = (max(lat_values) - min(lat_values)) * 0.01 if len(lat_values) > 0 else 0

            ax.plot(x_values + x_offset, lat_values - y_offset, linestyle,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)

            # Main plot
            ax.plot(x_values, lat_values, linestyle,
                   color=color, linewidth=4, label=label, zorder=2)
    
    ax.set_title('AVG eBPF HOOK LATENCY (ns)',
                fontsize=18, weight='black', pad=20, color=COLORS['text'])
    ax.set_xlabel('SAMPLE', fontsize=14, weight='bold', color=COLORS['text'])
    ax.set_ylabel('NANOSECONDS', fontsize=14, weight='bold', color=COLORS['text'])
    ax.tick_params(colors=COLORS['text'], which='both')
    
    # Legend
    legend = ax.legend(loc='upper right', frameon=True, 
                     fancybox=False, shadow=False,
                     edgecolor=COLORS['border'], 
                     facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                     prop={'weight': 'bold', 'size': 10})
    legend.get_frame().set_linewidth(3)
    for text in legend.get_texts():
        text.set_color('black' if palette_name != 'cyberpunk' else 'white')
    
    # Plot 6: Processing Time
    ax = plt.subplot(2, 3, 6)
    for i, (data, label) in enumerate(zip(metrics_data, labels)):
        if 'prc' in data:
            color = list(COLORS.values())[i % len(COLORS)]
            linestyle = LINESTYLES[i % len(LINESTYLES)]
            x_values = np.arange(len(data['prc']))
            
            # Shadow
            shadow_color = 'white' if palette_name == 'cyberpunk' else 'black'
            shadow_alpha = 0.2 if palette_name == 'cyberpunk' else 0.3
            x_offset = len(x_values) * 0.003
            prc_values = np.array(data['prc'])
            if len(prc_values) > 0 and prc_values.max() > prc_values.min():
                y_offset = (prc_values.max() - prc_values.min()) * 0.01
            else:
                y_offset = 1
            
            ax.plot(x_values + x_offset, prc_values - y_offset, linestyle,
                   color=shadow_color, linewidth=5, alpha=shadow_alpha, zorder=1)
            
            # Main plot
            ax.plot(x_values, prc_values, linestyle,
                   color=color, linewidth=4, label=label, zorder=2)
    
    ax.set_title('PROCESSING TIME (ns/event)', 
                fontsize=18, weight='black', pad=20, color=COLORS['text'])
    ax.set_xlabel('SAMPLE', fontsize=14, weight='bold', color=COLORS['text'])
    ax.set_ylabel('NANOSECONDS', fontsize=14, weight='bold', color=COLORS['text'])
    ax.tick_params(colors=COLORS['text'], which='both')
    
    # Legend
    legend = ax.legend(loc='upper right', frameon=True, 
                     fancybox=False, shadow=False,
                     edgecolor=COLORS['border'], 
                     facecolor='white' if palette_name != 'cyberpunk' else COLORS['border'],
                     prop={'weight': 'bold', 'size': 10})
    legend.get_frame().set_linewidth(3)
    for text in legend.get_texts():
        text.set_color('black' if palette_name != 'cyberpunk' else 'white')
    
    # Add decorative elements to all subplots
    if len(metrics_data) == 1:
        # For single dataset: RPS/PPS spans (1,3), EWP is 4, Latency is 5, Processing is 6
        subplot_positions = [(1, 3), 4, 5, 6]
        for pos in subplot_positions:
            if isinstance(pos, tuple):
                ax = plt.subplot(2, 3, pos)
            else:
                ax = plt.subplot(2, 3, pos)
            
            # Corner brackets
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            bracket_size = 0.05
            
            # Top-left corner bracket
            ax.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size], 
                   [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
            ax.plot([xlim[0], xlim[0]], 
                   [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)
            
            # Bottom-right corner bracket
            ax.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]], 
                   [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
            ax.plot([xlim[1], xlim[1]], 
                   [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)
            
            # Make spines thicker
            for spine in ax.spines.values():
                spine.set_linewidth(4)
                
            # Add background pattern (diagonal stripes)
            for i in range(0, 100, 10):
                ax.axhspan(ax.get_ylim()[0] + i * (ax.get_ylim()[1] - ax.get_ylim()[0]) / 100,
                          ax.get_ylim()[0] + (i + 5) * (ax.get_ylim()[1] - ax.get_ylim()[0]) / 100,
                          facecolor='white', alpha=0.1, zorder=0)
    else:
        # For multiple datasets: regular 2x3 grid
        for idx in range(1, 7):
            ax = plt.subplot(2, 3, idx)
        
            # Corner brackets
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            bracket_size = 0.05
            
            # Top-left corner bracket
            ax.plot([xlim[0], xlim[0] + (xlim[1]-xlim[0])*bracket_size], 
                   [ylim[1], ylim[1]], color=COLORS['border'], linewidth=6)
            ax.plot([xlim[0], xlim[0]], 
                   [ylim[1], ylim[1] - (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)
            
            # Bottom-right corner bracket
            ax.plot([xlim[1] - (xlim[1]-xlim[0])*bracket_size, xlim[1]], 
                   [ylim[0], ylim[0]], color=COLORS['border'], linewidth=6)
            ax.plot([xlim[1], xlim[1]], 
                   [ylim[0], ylim[0] + (ylim[1]-ylim[0])*bracket_size], color=COLORS['border'], linewidth=6)
            
            # Make spines thicker
            for spine in ax.spines.values():
                spine.set_linewidth(4)
                
            # Add background pattern (diagonal stripes)
            for i in range(0, 100, 10):
                ax.axhspan(ax.get_ylim()[0] + i * (ax.get_ylim()[1] - ax.get_ylim()[0]) / 100,
                          ax.get_ylim()[0] + (i + 5) * (ax.get_ylim()[1] - ax.get_ylim()[0]) / 100,
                          facecolor='white', alpha=0.1, zorder=0)
    
    # Adjust layout
    plt.tight_layout()
    
    # Add decorative border around entire figure
    border_ax = fig.add_subplot(111, frameon=False)
    border_ax.tick_params(labelcolor='none', top=False, bottom=False, 
                         left=False, right=False)
    for spine in border_ax.spines.values():
        spine.set_linewidth(8)
        spine.set_edgecolor(COLORS['border'])
    
    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor=COLORS['background'], edgecolor=COLORS['border'])
    print(f"Plot saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description='Generate neobrutalistic metric plots from JSON files')
    parser.add_argument('--files', nargs='+', required=True,
                       help='JSON files with metrics, format: label:path')
    parser.add_argument('--output', '-o', default='metrics_plot.png',
                       help='Output PNG file path (default: metrics_plot.png)')
    parser.add_argument('--palette', '-p', default='vibrant',
                       choices=['vibrant', 'cyberpunk', 'brutalist'],
                       help='Color palette to use (default: vibrant)')
    parser.add_argument('--mode', '-m', default='new',
                       choices=['all', 'rps-pps', 'new', 'individual', 'aggregate'],
                       help='Plot mode: all (old behavior), rps-pps (comparison), new (individual + aggregate), individual (only per-file), aggregate (only combined) (default: new)')

    args = parser.parse_args()

    # Parse files and labels
    metrics_data = []
    labels = []

    for file_spec in args.files:
        if ':' not in file_spec:
            print(f"Error: File spec must be in format 'label:path', got: {file_spec}")
            sys.exit(1)

        label, path = file_spec.split(':', 1)

        if not Path(path).exists():
            print(f"Error: File not found: {path}")
            sys.exit(1)

        try:
            data = load_metrics(path)
            metrics_data.append(data)
            labels.append(label)
            print(f"Loaded metrics from {path} with label '{label}'")
        except Exception as e:
            print(f"Error loading {path}: {e}")
            sys.exit(1)

    # Create plots based on mode
    if args.mode == 'rps-pps':
        # Old RPS vs PPS comparison mode
        create_rps_pps_comparison(metrics_data, labels, args.output, args.palette)
    elif args.mode == 'all':
        # Old all metrics mode
        create_metric_plots(metrics_data, labels, args.output, args.palette)
    elif args.mode in ['new', 'individual']:
        # Generate individual plots for each file
        output_base = Path(args.output).stem
        output_dir = Path(args.output).parent
        output_ext = Path(args.output).suffix or '.png'

        for data, label in zip(metrics_data, labels):
            # Create individual plot for each file
            individual_output = output_dir / f"{label}_rps_pps_events{output_ext}"
            create_individual_file_plot(data, label, str(individual_output), args.palette)

        if args.mode == 'new':
            # Also create aggregate plot
            aggregate_output = output_dir / f"{output_base}_aggregate{output_ext}"
            create_aggregate_metrics_plot(metrics_data, labels, str(aggregate_output), args.palette)
    elif args.mode == 'aggregate':
        # Only generate aggregate plot
        create_aggregate_metrics_plot(metrics_data, labels, args.output, args.palette)

if __name__ == "__main__":
    main()
