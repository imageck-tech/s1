import os

from dotenv import load_dotenv
from flask import Flask, render_template, request
from supabase import create_client

load_dotenv()

app = Flask(__name__)

supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None


def calc_bmi(height_cm: float, weight_kg: float) -> float:
    height_m = height_cm / 100
    return weight_kg / (height_m ** 2)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "저체중"
    elif bmi < 23:
        return "정상"
    elif bmi < 25:
        return "과체중"
    else:
        return "비만"


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    if request.method == "POST":
        try:
            name = request.form["name"].strip()
            height = float(request.form["height"])
            weight = float(request.form["weight"])
            if not name or height <= 0 or weight <= 0:
                raise ValueError
            bmi = calc_bmi(height, weight)
            result = {
                "name": name,
                "bmi": round(bmi, 2),
                "category": bmi_category(bmi),
                "height": height,
                "weight": weight,
            }
            if supabase:
                try:
                    supabase.table("bmi_records").insert({
                        "name": name,
                        "height": height,
                        "weight": weight,
                        "bmi": result["bmi"],
                        "category": result["category"],
                    }).execute()
                except Exception:
                    pass
        except (ValueError, KeyError):
            error = "이름을 입력하고, 키와 몸무게는 0보다 큰 숫자로 입력해주세요."

    return render_template("index.html", result=result, error=error)


if __name__ == "__main__":
    app.run(debug=True)
