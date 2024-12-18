import pandas as pd

# import test_prediction
from flask import Flask, render_template

app = Flask(__name__)


# fetch fixture
def fetch_fixture():
    pass


@app.route("/")
def mk_table():
    data = test_prediction.generate_ml_out()
    df = pd.DataFrame(data)
    html_table = df.to_html(classes="table table-striped shadow table-hover")
    return render_template("index.html", table=html_table)


if __name__ == "__main__":
    app.run(debug="True", port=5001)
