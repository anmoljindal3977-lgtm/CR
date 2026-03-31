# Project Execution Flow

Here is the step-by-step guide to run the credit underwriting system.

### 1. Setup
**What it does:** Creates a clean workspace and sets up a virtual Python environment so packages don't conflict with your system.
**Command:**
```bash
git clone <repository_url>
cd Credit-Risk-Model-UnderwritingRules-Agentic
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```
**Expected output:** A new virtual environment is created, and your terminal prompt shows `(venv)` indicating it is active.

### 2. Install dependencies
**What it does:** Installs all the required Python packages needed by the project (like pandas, scikit-learn, and lightgbm).
**Command:**
```bash
pip install -r requirements.txt
```
**Expected output:** A stream of logs showing packages being downloaded and installed, ending with a success message.

### 3. Add dataset
**What it does:** Prepares the data directory to hold your training dataset.
**Command:**
```bash
mkdir -p data
# Place your application_train.csv file inside this data folder
```
**Expected output:** A `data` folder is created at the root of your project ready to store the CSV file.

### 4. Train model
**What it does:** Loads and cleans the dataset, trains the LightGBM risk model, and saves the trained model so the risk agent can use it later.
**Command:**
```bash
python load_data.py
```
**Expected output:** Prints out the first few rows of data, the shape of the dataset, and the model's Accuracy and AUC scores. It also saves the model file into `models/risk_model.pkl`.

### 5. Run individual agents (optional)
**What it does:** Lets you test a single piece of the system (like the data validator) directly without running the whole pipeline.
**Command:**
```bash
python -c "from agents.data_validator import validate_application; print(validate_application({'SK_ID_CURR': 123, 'AMT_CREDIT': 5000, 'AMT_INCOME_TOTAL': 10000}))"
```
**Expected output:** Prints a short dictionary showing the output for just that agent (e.g., whether the test application passed or failed).

### 6. Run full pipeline
**What it does:** Puts a sample application through the entire process: validation, alternative credit scoring, risk prediction, and the final decision.
**Command:**
```bash
python main.py
```
**Expected output:** Prints a large JSON object to the terminal. This includes the results from each individual agent along with a "trace" showing the step-by-step execution.

### 7. Run scenario testing
**What it does:** Tests the pipeline against various predefined cases like a happy path, high risk, and suspected fraud.
**Command:**
```bash
python run_scenarios.py
```
**Expected output:** Runs silently but generates two new files in the `deliverables/` folder: `scenario_test_results.json` and a markdown table `scenario_test_results_table.md`.


---

# Where to Use Outputs in Design Document

1. **Validator Output**
   → paste in "Agents Overview" section

2. **Alt Credit Output**
   → paste in "Tools / Feature Engineering" section

3. **Risk Model Output (p_default)**
   → paste in "Model Training" section

4. **Decision Output**
   → paste in "Decision Logic" section

5. **Full Pipeline Output (JSON)**
   → paste in "System Architecture / Pipeline" section

6. **Scenario Results Table**
   → paste in "Scenario Testing" section

7. **Trace Log**
   → paste in "Observability & Tracing" section

8. **LLM Explanation Output**
   → paste in "LLM / Explanation Layer" section

---

# Output Extraction Guide

Here is exactly where to find the outputs, which file generates them, the command to run, and how to copy the results:

- **Validator Output**
  - **Where to find it:** Inside the full pipeline output or by testing the agent directly.
  - **Which file generates it:** `agents/data_validator.py`
  - **Which command to run:** `python main.py`
  - **How to copy:** Copy the dictionary block under the `"validator"` key in the printed output.

- **Alt Credit Output**
  - **Where to find it:** Inside the full pipeline output.
  - **Which file generates it:** `agents/alt_credit.py`
  - **Which command to run:** `python main.py`
  - **How to copy:** Copy the dictionary block under the `"alt_credit"` key.

- **Risk Model Output**
  - **Where to find it:** Inside the full pipeline output.
  - **Which file generates it:** `agents/risk_model.py`
  - **Which command to run:** `python main.py`
  - **How to copy:** Copy the dictionary block under the `"risk"` key (this section contains the `p_default` value).

- **Decision Output**
  - **Where to find it:** Inside the full pipeline output.
  - **Which file generates it:** `agents/decision_engine.py`
  - **Which command to run:** `python main.py`
  - **How to copy:** Copy the dictionary block under the `"decision"` key from the terminal.

- **Full Pipeline Output (JSON)**
  - **Where to find it:** Printed directly to your terminal.
  - **Which file generates it:** `main.py`
  - **Which command to run:** `python main.py`
  - **How to copy:** Highlight and copy the entire JSON dictionary that gets printed.

- **Scenario Results Table**
  - **Where to find it:** Inside the deliverables folder.
  - **Which file generates it:** `run_scenarios.py`
  - **Which command to run:** `python run_scenarios.py`
  - **How to copy:** Open `deliverables/scenario_test_results_table.md` in your text editor and copy the markdown table inside.

- **Trace Log**
  - **Where to find it:** At the end of the full pipeline output.
  - **Which file generates it:** `orchestrator/pipeline.py`
  - **Which command to run:** `python main.py`
  - **How to copy:** Look for the `"trace"` key in the printed JSON and copy the entire list of steps.

- **LLM Explanation Output**
  - **Where to find it:** Printed to the terminal when requesting an explanation.
  - **Which file generates it:** `orchestrator/explanation.py`
  - **Which command to run:** Since there is no main block in this file, use a quick shell command: `python -c "from orchestrator.explanation import generate_explanation; print(generate_explanation({'risk': {'p_default': 0.1}, 'alt_credit': {'alt_credit_score': 0.8}, 'decision': {'decision': 'APPROVE'}}))"` (Ensure you have Ollama running locally first).
  - **How to copy:** Copy the human-readable text paragraph printed in your terminal.
