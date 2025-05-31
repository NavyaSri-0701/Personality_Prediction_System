from extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class SurveyResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    EXT = db.Column(db.Integer)
    EST = db.Column(db.Integer)
    AGR = db.Column(db.Integer)
    CSN = db.Column(db.Integer)
    OPN = db.Column(db.Integer)
    Technical_Skills = db.Column(db.Integer)
    Communication_Skills = db.Column(db.Integer)
    Experience_Years = db.Column(db.Integer)
    Education_Level = db.Column(db.Integer)
    Certifications = db.Column(db.Integer)
    Leadership_Score = db.Column(db.Integer)
    Adaptability_Score = db.Column(db.Integer)
    Analytical_Thinking = db.Column(db.Integer)
    Teamwork_Score = db.Column(db.Integer)
    Project_Management = db.Column(db.Integer)
    prediction = db.Column(db.String(100))
    access_code = db.Column(db.String(4))
    suggested_roles = db.Column(db.String(255))

    

class SurveyRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hr_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    access_code = db.Column(db.String(4), unique=True)



