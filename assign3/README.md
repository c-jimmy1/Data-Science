# 💵 Modeling U.S. Credit Response to Rising Interest Rates
The U.S. is facing historically high household debt alongside rapidly rising interest rates, putting pressure on consumers who rely on credit cards, auto loans, and student loans to manage everyday expenses. In this project, we explore how changes in the Federal Funds Rate influence different types of consumer borrowing so we can better understand which segments of debt are most sensitive to monetary policy and why these shifts matter for economic stability.

## How to Run
### Step 1: Download Miniconda
https://www.anaconda.com/download

### Step 2: Create Conda Environment

cd to the assign3 folder (`cd assign3`) and run the below:
```
conda env create -f environment.yaml
```

### Step 3: Activate Conda Environment
```
conda activate consumer-credit-analysis
```

### Step 4: Get FRED API Key Create Secrets File
1. Get a FRED API Key by creating a free account. Instructions here: https://fred.stlouisfed.org/docs/api/api_key.html
2. In the `assign3/` folder, create a `secrets.yaml` file. I.e. `assign3/secrets.yaml`. 
Inside the secrets.yaml file, add a line with your FRED API Key.
```
FRED_API_KEY:"XXXXXXXXXXXXXXXXXXXXXXX"
```

### Step 5: Switch VS Code Python Interpreter to `consumer-credit-analysis`
1. Open Command Menu: `Ctrl-Shift-P`
2. Type in and Click: `Python: Select Interpreter`
3. Select `consumer-credit-analysis` as your interpreter

### Step 6: Run Jupyter Notebook
```
assign3.ipynb
```


## Data Sources

- https://fred.stlouisfed.org/series/TOTALSL
- https://fred.stlouisfed.org/series/REVOLSL
- https://fred.stlouisfed.org/series/NONREVSL
- https://fred.stlouisfed.org/series/FEDFUNDS
