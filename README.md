Welcome to the pitchProphet. This documentation will guide you through the setup, usage, and development of the project.


# Project Status 🚧

This project is under active development, with features being added and updated regularly. While predictions currently rely on team-level features, the ultimate goal of this project is to experiement and research with player-level data and advanced ML modeling that capturues the symmetry and patters of the data for more accurate predictions.


## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Usage](#usage)
    - [Data Scrapping](#data-scrapping)
    - [Pre-processing](#pre-processing)
    - [Training](#training)  
4. [Web Application](#web-application)
5. [Testing](#testing)
6. [Contributing](#contributing)

## Introduction

**PitchProphet** is a football match forecasting tool that predicts the outcome probabilities for upcoming fixtures in all major European leagues. You can explore the prediction results on the web application [here](http://ec2-35-170-244-111.compute-1.amazonaws.com/).

### Current Features
- **Data Scraping**: Collects match-related data for teams and players from FBref.com across all major european leagues.
- **Data Processing**: Prepares the scraped data for training ML models.
- **Predictive Modeling**: Trains a machine learning model to predict win probabilities for upcoming matches.
- **Web Application**: Displays the prediction results in an easy-to-use web interface.

## Installation

### Prerequisites

- Python 3.13+
- Poetry (for dependency management)

### Steps

1. Clone the repository:

   ```sh
   git clone git@github.com:6076paras/pitchProphet.git
   cd pitchProphet
   ```

2. Install dependencies:

   ```sh
   poetry install
   ```

3. Activate the virtual environment:
   ```sh
   poetry shell
   ```

## Usage

### Data Scraping

To scrape data from FBref, run the following script:

```sh
get-data
```
The configurations for the scrapping can be set in the `config.yaml` with "scrapper" key. For example,
```yaml
...
scraper:
  season: 2017-2018
  league: Premier-League
  player_data: false
...
```
### Pre-processing

To preprocess the scraped data, use the [`pre_process.py`](command:_github.copilot.openRelativePath?%5B%22pitchProphet%2Fdata%2Fpre_processing%2Fpre_process.py%22%5D "pitchProphet/data/pre_processing/pre_process.py") script:

```sh
pre-process
```

The pre-processing step transforms raw match data into features suitable for model training. For each match and team, the system calculates descriptive statistics (aggregation, trend, variance) of team performance metrics (e.g., goals, xG, shots) from their previous N matches. This creates a rich set of features that capture both teams' recent form and performance variability.  You can also spefify which of the features you want to pre-process from in the configuration file.

Configuration for feature extraction can be set in the `config.yaml` under the "processing" key:
```yaml
processing:
  last_n_matches: 5
  x_vars:
    - Gls     # goals scored
    - xG      # expected goals
    - Sh      # shots
    - SoT     # shots on target
    # ... other features
```

### Model Development

The model development process is documented in Jupyter notebooks located in the `pitchProphet/models/notebook/` directory:

- `model_classic_1.ipynb`: Initial model development using classical machine learning approaches
  - Data preparation and feature engineering
  - Model training and evaluation
  - Performance metrics and analysis with plots
  - Model serialization (.pkl file)

To run the notebooks:
```bash
jupyter notebook pitchProphet/models/notebook/
```
### Inference Pipeline

The inference pipeline automatically processes upcoming fixtures and generates predictions that is fed to the web application. This involves several steps:

1. **Matchweek Detection**:
   - The system tracks current matchweek dates for each league using a CSV file containing fixture schedules
   - For each league, it checks if the current date falls outside the active matchweek period (between first and last game dates)
   - Only processes leagues that aren't currently in an active matchweek

2. **Feature Generation**:
   - For each upcoming fixture:
     - Retrieves last N matches for both home and away teams
     - Calculates descriptive statistics (aggregation, trend, variance) for each team's performance metrics
     - Combines home and away team features into a format suitable for model inference

3. **Model Prediction**:
   - Processes the prepared features through the trained XGBoost model
   - Generates probability scores for three possible outcomes:
     - Home Win
     - Draw
     - Away Win

This processed data feeds directly into the web application, which displays the predictions for upcoming fixtures in each league.

### Web Application

To start the web application, run:

```sh
python web/app.py
```

Then, open your browser and navigate to `http://localhost:5000`.

## Testing

To run the tests, use the following command:

```sh
pytest
```

Test files are located in the [`tests/`](command:_github.copilot.openRelativePath?%5B%22tests%2F%22%5D "tests/") directory.

## Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Install pre-commit hooks:
   ```sh
   pre-commit install
   ```
5. Commit your changes (`git commit -am 'Add new feature'`).
6. Push to the branch (`git push origin feature-branch`).
7. Create a new Pull Request.
