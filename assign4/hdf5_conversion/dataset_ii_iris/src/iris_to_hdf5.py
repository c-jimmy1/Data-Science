import pandas as pd
import h5py
import numpy as np
from datetime import datetime
import os
from pathlib import Path

# Directories
DATASET_II_DIR = Path(__file__).resolve().parent.parent
HDF5_ROOT = DATASET_II_DIR.parent
ASSIGN4_ROOT = HDF5_ROOT.parent

RAW_DIR = ASSIGN4_ROOT / "raw_data" / "dataset_ii_iris"
DATA_DIR_II = DATASET_II_DIR / "data"
DATA_DIR_II.mkdir(parents=True, exist_ok=True)  # make sure it exists

iris_data_path = RAW_DIR / "iris.data"
iris_names_path = RAW_DIR / "iris.names"
index_path = RAW_DIR / "index"
h5_filename = DATA_DIR_II / "dataset_ii_iris.h5"

# Step 1: Load the raw data

# iris.data has no header row; we supply column names explicitly
iris_cols = [
    "sepal_length_cm",
    "sepal_width_cm",
    "petal_length_cm",
    "petal_width_cm",
    "species"
]

iris_df = pd.read_csv(
    iris_data_path,
    header=None,
    names=iris_cols,
    dtype={
        "sepal_length_cm": "float64",
        "sepal_width_cm": "float64",
        "petal_length_cm": "float64",
        "petal_width_cm": "float64",
        "species": "string"
    }
)

# Make sure we have 150 instances
assert iris_df.shape == (150, 5)

# Split numeric features and label
feature_cols = [
    "sepal_length_cm",
    "sepal_width_cm",
    "petal_length_cm",
    "petal_width_cm"
]
features = iris_df[feature_cols].to_numpy(dtype="float32")
species = iris_df["species"].astype("string")

# Convert species to fixed-length byte strings for HDF5
species_bytes = species.to_numpy(dtype="S20")  # up to 20 characters

# Read original documentation files as plain text
with open(iris_names_path, "r", encoding="utf-8") as f:
    iris_names_text = f.read()

with open(index_path, "r", encoding="utf-8") as f:
    index_text = f.read()


# Step 2: Write HDF5 file
with h5py.File(h5_filename, "w") as f:
    # ---- File-level attributes (overall metadata) ----
    f.attrs["dataset_label"] = "Dataset II"
    f.attrs["title"] = "Iris Plants Database"
    f.attrs["creator_of_hdf5"] = "Your Name Here"
    f.attrs["original_creator"] = "R.A. Fisher"
    f.attrs["donor"] = "Michael Marshall (MARSHALL%PLU@io.arc.nasa.gov)"
    f.attrs["original_date"] = "1988-07"  # from iris.names
    f.attrs["description"] = (
        "Classic Iris dataset with 150 instances and 5 attributes: "
        "sepal length/width, petal length/width, and species class label."
    )
    f.attrs["number_of_instances"] = 150
    f.attrs["number_of_attributes"] = 5
    f.attrs["classes"] = np.array(
        ["Iris-setosa", "Iris-versicolor", "Iris-virginica"],
        dtype="S20"
    )
    f.attrs["license"] = (
        "Provided for research and educational use via the UCI "
        "Machine Learning Repository."
    )
    f.attrs["conversion_software"] = "Python (pandas + h5py)"
    f.attrs["conversion_date_utc"] = datetime.utcnow().isoformat() + "Z"

    # ---- Group for the main data ----
    g_data = f.create_group("iris")

    g_data.attrs["logical_structure"] = (
        "Tabular data with 150 rows. Each row is a flower instance; "
        "columns are four numeric features and one species label."
    )
    g_data.attrs["missing_values"] = "None"
    g_data.attrs["class_distribution"] = (
        "3 classes with 50 instances each: Iris-setosa, "
        "Iris-versicolor, Iris-virginica."
    )

    # Numeric features dataset
    d_features = g_data.create_dataset(
        "features",
        data=features,
        dtype="float32"
    )
    d_features.attrs["columns"] = np.array(feature_cols, dtype="S32")
    d_features.attrs["units"] = np.array(["cm", "cm", "cm", "cm"], dtype="S4")
    d_features.attrs["description"] = (
        "Four numeric predictive attributes: sepal length, sepal width, "
        "petal length, petal width (all in centimeters)."
    )

    # Species label dataset
    d_species = g_data.create_dataset(
        "species",
        data=species_bytes,
        dtype="S20"
    )
    d_species.attrs["description"] = (
        "Class label indicating iris species for each row in 'features'."
    )
    d_species.attrs["classes"] = np.array(
        ["Iris-setosa", "Iris-versicolor", "Iris-virginica"],
        dtype="S20"
    )
    d_species.attrs["row_alignment"] = (
        "Row i in 'species' corresponds to row i in 'features'."
    )

    # ---- Group for original documentation files (preservation of metadata) ----
    str_dtype = h5py.string_dtype(encoding="utf-8")

    g_docs = f.create_group("documentation")

    d_names = g_docs.create_dataset(
        "iris_names_text",
        data=iris_names_text,
        dtype=str_dtype
    )
    d_names.attrs["original_filename"] = "iris.names"
    d_names.attrs["description"] = (
        "Original documentation file containing title, sources, "
        "attribute information, summary statistics, and discrepancy notes."
    )

    d_index = g_docs.create_dataset(
        "index_text",
        data=index_text,
        dtype=str_dtype
    )
    d_index.attrs["original_filename"] = "index"
    d_index.attrs["description"] = (
        "Original index file from the repository listing iris-related files "
        "and their modification dates/sizes."
    )

    # Summary statistics from iris.names as attributes on features
    d_features.attrs["summary_statistics_source"] = "iris.names"
    d_features.attrs["sepal_length_min_max_mean_sd"] = np.array(
        [4.3, 7.9, 5.84, 0.83], dtype="float32"
    )
    d_features.attrs["sepal_width_min_max_mean_sd"] = np.array(
        [2.0, 4.4, 3.05, 0.43], dtype="float32"
    )
    d_features.attrs["petal_length_min_max_mean_sd"] = np.array(
        [1.0, 6.9, 3.76, 1.76], dtype="float32"
    )
    d_features.attrs["petal_width_min_max_mean_sd"] = np.array(
        [0.1, 2.5, 1.20, 0.76], dtype="float32"
    )

    # Discrepancy note captured from iris.names
    g_data.attrs["discrepancy_note"] = (
        "The data differ slightly from Fisher's original article: "
        "35th sample and 38th sample feature values corrected as noted "
        "in iris.names."
    )

print(f"Created HDF5 file: {os.path.abspath(h5_filename)}")
