#!./.venv/bin/python

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import glob
import os
import argparse
import re
import numpy as np
from heat1d_solver import run_solver, get_timestamp
from pathlib import Path

def sort_key_func(filename):
    """Extract number from filename like 'prefix_t_10.csv'."""
    match = re.search(r'_t_(\d+)\.csv$', filename)
    return int(match.group(1)) if match else 0

def create_animation(result, output_file=None, interval=50, ymin=None, ymax=None, L=1.0):
    """Create an animation from simulation data."""
    if not result:
        print("No simulation data available")
        return
    
    # Create imgs directory if it doesn't exist
    imgs_dir = Path("imgs")
    imgs_dir.mkdir(exist_ok=True)
    
    # Generate output filename with timestamp if not provided
    if output_file is None:
        timestamp = get_timestamp()
        output_file = imgs_dir / f"heat_conduction_{timestamp}.gif"
    else:
        output_file = imgs_dir / output_file
    
    df = result['data']
    timesteps = result['timesteps']
    x = result['x']
    params = result['params']  # Get simulation parameters
    
    # Calculate dx from L and num_x if not provided
    if 'dx' not in params:
        params['dx'] = L / (params['num_x'] + 1)
    
    # Determine y-axis limits if not provided
    if ymin is None or ymax is None:
        if ymin is None:
            ymin = df['Temperature'].min() - 0.1 * (df['Temperature'].max() - df['Temperature'].min())
        if ymax is None:
            ymax = df['Temperature'].max() + 0.1 * (df['Temperature'].max() - df['Temperature'].min())
    
    print(f"Y-axis limits: [{ymin}, {ymax}]")
    print(f"X-axis limit (Domain Length L): {L}")
    
    # Create figure and animation
    fig, ax = plt.subplots(figsize=(10, 6))
    line, = ax.plot([], [], lw=2)
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    
    # Add parameter information
    param_text = (
        f"Parameters:\n"
        f"α = {params['alpha']:.3e} (Thermal diffusivity)\n"
        f"dx = {params['dx']:.3e} (Spatial step)\n"
        f"dt = {params['dt']:.3e} (Time step)\n"
        f"CFL = {params['alpha'] * params['dt'] / (params['dx'] * params['dx']):.3f} (Courant number)\n"
        f"Total time = {params['total_time']:.3f}\n"
        f"Number of cells = {params['num_x']}"
    )
    ax.text(0.98, 0.95, param_text, transform=ax.transAxes, 
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'),
            fontsize=8, verticalalignment='top', horizontalalignment='right')
    
    ax.set_xlim(0, L)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("Position (x)")
    ax.set_ylabel("Temperature")
    ax.set_title("Heat Conduction Simulation")
    ax.grid(True)
    
    def init():
        line.set_data([], [])
        time_text.set_text('')
        return line, time_text
    
    def update(frame):
        if frame % 100 == 0:  # Show progress every 100 frames
            print(f"Processing frame {frame}/{len(timesteps)} ({(frame/len(timesteps)*100):.1f}%)")
        
        current_time = timesteps[frame]
        current_data = df[df['t'] == current_time]
        line.set_data(current_data['x'], current_data['Temperature'])
        time_text.set_text(f'Time: {current_time:.3f}')
        return line, time_text
    
    print(f"Generating {len(timesteps)} frames...")
    ani = animation.FuncAnimation(fig, update, frames=len(timesteps),
                                init_func=init, blit=True, interval=interval)
    
    # Save animation
    print(f"\nSaving animation to {output_file}...")
    try:
        # Use a higher DPI for better quality
        ani.save(output_file, writer='pillow', fps=1000/interval, dpi=100)
        print("Animation saved successfully!")
        
        # Verify the GIF file was created and has a reasonable size
        if output_file.exists():
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print(f"GIF file size: {size_mb:.2f} MB")
            if size_mb < 0.1:  # If file is too small, it might be corrupted
                print("Warning: GIF file seems too small, might be corrupted")
        else:
            print("Error: GIF file was not created")
            
    except Exception as e:
        print(f"Error saving animation: {e}")
        print("Please ensure Pillow is installed: pip install Pillow")
    
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Create animation from heat conduction simulation results')
    parser.add_argument('--output', help='Output GIF file name (default: heat_conduction_TIMESTAMP.gif)')
    parser.add_argument('--interval', type=int, default=50, help='Interval between frames in milliseconds')
    parser.add_argument('--ymin', type=float, help='Minimum y-axis value')
    parser.add_argument('--ymax', type=float, help='Maximum y-axis value')
    parser.add_argument('--L', type=float, default=1.0, help='Domain length')
    parser.add_argument('--alpha', type=float, default=0.01, help='Thermal diffusivity')
    parser.add_argument('--dt', type=float, default=0.002, help='Time step size')
    parser.add_argument('--time', type=float, default=1.0, help='Total simulation time')
    parser.add_argument('--num-x', type=int, default=100, help='Number of spatial cells')
    
    args = parser.parse_args()
    
    # Run simulation and get results
    result = run_solver(alpha=args.alpha, dt=args.dt, total_time=args.time, num_x=args.num_x)
    
    # Create animation
    create_animation(result, args.output, args.interval, args.ymin, args.ymax, args.L)

if __name__ == "__main__":
    main() 