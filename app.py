from flask import Flask, render_template, request, redirect, session, make_response
import numpy as np
import pickle
import random
from extensions import db
from models import User, SurveyResponse, SurveyRequest
import csv
from io import StringIO
from flask_mail import Mail, Message
from collections import Counter

app = Flask(__name__)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'navyasriparepalli@gmail.com'
app.config['MAIL_PASSWORD'] = 'zspu khtf sziw dxhw'

mail = Mail(app)

app.secret_key = "your_secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Navyatanu%403y@localhost/personality_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
with app.app_context():
    db.create_all()

# Load ML models
with open("scaler.pkl", "rb") as f:
    scaler = pickle.load(f)
with open("pca.pkl", "rb") as f:
    pca = pickle.load(f)
with open("kmeans.pkl", "rb") as f:
    kmeans = pickle.load(f)

cluster_map = {
    0: "Experienced Professionals",
    1: "Analytical Thinkers",
    2: "Team Players",
    3: "Adaptable Experts",
    4: "Creative Leaders",
    5: "Detail Oriented"
}
suggested_roles_map = {
    0: ["Senior Developer", "Technical Architect", "Project Manager"],
    1: ["Data Analyst", "Business Analyst", "Researcher", "Machine Learning Engineer"],
    2: ["HR Specialist", "Customer Support","Scrum Maaster", "Team Coordinator"],
    3: ["Operations Manager", "Field Engineer", "Scrum Master"],
    4: ["Product Manager", "UX Designer", "Innovation Strategist"],
    5: ["QA Engineer", "Compliance Officer", "Data Entry Specialist"]
}



