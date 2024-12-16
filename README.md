
Welcome to the CustomFootball. This documentation will guide you through the setup, usage, and development of the project.

## Table of Contents

1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Data Processing](#data-processing)
8. [Model Training](#model-training)
7. [Web Application](#web-application)
8. [Testing](#testing)
9. [Contributing](#contributing)


## Introduction

The Custom FPL project is designed to provide advanced data analysis and predictive modeling for the outcome of football matches. It includes data scraping, preprocessing, model training, and a web application.

## Project Structure

```
.gitignore
.mypy_cache/
.pre-commit-config.yaml
README.md
costomFPL/
    .mypy_cache/
    __init__.py
    __pycache__/
    config/
        dataVars.yaml
    data/
        EDA/
        __init__.py
        __pycache__/
        fbref/
        football_data_uk/
        pre_processing/
    models/
        __init__.py
        notebook/
        xgb_model.pkl
    scripts/
        __init__.py
    utils/
poetry.lock
pyproject.toml
tests/
    __init__.py
    __pycache__/
    test_prediction.py
    test_scrapper.py
web/
    app.py
    static/
        assets/
        css/
        js/
    templates/
        index.html
        index_temp.html
```

## Installation

### Prerequisites

- Python 3.8+
- Poetry (for dependency management)

### Steps

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/custom-fpl.git
    cd custom-fpl
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

### Data Preprocessing

To preprocess the scraped data, use the [`pre_process.py`](command:_github.copilot.openRelativePath?%5B%22costomFPL%2Fdata%2Fpre_processing%2Fpre_process.py%22%5D "costomFPL/data/pre_processing/pre_process.py") script:
```sh
pre-process
```

### Model Training

To train the predictive model, run the following script:
```sh
python costomFPL/models/train_model.py
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