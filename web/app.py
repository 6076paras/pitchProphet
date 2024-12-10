import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)


# fetch fixture
def fetch_fixture():
    pass


@app.route("/")
def mk_table():
    data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"],
    }
    df = pd.DataFrame(data)
    html_table = df.to_html(classes="table table-striped")

    return render_template("index.html", table=html_table)


if __name__ == "__main__":
    app.run(debug=True)
