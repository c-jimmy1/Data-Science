import pandas as pd
import h5py
import numpy as np
from datetime import datetime
import os
from pathlib import Path

# Directories
DATASET_I_DIR = Path(__file__).resolve().parent.parent
HDF5_ROOT = DATASET_I_DIR.parent
ASSIGN4_ROOT = HDF5_ROOT.parent

RAW_DIR = ASSIGN4_ROOT / "raw_data" / "dataset_i_dining"

DATA_DIR_I = DATASET_I_DIR / "data"
DATA_DIR_I.mkdir(parents=True, exist_ok=True)

dining_data_path = RAW_DIR / "raw" / "dining_data.csv"
data_dict_path = RAW_DIR / "metadata" / "data_dictionary.csv"
dc_jsonld_path = RAW_DIR / "metadata" / "dublin_core_metadata.jsonld"

h5_filename = DATA_DIR_I / "dataset_i_dining.h5"

# Step 1: Load the raw data

# Adjust these if your header names are slightly different
cols = [
    "timestamp",
    "vendor",
    "num_people",
    "start_time",
    "end_time",
    "line_wait_time (min)",
]

# Load main dining data
dining_df = pd.read_csv(dining_data_path)

# Ensure we only keep the expected columns and in a defined order
missing_cols = [c for c in cols if c not in dining_df.columns]
if missing_cols:
    raise ValueError(f"Expected columns {missing_cols} not found in dining_data.csv")

dining_df = dining_df[cols]

# Build a NumPy structured array (compound dtype) for the HDF5 table
dtype = np.dtype([
    ("timestamp", "S32"),           # "YYYY-MM-DD HH:MM:SS" as text
    ("vendor", "S64"),              # vendor name
    ("num_people", "i4"),           # 32-bit integer
    ("start_time", "S8"),           # "HH:MM"
    ("end_time", "S8"),             # "HH:MM"
    ("line_wait_time_min", "i4"),   # derived from CSV column "line_wait_time (min)"
])

structured = np.zeros(len(dining_df), dtype=dtype)

structured["timestamp"] = dining_df["timestamp"].astype(str).to_numpy(dtype="S32")
structured["vendor"] = dining_df["vendor"].astype(str).to_numpy(dtype="S64")
structured["num_people"] = dining_df["num_people"].to_numpy(dtype="i4")
structured["start_time"] = dining_df["start_time"].astype(str).to_numpy(dtype="S8")
structured["end_time"] = dining_df["end_time"].astype(str).to_numpy(dtype="S8")
structured["line_wait_time_min"] = dining_df["line_wait_time (min)"].to_numpy(dtype="i4")

# Load data dictionary
data_dict_df = pd.read_csv(data_dict_path)
dd_values = data_dict_df.astype(str).to_numpy()

# Load Dublin Core JSON-LD as raw text (we don’t need to parse it here)
with open(dc_jsonld_path, "r", encoding="utf-8") as f:
    dc_text = f.read()

# String dtypes for HDF5
utf8_str_dtype = h5py.string_dtype(encoding="utf-8")

# Step 2: Write HDF5 file

with h5py.File(h5_filename, "w") as f:
    # ---- File-level attributes (overall metadata) ----
    f.attrs["dataset_label"] = "Dataset I"
    f.attrs["title"] = "Campus Dining Line Wait Times (Observed + Mock)"
    f.attrs["creators"] = np.array(
        ["Jimmy Chen", "Joshua Sundararaman", "Taein Yi"],
        dtype="S64"
    )
    f.attrs["temporal_coverage"] = "2025-10-02/2025-10-06"
    f.attrs["spatial_coverage"] = "RPI Union, Troy, NY"
    f.attrs["license"] = "MIT License"
    f.attrs["description"] = (
        "Observed and mock line wait times at campus dining vendors in the RPI Union. "
        "Each record represents a party arriving at a vendor, with recorded queue "
        "join and exit times and a derived line wait time in minutes."
    )
    f.attrs["standard"] = "Dublin Core (DCMI Terms)"
    f.attrs["conversion_software"] = "Python (pandas + h5py)"
    f.attrs["conversion_date_utc"] = datetime.utcnow().isoformat() + "Z"

    # ---- Main data group ----
    g_data = f.create_group("dining_data")
    g_data.attrs["logical_structure"] = (
        "Tabular dataset: each row is one party arriving at a vendor; fields include "
        "timestamp, vendor name, party size, queue join and exit times, and total "
        "line wait time in minutes."
    )

    d_table = g_data.create_dataset(
        "table",
        data=structured,
        dtype=dtype
    )
    d_table.attrs["field_order"] = np.array(
        ["timestamp", "vendor", "num_people", "start_time", "end_time", "line_wait_time_min"],
        dtype="S32"
    )
    d_table.attrs["original_column_names"] = np.array(
        cols,
        dtype="S32"
    )
    d_table.attrs["notes"] = (
        "line_wait_time_min corresponds to the CSV column 'line_wait_time (min)'. "
        "It is the total minutes spent waiting in line for that party."
    )

    # ---- Data dictionary group ----
    g_dd = f.create_group("data_dictionary")
    g_dd.attrs["description"] = (
        "Field-level metadata copied from data_dictionary.csv, including names, "
        "types, descriptions, and any constraints for each column."
    )

    d_dd = g_dd.create_dataset(
        "table",
        data=dd_values,
        dtype=utf8_str_dtype
    )
    d_dd.attrs["columns"] = np.array(
        list(data_dict_df.columns),
        dtype="S64"
    )

    # ---- Metadata group with Dublin Core JSON-LD ----
    g_meta = f.create_group("metadata")
    g_meta.attrs["description"] = (
        "Original dataset-level Dublin Core metadata record serialized as JSON-LD."
    )

    d_dc = g_meta.create_dataset(
        "dublin_core_metadata_jsonld",
        data=dc_text,
        dtype=utf8_str_dtype
    )
    d_dc.attrs["format"] = "application/ld+json"
    d_dc.attrs["role"] = "dataset-level metadata (Dublin Core JSON-LD)"

print(f"Created HDF5 file for Dataset I: {os.path.abspath(h5_filename)}")