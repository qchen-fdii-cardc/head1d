#!./.venv/bin/python

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import glob
import os
import argparse
import re
import numpy as np
from pathlib import Path
from heat1d_solver import run_multiple_simulations, get_timestamp

# Disable interactive mode to prevent showing plots
plt.ioff()

def create_comparison_animation(results, output_gif=None, interval=100):
    """Create an animation comparing temperature evolution for different alpha values."""
    if not results:
        print("No simulation results available for comparison")
        return
    
    # Create imgs directory if it doesn't exist
    imgs_dir = Path("imgs")
    imgs_dir.mkdir(exist_ok=True)
    
    # Generate output filename with timestamp if not provided
    if output_gif is None:
        timestamp = get_timestamp()
        output_gif = imgs_dir / f"alpha_comparison_{timestamp}.gif"
    else:
        output_gif = Path(output_gif)
        if not output_gif.parent.exists():
            output_gif.parent.mkdir(parents=True)
    
    # Get global min/max temperatures
    max_temp = float('-inf')
    min_temp = float('inf')
    
    for alpha, result in results.items():
        df = result['data']
        max_temp = max(max_temp, df['Temperature'].max())
        min_temp = min(min_temp, df['Temperature'].min())
    
    # Add some padding to the temperature range
    temp_range = max_temp - min_temp
    y_min = min_temp - 0.1 * temp_range
    y_max = max_temp + 0.1 * temp_range
    
    print("\nCreating animation frames...")
    # Create the animation
    fig, ax = plt.subplots(figsize=(10, 6))
    lines = {}
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)
    
    # Plot initial state for each alpha
    for alpha, result in results.items():
        initial_data = result['data'][result['data']['t'] == result['timesteps'][0]]
        line, = ax.plot(initial_data['x'], initial_data['Temperature'], 
                       label=f'α = {alpha:.3f}', lw=2)
        lines[alpha] = line
    
    ax.set_xlim(0, 1.0)
    ax.set_ylim(y_min, y_max)
    ax.set_xlabel("Position (x)")
    ax.set_ylabel("Temperature")
    ax.set_title("Temperature Evolution for Different Thermal Diffusivity Values")
    ax.grid(True)
    ax.legend()
    
    def init():
        for line in lines.values():
            line.set_data([], [])
        time_text.set_text('')
        return list(lines.values()) + [time_text]
    
    # Get unique time points from the first dataset
    time_points = results[list(results.keys())[0]]['timesteps']
    total_frames = len(time_points)
    
    def update(frame):
        if frame % 100 == 0:  # Show progress every 100 frames
            print(f"Processing frame {frame}/{total_frames} ({(frame/total_frames*100):.1f}%)")
        
        current_time = time_points[frame]
        for alpha, result in results.items():
            current_data = result['data'][result['data']['t'] == current_time]
            if not current_data.empty:
                lines[alpha].set_data(current_data['x'], current_data['Temperature'])
        time_text.set_text(f'Time: {current_time:.3f}')
        return list(lines.values()) + [time_text]
    
    print(f"Generating {total_frames} frames...")
    ani = animation.FuncAnimation(fig, update, frames=total_frames,
                                init_func=init, blit=True, interval=interval)
    
    # Save animation
    print(f"\nSaving animation to {output_gif}...")
    try:
        # Use a higher DPI for better quality
        ani.save(str(output_gif), writer='pillow', fps=1000/interval, dpi=100)
        print("Animation saved successfully!")
        
        # Verify the GIF file was created and has a reasonable size
        if output_gif.exists():
            size_mb = output_gif.stat().st_size / (1024 * 1024)
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
    # Define alpha values to compare
    alpha_values = [0.001, 0.01, 0.1]
    
    print("Starting comparison of different thermal diffusivity values...")
    # Run simulations for each alpha value
    results = run_multiple_simulations(alpha_values)
    
    # Create comparison animation
    create_comparison_animation(results)
    print("\nComparison complete!")

if __name__ == "__main__":
    main() 