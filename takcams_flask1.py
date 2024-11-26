from flask import Flask,render_template,request,jsonify
import os,json,datetime
from flask_wtf import FlaskForm
from wtforms import MultipleFileField,FileField,TextAreaField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
import takcams_ai
import takcams_storage
from dotenv import load_dotenv
import config
import takcams_schema

app = Flask(__name__)
app.config.from_object(config.Config)
app.ContextStore = takcams_storage.ContextStore()
app.session_log = []

class UploadFileForm(FlaskForm):
    prefiles = FileField('Pre-existing',validators=[InputRequired()])
    guidelines = FileField('Guidelines',validators=[])
    userprofile = FileField('User profile',validators=[])

class QueryForm(FlaskForm):
    question = TextAreaField('Question',validators=[InputRequired()])

@app.route('/clear_files',methods=["GET"])
def clear_files():
    app.ContextStore.clear()
    return index()

@app.route('/clear_log',methods=["GET"])
def clear_log():
    app.session_log=[]
    return index()

@app.route('/upload',methods=["GET","POST"])
def upload():
    form = UploadFileForm()
    if form.validate_on_submit():
        
        #app.ContextStore.clear()

        #prefiles
        pre_filenames = []        
        if 0: # if we allowed multiple files
            for afile in form.prefiles.data:
                if(afile.filename):
                    app.ContextStore.add_context(afile,'pre-existing')
                    file_name = secure_filename(afile.filename)
                    afile.save(file_name)
                    pre_filenames.append(file_name)
        else:
            pre = form.prefiles.data
            if pre:
                app.ContextStore.add_context(pre,'pre-existing')
                pre_name = secure_filename(pre.filename)
                pre_filenames.append(pre_name)


        #guidelines
        guideline_filenames = []
        if 0: # if we allowed multiple files
            for file in form.guidelines.data:
                if(file.filename):
                    app.ContextStore.add_context(file,'guideline')
                    file_name = secure_filename(file.filename)
                    file.save(file_name)
                    guideline_filenames.append(file_name)
        else:
            pre = form.guidelines.data
            if pre:
                app.ContextStore.add_context(pre,'guideline')
                pre_name = secure_filename(pre.filename)
                guideline_filenames.append(pre_name)
        
        #userprofile
        profile_name=''
        profile = form.userprofile.data
        if profile:
            app.ContextStore.add_context(profile,'user-profile')
            profile_name = secure_filename(profile.filename)
            profile.save(profile_name)


        return render_template('upload.html', form=form, contexts=app.ContextStore.contexts)        

    return render_template('upload.html', form=form,contexts=app.ContextStore.contexts)


@app.route('/',methods=["GET"])
@app.route('/query',methods=["GET","POST"])
def index():

    question=""
    answer=""
    form = QueryForm()
    alog=[]
    if form.validate_on_submit():
        question=form.question.data
        #datetime.datetime.now().strftime("%I:%M%p:%S on %B %d, %Y")
        #DEBUG
        answer='no answer available'
        item = { 'when': datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y"),
                'question': question, 'answer':answer}
        app.session_log.append(item)
        print(item)
        alog= app.session_log.copy()
        alog.reverse()


    return render_template('index.html', form=form,contexts=len(app.ContextStore.contexts),question=question, answer=answer, log=alog)

@app.route('/schema_test',methods=["GET"])
def schema_test():
    test = takcams_schema.TakcamsData_v1([],'david','david@email.com')
    test.set_user_input(1,'some user tip','some user question')
    test.set_user_tip(takcams_schema.raw_tip_example)
    test.set_system_suggestion()
    test.set_answer(takcams_schema.raw_answer_example)


    return '<pre>' + takcams_schema.toJSON(test) + '</pre><pre>' + takcams_schema.toJSON(json.loads(takcams_schema.procedure_example_str)) + '</pre>'


