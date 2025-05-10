#!./.venv/bin/python

import subprocess
import os
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

def get_timestamp():
    """Get current timestamp in format YYYYMMDDHHMM."""
    return datetime.now().strftime("%Y%m%d%H%M")

def run_solver(alpha=0.01, dt=0.002, total_time=1.0, num_x=100):
    """
    Run the heat1d_solver executable with specified parameters and return the simulation data.
    
    Args:
        alpha (float): Thermal diffusivity (default: 0.01)
        dt (float): Time step size (default: 0.002)
        total_time (float): Total simulation time (default: 1.0)
        num_x (int): Number of spatial cells (default: 100)
    
    Returns:
        dict: A dictionary containing:
            - 'data': DataFrame with all timesteps
            - 'timesteps': List of timestep numbers
            - 'x': Array of spatial positions
            - 'params': Dictionary of simulation parameters
            - 'results_dir': Path to the results directory
    
    Raises:
        subprocess.CalledProcessError: If the solver fails to run
        FileNotFoundError: If the solver executable is not found
    """
    # Create timestamped results directory
    timestamp = get_timestamp()
    results_dir = Path("results") / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Get the absolute path to the solver executable
    solver_path = Path(__file__).parent.parent / "build" / "heat1d_solver"
    if not solver_path.exists():
        raise FileNotFoundError(f"Solver executable not found at {solver_path}")
    
    # Run the solver
    cmd = [
        str(solver_path),
        "--alpha", str(alpha),
        "--dt", str(dt),
        "--time", str(total_time),
        "--output", str(results_dir / "temperature"),
        str(num_x)
    ]
    
    print(f"Running simulation with parameters:")
    print(f"  alpha = {alpha}")
    print(f"  dt = {dt}")
    print(f"  total_time = {total_time}")
    print(f"  num_x = {num_x}")
    print(f"  results directory: {results_dir}")
    
    subprocess.run(cmd, check=True)
    
    # Read the all_timesteps file
    all_timesteps_file = results_dir / "temperature_all_timesteps.csv"
    if not all_timesteps_file.exists():
        raise FileNotFoundError(f"Output file not found: {all_timesteps_file}")
    
    # Read the data
    df = pd.read_csv(all_timesteps_file)
    
    # Extract unique timesteps and x positions
    timesteps = sorted(df['t'].unique())
    x = sorted(df['x'].unique())
    
    # Create result dictionary
    result = {
        'data': df,
        'timesteps': timesteps,
        'x': x,
        'params': {
            'alpha': alpha,
            'dt': dt,
            'total_time': total_time,
            'num_x': num_x
        },
        'results_dir': results_dir
    }
    
    return result

def run_multiple_simulations(alpha_values, dt=0.002, total_time=1.0, num_x=100):
    """
    Run multiple simulations with different alpha values.
    
    Args:
        alpha_values (list): List of alpha values to simulate
        dt (float): Time step size
        total_time (float): Total simulation time
        num_x (int): Number of spatial cells
    
    Returns:
        dict: Dictionary with alpha values as keys and simulation results as values
    """
    results = {}
    for alpha in alpha_values:
        print(f"\nRunning simulation for α = {alpha:.3f}...")
        results[alpha] = run_solver(alpha=alpha, dt=dt, total_time=total_time, num_x=num_x)
    return results

if __name__ == "__main__":
    # Example usage when run directly
    result = run_solver()
    print("\nSimulation completed successfully!")
    print(f"Number of timesteps: {len(result['timesteps'])}")
    print(f"Number of spatial points: {len(result['x'])}")
    print(f"Results saved in: {result['results_dir']}") 