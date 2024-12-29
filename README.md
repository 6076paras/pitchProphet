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
    -  
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

The pre-processing step transforms raw match data into features suitable for model training. For each match, the system calculates descriptive statistics (aggregation, trend, variance) of team performance metrics (e.g., goals, xG, shots) from their previous N matches. This creates a rich set of features that capture both teams' recent form and performance variability.

Configuration for feature extraction can be set in the `config.yaml` under the "processing" key:
```yaml
processing:
  x_vars:
    - Gls     # Goals scored
    - xG      # Expected goals
    - Sh      # Shots
    - SoT     # Shots on target
    # ... other features
```

### Model Training

To train the predictive model, run the following script:

```sh
python pitchProphet/models/train_model.py
```

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