questions = [
    {"name": "EXT_1", "text": "I feel comfortable being the center of attention."},
    {"name": "EXT_2", "text": "I make friends easily."},
    {"name": "EST_1", "text": "I get stressed out easily."},
    {"name": "EST_2", "text": "I often worry about things."},
    {"name": "AGR_1", "text": "I sympathize with others’ feelings."},
    {"name": "AGR_2", "text": "I take time out for others."},
    {"name": "CSN_1", "text": "I pay attention to details."},
    {"name": "CSN_2", "text": "I like order."},
    {"name": "OPN_1", "text": "I have a vivid imagination."},
    {"name": "OPN_2", "text": "I am full of ideas."},
    {"name": "Technical_Skills", "text": "I am confident in solving technical problems."},
    {"name": "Communication_Skills", "text": "I communicate ideas effectively."},
    {"name": "Experience_Years", "text": "I have many years of practical experience."},
    {"name": "Education_Level", "text": "I have a strong academic background."},
    {"name": "Certifications", "text": "I have earned multiple certifications."},
    {"name": "Leadership_Score", "text": "I enjoy taking the lead on projects."},
    {"name": "Adaptability_Score", "text": "I adjust quickly to changing situations."},
    {"name": "Analytical_Thinking", "text": "I enjoy solving complex problems."},
    {"name": "Teamwork_Score", "text": "I work well in team environments."},
    {"name": "Project_Management", "text": "I can manage multiple tasks effectively."}
]

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        new_user = User(
            username=request.form["username"],
            email=request.form["email"],
            password=request.form["password"],
            role=request.form["role"]
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        uname = request.form["username"]
        pwd = request.form["password"]
        user = User.query.filter_by(username=uname, password=pwd).first()
        if user:
            session["user_id"] = user.id
            session["user_role"] = user.role
            if user.role == "candidate":
                return redirect("/enter-code")
            elif user.role == "hr":
                return redirect("/dashboardhr")
            else:
                return "Unauthorized role"

        return "Invalid credentials"
    return render_template("login.html")

@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        uname = request.form["username"]
        pwd = request.form["password"]
        if uname == "admin" and pwd == "admin123":
            requests = SurveyRequest.query.all()
            users = User.query.all()
            return render_template("admin_dashboard.html", requests=requests, users=users)
        else:
            return "Invalid admin credentials"
    return render_template("admin_login.html")


@app.route("/approve-request/<int:request_id>")
def approve_request(request_id):
    req = SurveyRequest.query.get(request_id)
    if req and not req.approved:
        req.approved = True
        existing_codes = [r.access_code for r in SurveyRequest.query.all()]
        while True:
            code = str(random.randint(1000, 9999))
            if code not in existing_codes:
                break
        req.access_code = code

        db.session.commit()
    return redirect("/admin-login")

@app.route("/dashboardhr", methods=["GET", "POST"])
def dashboard_hr():
    if "user_id" in session and session.get("user_role") == "hr":
        user = User.query.get(session["user_id"])
        existing_request = SurveyRequest.query.filter_by(hr_id=user.id).first()

        if request.method == "POST" and not existing_request:
            new_request = SurveyRequest(hr_id=user.id)
            db.session.add(new_request)
            db.session.commit()
            return redirect("/dashboardhr")

        candidates = []
        cluster_labels = []
        cluster_counts = []

        if existing_request and existing_request.approved:
            # Get candidates who took surveys linked to this HR's access code
            candidates = SurveyResponse.query.join(User).filter(
                SurveyResponse.user_id == User.id,
                SurveyResponse.access_code == existing_request.access_code
            ).all()

            cluster_counts_raw = Counter([c.prediction for c in candidates])
            cluster_labels = list(cluster_counts_raw.keys())
            cluster_counts = list(cluster_counts_raw.values())

        return render_template(
            "dashboardhr.html",
            user=user,
            request_status=existing_request,
            candidates=candidates,
            cluster_labels=cluster_labels,
            cluster_counts=cluster_counts
        )
    return redirect("/login")

@app.route("/enter-code", methods=["GET", "POST"])
def enter_code():
    if "user_id" not in session or session.get("user_role") != "candidate":
        return redirect("/login")
    if request.method == "POST":
        code = request.form["access_code"]
        req = SurveyRequest.query.filter_by(access_code=code, approved=True).first()
        if req:
            session["access_code_valid"] = True
            session["access_code"] = code
            return redirect("/survey")
        else:
            return render_template("enter_code.html", error="Invalid or unapproved access code.")
    return render_template("enter_code.html")

@app.route("/survey", methods=["GET", "POST"])
def survey():
    if "user_id" not in session or session.get("user_role") != "candidate" or not session.get("access_code_valid"):
        return redirect("/login")

    prediction = None
    suggested_roles = []
    if request.method == "POST":
        try:
            responses = request.form
            scores = {
                "EXT": int(responses["EXT_1"]) + int(responses["EXT_2"]),
                "EST": int(responses["EST_1"]) + int(responses["EST_2"]),
                "AGR": int(responses["AGR_1"]) + int(responses["AGR_2"]),
                "CSN": int(responses["CSN_1"]) + int(responses["CSN_2"]),
                "OPN": int(responses["OPN_1"]) + int(responses["OPN_2"]),
                "Technical_Skills": int(responses["Technical_Skills"]) * 10,
                "Communication_Skills": int(responses["Communication_Skills"]) * 10,
                "Experience_Years": int(responses["Experience_Years"]) * 2,
                "Education_Level": int(responses["Education_Level"]),
                "Certifications": int(responses["Certifications"]),
                "Leadership_Score": int(responses["Leadership_Score"]) * 10,
                "Adaptability_Score": int(responses["Adaptability_Score"]) * 10,
                "Analytical_Thinking": int(responses["Analytical_Thinking"]) * 10,
                "Teamwork_Score": int(responses["Teamwork_Score"]) * 10,
                "Project_Management": int(responses["Project_Management"]) * 10
            }

            input_features = np.array(list(scores.values())).reshape(1, -1)
            scaled = scaler.transform(input_features)
            reduced = pca.transform(scaled)
            cluster = kmeans.predict(reduced)[0]
            prediction = cluster_map[cluster]
            suggested_roles = suggested_roles_map.get(cluster, [])

            survey_response = SurveyResponse(
                user_id=session["user_id"],
                access_code=session["access_code"],  # Store access code in SurveyResponse for linkage
                **scores,
                prediction=prediction,
                suggested_roles=", ".join(suggested_roles)
            )
            db.session.add(survey_response)
            db.session.commit()

            # Notify HR via email
            req = SurveyRequest.query.filter_by(access_code=session.get("access_code")).first()
            if req:
                hr_user = User.query.get(req.hr_id)
                if hr_user and hr_user.email:
                    msg = Message(
                        "New Survey Completed",
                        sender="navyasriparepalli@gmail.com",
                        recipients=[hr_user.email]
                    )
                    msg.body = f"A candidate has completed the survey with cluster prediction: {prediction}."
                    mail.send(msg)

        except Exception as e:
            prediction = f"Error: {e}"

    return render_template("survey.html", questions=questions, prediction=prediction, suggested_roles=suggested_roles)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
@app.route("/download-candidate-report", methods=["GET"])
def download_candidate_report():
    if "user_id" not in session or session.get("user_role") != "candidate":
        return redirect("/login")

    response = SurveyResponse.query.filter_by(user_id=session["user_id"]).first()
    if not response:
        return "No survey response found for this candidate."

    si = StringIO()
    cw = csv.writer(si)
    header = ["EXT", "EST", "AGR", "CSN", "OPN", "Technical_Skills", "Communication_Skills",
              "Experience_Years", "Education_Level", "Certifications", "Leadership_Score",
              "Adaptability_Score", "Analytical_Thinking", "Teamwork_Score", "Project_Management",
              "Prediction","Suggested Roles"]
    cw.writerow(header)
    cw.writerow([
        response.EXT, response.EST, response.AGR, response.CSN, response.OPN,
        response.Technical_Skills, response.Communication_Skills, response.Experience_Years,
        response.Education_Level, response.Certifications, response.Leadership_Score,
        response.Adaptability_Score, response.Analytical_Thinking, response.Teamwork_Score,
        response.Project_Management, response.prediction,response.suggested_roles
    ])

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=your_survey_result.csv"
    output.headers["Content-type"] = "text/csv"
    return output


@app.route("/download-hr-report", methods=["GET"])
def download_hr_report():
    if "user_id" not in session or session.get("user_role") != "hr":
        return redirect("/login")

    hr_id = session["user_id"]
    req = SurveyRequest.query.filter_by(hr_id=hr_id, approved=True).first()
    if not req:
        return "No approved survey for this HR."

    # Join SurveyResponse and User filtering by access_code
    responses = db.session.query(SurveyResponse, User).join(User, User.id == SurveyResponse.user_id).filter(
        SurveyResponse.access_code == req.access_code
    ).all()

    si = StringIO()
    cw = csv.writer(si)
    header = ["Candidate Username", "EXT", "EST", "AGR", "CSN", "OPN", "Technical_Skills", "Communication_Skills",
              "Experience_Years", "Education_Level", "Certifications", "Leadership_Score", "Adaptability_Score",
              "Analytical_Thinking", "Teamwork_Score", "Project_Management", "Prediction","Suggested Roles"]
    cw.writerow(header)

    for resp, user in responses:
        row = [
            user.username,
            resp.EXT, resp.EST, resp.AGR, resp.CSN, resp.OPN,
            resp.Technical_Skills, resp.Communication_Skills, resp.Experience_Years,
            resp.Education_Level, resp.Certifications, resp.Leadership_Score,
            resp.Adaptability_Score, resp.Analytical_Thinking, resp.Teamwork_Score,
            resp.Project_Management, resp.prediction,resp.suggested_roles
        ]
        cw.writerow(row)

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=hr_survey_results.csv"
    output.headers["Content-type"] = "text/csv"
    return output

if __name__ == "__main__":
    app.run(debug=True)
