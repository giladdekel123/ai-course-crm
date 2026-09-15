from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional

from app.constants import DELIVERY_FORMATS


class CourseForm(FlaskForm):
    course_name = StringField("Course Name", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Optional()])
    start_date = DateField("Start Date", validators=[DataRequired()])
    duration = StringField("Duration", validators=[DataRequired(), Length(max=50)])
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)])
    capacity = IntegerField("Capacity", validators=[DataRequired(), NumberRange(min=1)])
    delivery_format = SelectField(
        "Delivery Format", choices=[(d, d) for d in DELIVERY_FORMATS], validators=[DataRequired()],
    )
    submit = SubmitField("Save")
