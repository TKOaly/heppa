from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from flask_babel import lazy_gettext

class CandidateForm(FlaskForm):
    name = StringField(lazy_gettext("Candidate name"))
    url = StringField(lazy_gettext("Candidate URL, e.g. IMDB page"))
    description = TextAreaField(lazy_gettext("Description"))

    class Meta:
        csrf = False

class EditForm(FlaskForm):
    name = StringField(lazy_gettext("Candidate name"))
    url = StringField(lazy_gettext("Candidate URL"))
    description = TextAreaField(lazy_gettext("Description"))
    selected = BooleanField(lazy_gettext("Selected"))
    
    class Meta:
        csrf = False