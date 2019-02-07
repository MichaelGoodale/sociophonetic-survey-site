import os
import json

from flask import Flask, render_template, redirect, url_for, Blueprint, session, request, current_app, abort
from wtforms import BooleanField, StringField, PasswordField, validators
from werkzeug.utils import secure_filename
from uuid import uuid1

from .db import db_session
from .models import User, Survey, SurveyResponse
from .utils import generate_survey_form

bp = Blueprint('survey', __name__)
surveys = {}

def get_survey(survey_name):
    if survey_name in surveys:
        return surveys[survey_name]

    survey_path = os.path.join(current_app.instance_path, "surveys", survey_name)
    if not os.path.isfile(survey_path):
        return None
    surveys[survey_name]= generate_survey_form(survey_path)

    if db_session.query(Survey).filter(Survey.survey_name == survey_name).first() is None:
        with open(survey_path, "r") as f:
            survey_json_string = f.read()
        survey = Survey(survey_name, survey_json_string)
        db_session.add(survey)
        db_session.commit()
    return surveys[survey_name]

def get_survey_response(user, survey_name):
    survey = db_session.query(Survey).filter(Survey.survey_name == survey_name).first()
    if survey is None:
        return None
    survey_response = db_session.query(SurveyResponse).filter((SurveyResponse.user_id == user.uuid) & (SurveyResponse.survey_id == survey.id)).first()
    if survey_response is None:
        #Construct response if it's not there
        survey_response = json.loads(survey.survey)
        for page in survey_response["pages"]:
            for q in page:
                q.pop("answers", 0)
        survey_response = SurveyResponse(json.dumps(survey_response))
        user.responses.append(survey_response)
        survey.responses.append(survey_response)
        db_session.commit()
    return survey_response

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/survey/<survey_name>/<int:page>', methods=['GET', 'POST'])
def survey(survey_name, page):
    form = get_survey(survey_name)
    if form is None or page < 0 or page >= len(form):
        abort(404)
    if request.method == 'GET' and 'user_id' not in session:
        session['user_id'] = str(uuid1())
        user = User(session['user_id'])
        db_session.add(user)
        db_session.commit()
    if request.method == 'POST':
        if request.form["submit"] == "Previous page":
            return redirect(url_for("survey.survey", survey_name=survey_name, page=page-1))
        elif request.form["submit"] == "Next page":
            return redirect(url_for("survey.survey", survey_name=survey_name, page=page+1))
        elif request.form["submit"] == "Submit":
            pass
        else:
            abort(404)
    return render_template('survey.html', survey_name=survey_name, form=form[page](), \
                                         page=page, number_pages=len(form))

@bp.route('/upload_audio/<survey_name>/<recording>', methods=['POST'])
def upload_audio(survey_name, recording):
    user = db_session.query(User).filter(User.uuid == session['user_id']).first()
    if user is None:
        raise ValueError("No u")
        abort(404)

    survey_response = get_survey_response(user, survey_name)
    recording_file = request.files["recording"]
    file_path = os.path.join(current_app.instance_path, '{}.wav'.format(uuid1()))
    recording_file.save(file_path)

    found = False
    response = json.loads(survey_response.response)
    for page in response["pages"]:
        for q in page:
            if q["name"] == recording:
                q["answer"] = file_path
                found = True
                break
        if found:
            break

    if not found:
        raise ValueError("No q")
        abort(404)
        #That isn't a q of survey_name

    survey_response.response = json.dumps(response)
    db_session.commit()
    return "we did it"
