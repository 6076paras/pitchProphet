from flask import Flask, render_template

from web.utils.utils import get_predictions

app = Flask(__name__)


@app.route("/")
def mk_table():
    """render the main page with prediction tables for all leagues."""
    league_data = get_predictions()
    return render_template("index.html", league_data=league_data)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
