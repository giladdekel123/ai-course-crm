from datetime import date

from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional

from app.constants import (
    EDUCATION_LEVELS,
    LEAD_STATUSES,
    OCCUPATIONS,
    PAYMENT_METHODS,
    REASONS_FOR_INTEREST,
    SOURCES,
    TECHNICAL_EXPERIENCE_LEVELS,
)


class LeadForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=200)])
    phone = StringField("Phone", validators=[Optional(), Length(max=50)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=200)])
    age = IntegerField("Age", validators=[Optional(), NumberRange(min=1, max=120)])
    city = StringField("City", validators=[Optional(), Length(max=200)])
    occupation = SelectField("Occupation", choices=[(o, o) for o in OCCUPATIONS], validators=[DataRequired()])
    education = SelectField("Education", choices=[(e, e) for e in EDUCATION_LEVELS], validators=[DataRequired()])
    technical_experience = SelectField(
        "Technical Experience",
        choices=[(t, t) for t in TECHNICAL_EXPERIENCE_LEVELS],
        validators=[DataRequired()],
    )
    reason_for_interest = SelectField(
        "Reason for Interest", choices=[(r, r) for r in REASONS_FOR_INTEREST], validators=[DataRequired()],
    )
    source = SelectField("Source", choices=[(s, s) for s in SOURCES], validators=[DataRequired()])
    course_interest_id = SelectField("Course Interest", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save")


class StatusForm(FlaskForm):
    status = SelectField("Status", choices=[(s, s) for s in LEAD_STATUSES], validators=[DataRequired()])
    submit = SubmitField("Update Status")


class ConvertForm(FlaskForm):
    course_id = SelectField("Course", coerce=int, validators=[DataRequired()])
    enrollment_date = DateField("Enrollment Date", validators=[DataRequired()], default=date.today)
    amount_paid = DecimalField("Amount Paid", validators=[DataRequired(), NumberRange(min=0)])
    payment_method = SelectField(
        "Payment Method", choices=[(p, p) for p in PAYMENT_METHODS], validators=[DataRequired()],
    )
    submit = SubmitField("Convert to Registration")
