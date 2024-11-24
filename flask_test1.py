from flask import Flask,render_template,request,jsonify
import os
from flask_wtf import FlaskForm
from wtforms import MultipleFileField,FileField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
import takcams_ai
import takcams_storage
from dotenv import load_dotenv
import config

app = Flask(__name__)
app.config.from_object(config.Config)
app.ContextStore = takcams_storage.ContextStore()


class UploadFileForm(FlaskForm):
    prefiles = MultipleFileField('Pre-existing',validators=[InputRequired()])
    guidelines = MultipleFileField('Guidelines',validators=[])
    userprofile = FileField('User profile',validators=[])


@app.route('/clear',methods=["GET"])
def clear():
    app.ContextStore.clear()
    return index()


@app.route('/upload',methods=["GET","POST"])
def upload():
    form = UploadFileForm()
    if form.validate_on_submit():
        
        #app.ContextStore.clear()

        #prefiles
        pre_filenames = []
        for afile in form.prefiles.data:
            if(afile.filename):
                app.ContextStore.add_context(afile,'pre-existing')
                file_name = secure_filename(afile.filename)
                afile.save(file_name)
                pre_filenames.append(file_name)
        
        #guidelines
        guideline_filenames = []
        for file in form.guidelines.data:
            if(file.filename):
                app.ContextStore.add_context(file,'guideline')
                file_name = secure_filename(file.filename)
                file.save(file_name)
                guideline_filenames.append(file_name)
        
        #userprofile
        profile_name=''
        profile = form.userprofile.data
        if profile:
            app.ContextStore.add_context(profile,'user-profile')
            profile_name = secure_filename(profile.filename)
            profile.save(profile_name)


        return render_template('upload.html', form=form, contexts=app.ContextStore.contexts)        

    return render_template('upload.html', form=form)


@app.route('/',methods=["GET"])
@app.route('/index',methods=["GET"])
def index():


    return render_template('index.html', contexts=app.ContextStore.contexts)

