import sys
from pathlib import Path

import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)


def get_predictions() -> pd.DataFrame:
    """load match predictions from CSV file."""
    file_path = Path(
        "/Users/paraspokharel/Programming/pitchProphet/web/static/assets/tables/Premier-League_week_10_predictions.csv"
    )

    df = pd.read_csv(file_path)
    # Round probabilities to 3 decimal places
    prob_columns = [col for col in df.columns if col.startswith("p(")]
    df[prob_columns] = df[prob_columns].round(3)

    return df


@app.route("/")
def mk_table():
    df = get_predictions()
    html_table = df.to_html(
        classes="table table-striped shadow table-hover", index=False
    )
    return render_template("index.html", table=html_table)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
