#!/usr/bin/env python3
"""
Temporary script to extract images from parquet files.
Extract image_name.bytes and save as jpg image using image_name.path as filename.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
from PIL import Image


def convert_heatmap_to_image(heatmap_data, output_path: Path) -> None:
    """
    Convert 1024x1024 heatmap data (0-1 floats) to grayscale image (0-255).

    Args:
        heatmap_data: 1024x1024 list of lists with float values 0-1
        output_path: Path to save the image
    """

    # Handle nested numpy arrays or convert to numpy array
    if isinstance(heatmap_data, np.ndarray):
        # Check if this is a 1D array of arrays (nested structure)
        if heatmap_data.shape == (1024,) and hasattr(heatmap_data[0], '__len__'):
            # Convert each nested array to list, then to 2D array
            heatmap_list = [list(row) for row in heatmap_data]
            heatmap_array = np.array(heatmap_list, dtype=np.float32)
        else:
            heatmap_array = heatmap_data.astype(np.float32)
    else:
        # Try to convert list of lists to array, handling nested structures
        raise TypeError(f"Heatmap data type {type(heatmap_data)} is not supported")


    # Inverse the values and convert from 0-1 range to 0-255 range
    inverted_array = heatmap_array
    grayscale_array = (inverted_array * 255).astype(np.uint8)

    # Create PIL image
    image = Image.fromarray(grayscale_array, mode='L')

    # Save as PNG
    image.save(output_path, 'PNG')


def process_parquet_file(parquet_path: Path, output_dir: Path) -> None:
    """
    Process a single parquet file to extract images and heatmaps.

    Args:
        parquet_path: Path to the parquet file
        output_dir: Directory to save extracted images
    """
    print(f"Processing: {parquet_path}")

    # Read the parquet file
    df = pd.read_parquet(parquet_path)

    print(f"Found {len(df)} rows in {parquet_path.name}")

    # Check if required columns exist
    if 'image_name' not in df.columns:
        print(f"Warning: 'image_name' column not found in {parquet_path.name}")
        print(f"Available columns: {list(df.columns)}")
        return

    # Find heatmap columns (columns ending with 'heatmap')
    heatmap_columns = [col for col in df.columns if col.endswith('heatmap')]
    print(f"Found {len(heatmap_columns)} heatmap columns: {heatmap_columns}")

    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)

    # Create directories for heatmaps
    heatmap_dirs = {}
    for col in heatmap_columns:
        heatmap_dir = output_dir.parent / f"image_mask_{col}"
        heatmap_dir.mkdir(parents=True, exist_ok=True)
        heatmap_dirs[col] = heatmap_dir

    # Process each row
    for idx, row in df.iterrows():
        try:
            image_name = row['image_name']

            # Extract bytes and path from image_name dict
            if isinstance(image_name, dict) and 'bytes' in image_name and 'path' in image_name:
                image_bytes = image_name['bytes']
                image_path = image_name['path']

                # Get filename from path
                filename = Path(image_path).name

                # Ensure it has .jpg extension
                if not filename.lower().endswith('.jpg'):
                    filename = f"{Path(filename).stem}.jpg"

                # Save image
                output_file = output_dir / filename
                with open(output_file, 'wb') as f:
                    f.write(image_bytes)

                print(f"  Saved: {filename} ({len(image_bytes)} bytes)")

                # Process heatmap columns for this row
                for col in heatmap_columns:
                    heatmap_data = row[col]

                    # Skip if null/None - use proper null check for arrays
                    if heatmap_data is None or (hasattr(heatmap_data, '__len__') and len(heatmap_data) == 0):
                        continue

                    # Convert heatmap to grayscale image (change extension to .png)
                    png_filename = f"{Path(filename).stem}.png"
                    heatmap_output_file = heatmap_dirs[col] / png_filename
                    convert_heatmap_to_image(heatmap_data, heatmap_output_file)
                    print(f"  Saved heatmap: {col}/{png_filename}")



            else:
                print(f"  Row {idx}: image_name doesn't have expected 'bytes' or 'path' keys")
                print(f"  Type: {type(image_name)}, keys: {image_name.keys() if isinstance(image_name, dict) else 'N/A'}")

        except Exception as e:
            print(f"  Error processing row {idx}: {e}")


def main():
    """Main function to process parquet files."""

    # Define paths
    data_dir = Path("/Users/senlin/Work/sense-table-demo-data/datasets-todo/text-2-image-Rich-Human-Feedback-32k/data")
    output_dir = Path("/Users/senlin/Work/sense-table-demo-data/datasets-todo/text-2-image-Rich-Human-Feedback-32k/images")

    # Check if data directory exists
    if not data_dir.exists():
        print(f"Error: Data directory does not exist: {data_dir}")
        return

    # Find all parquet files
    parquet_files = list(data_dir.glob("*.parquet"))

    if not parquet_files:
        print(f"No parquet files found in {data_dir}")
        return

    print(f"Found {len(parquet_files)} parquet files")

    # Process only the first file for testing
    first_file = parquet_files[0]
    print(f"Testing with first file: {first_file.name}")

    process_parquet_file(first_file, output_dir)

    print("\nTest complete. Check the output to verify it works before processing all files.")

    # Uncomment the following lines to process all files:
    # print("\nProcessing all files...")
    # for parquet_file in parquet_files:
    #     process_parquet_file(parquet_file, output_dir)


if __name__ == "__main__":
    main()