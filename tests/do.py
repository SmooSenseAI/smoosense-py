#!/usr/bin/env python3
"""
Temporary script to process selected.parquet file
"""

import pandas as pd
import json
import os

# Input file path
input_file = os.path.expanduser("~/Downloads/selected.parquet")

# Output file path
output_file = os.path.expanduser("~/Downloads/cleaned.parquet")

print(f"Reading data from: {input_file}")
df = pd.read_parquet(input_file)

print(f"Original DataFrame shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Remove row where file_name is 'image_simplified_sd_11010.jpg'
print("Removing row with file_name = 'image_simplified_sd_11010.jpg'")
df = df[df['file_name'] != 'image_simplified_sd_11010.jpg']
print(f"After removing row: {df.shape}")

# Keep only specified columns
columns_to_keep = ['image_url', 'image_mask_alignment', 'word_scores', 'alignment_score']
print(f"Keeping only columns: {columns_to_keep}")

# Check if all columns exist
missing_columns = [col for col in columns_to_keep if col not in df.columns]
if missing_columns:
    print(f"Warning: Missing columns: {missing_columns}")
    columns_to_keep = [col for col in columns_to_keep if col in df.columns]
    print(f"Using available columns: {columns_to_keep}")

df = df[columns_to_keep]
print(f"After column selection: {df.shape}")

# Process word_scores column
if 'word_scores' in df.columns:
    print("Processing word_scores column...")

    def process_word_scores(word_scores_str):
        try:
            # Parse JSON string to list
            word_list = json.loads(word_scores_str)

            # Remove the last item if list is not empty
            if isinstance(word_list, list) and len(word_list) > 0:
                word_list = word_list[:-1]

            # Convert back to JSON string
            return json.dumps(word_list)
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error processing word_scores: {e}")
            return word_scores_str  # Return original if parsing fails

    # Apply the processing function to word_scores column
    df['word_scores'] = df['word_scores'].apply(process_word_scores)
    print("word_scores processing completed")

print(f"Final DataFrame shape: {df.shape}")

# Save the processed data
print(f"Saving processed data to: {output_file}")
df.to_parquet(output_file, index=False)

print("Done!")

# Display sample of the processed data
print("\nSample of processed data:")
print(df.head(2))