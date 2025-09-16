#!/usr/bin/env python3

import os
import shutil

import pyarrow.parquet as pq


def read_parquet_metadata(file_path):
    """Read and print file-level metadata from a parquet file."""
    try:
        # Open the parquet file
        parquet_file = pq.ParquetFile(file_path)

        print(f"File: {file_path}")
        print("=" * 80)

        # Get file metadata
        metadata = parquet_file.metadata
        print(metadata)

        # Also print schema metadata
        schema = parquet_file.schema_arrow
        if schema.metadata:
            print("\nSchema metadata:")
            for key, value in schema.metadata.items():
                key_str = key.decode("utf-8") if isinstance(key, bytes) else key
                value_str = value.decode("utf-8") if isinstance(value, bytes) else value
                print(f"  {key_str}: {value_str}")

    except Exception as e:
        print(f"Error reading parquet file: {e}")


def add_file_metadata(filepath, description, source, source_url, license_info):
    """
    Add file-level metadata to a parquet file.

    Args:
        filepath (str): Path to the parquet file
        description (str): Description of the dataset
        source (str): Source of the data
        source_url (str): URL of the data source
        license_info (str): License information
    """
    try:
        if not filepath.endswith(".parquet"):
            raise ValueError("File must be a parquet file")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        # Read the existing parquet file
        table = pq.read_table(filepath)

        # Get existing schema metadata
        existing_metadata = table.schema.metadata or {}

        # Create new metadata dictionary
        new_metadata = dict(existing_metadata)
        new_metadata[b"description"] = description.encode("utf-8")
        new_metadata[b"source"] = source.encode("utf-8")
        new_metadata[b"source_url"] = source_url.encode("utf-8")
        new_metadata[b"license"] = license_info.encode("utf-8")

        # Create new schema with updated metadata
        new_schema = table.schema.with_metadata(new_metadata)

        # Create new table with updated schema
        new_table = table.cast(new_schema)

        # Write to a temporary file first
        temp_file = filepath.replace(".parquet", ".new.parquet")
        pq.write_table(new_table, temp_file)

        # Replace the original file
        shutil.move(temp_file, filepath)

        print(f"Successfully added metadata to {filepath}")
        print("Added metadata:")
        print(f"  description: {description}")
        print(f"  source: {source}")
        print(f"  source_url: {source_url}")
        print(f"  license: {license_info}")

    except Exception as e:
        print(f"Error adding metadata to parquet file: {e}")


if __name__ == "__main__":
    file_path = "/Users/senlin/Work/sense-table-demo-data/datasets-todo/image-to-video-human-preference-hailuo-02-marey/train.parquet"

    print("=== BEFORE ADDING METADATA ===")
    read_parquet_metadata(file_path)

    print("\n=== ADDING METADATA ===")
    add_file_metadata(
        filepath=file_path,
        description="Rapidata Video Generation Hailuo-02 v Marey Human Preference",
        source="Rapidata",
        source_url="https://huggingface.co/datasets/Rapidata/image-to-video-human-preference-hailuo-02-marey",
        license_info="Apache license 2.0",
    )

    print("\n=== AFTER ADDING METADATA ===")
    read_parquet_metadata(file_path)
