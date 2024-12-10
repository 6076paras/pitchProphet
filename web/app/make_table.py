import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)


# fetch fixture
def fetch_fixture():
    pass


# html table
@app.route("/")
def mk_table(data=None):
    data = {
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [25, 30, 35],
        "City": ["New York", "Los Angeles", "Chicago"],
    }
    df = pd.DataFrame(data)
    html_table = df.to_html()
    return render_template(r"index.html")


if __name__ == "__main__":
    app.run(debug=True)
