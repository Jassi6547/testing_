from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from source.patent_matching import *
import logging
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

## Create a Form for Id's

app.config['SECRET_KEY'] = "YaHoooo"


@app.context_processor
def base():
    form = IdForm()
    return dict(form=form)


class IdForm(FlaskForm):
    id1 = StringField("Enter Patent id", validators=[DataRequired()])
    id2 = StringField("Enter Patent id", validators=[DataRequired()])
    submit = SubmitField("Submit")


@app.route('/ids', methods=['GET', 'POST'])
def ids():
    id1 = None
    id2 = None
    form = IdForm()
    if form.submit.validators:
        id1 = form.id1.data
        id2 = form.id2.data
        form.id1.data = ""
        form.id2.data = ""
    return render_template('ids_form.html', id1=id1, id2=id2, form=form)


@app.route('/')
def home():
    return render_template('index.html')


# @app.route('/info', methods=['POST'])
# def info():
#     id1 = request.form.get('id1')
#     id2 = request.form.get('id2')
#     info1, status = get_claims(id1)
#     list_info1 = list_to_dict_with_custom_keys(get_claim_list(info1)) if status == API_SUCCESS else []
#
#     info2, status2 = get_claims(id2)
#     list_info2 = list_to_dict_with_custom_keys(get_claim_list(info2)) if status2 == API_SUCCESS else []
#     result = compare_claims(get_claim_list(info1), get_claim_list(info2))
#     similarity_per = (len(result) / max(len(list_info1), len(list_info2)) * 100)
#     if similarity_per >= 75:
#         flash("Almost Similar Patents", "success")
#     elif similarity_per >= 50:
#         flash("Partial Similar Patents", "warning")
#     else:
#         flash("Not Similar", "danger")
#     return render_template('index.html', id1=id1, id2=id2, info1=list_info1, info2=list_info2, result=result)

@app.route('/info', methods=['POST'])
def info():
    form = IdForm()
    if form.validate_on_submit():
        id1 = form.id1.data
        id2 = form.id2.data
        info1, status = get_claims(id1)
        list_info1 = list_to_dict_with_custom_keys(get_claim_list(info1)) if status == API_SUCCESS else []
        info2, status2 = get_claims(id2)
        list_info2 = list_to_dict_with_custom_keys(get_claim_list(info2)) if status2 == API_SUCCESS else []
        result = compare_claims(get_claim_list(info1), get_claim_list(info2))
        try:
            similarity_per = (len(result) / max(len(list_info1), len(list_info2)) * 100)
        except ZeroDivisionError:
            similarity_per = 0
        if similarity_per == 0:
            flash("Please check Id's that you entered", "primary")
        elif similarity_per >= 75:
            flash("Almost Similar Patents", "success")
        elif similarity_per >= 50:
            flash("Partial Similar Patents", "warning")
        else:
            flash("Not Similar", "danger")
        return render_template('index.html', form=form, id1=id1, id2=id2, info1=list_info1, info2=list_info2,
                           result=result)
    return redirect(url_for('home'))


@app.route('/api/compare', methods=['POST'])
def compare_items():
    selected_item1_id = request.form['item1_id']
    selected_item2_id = request.form['item2_id']
    selected_item1_id = selected_item1_id.replace(';', ' ; ').replace(':', ' : ').replace(',', ' , ')
    selected_item2_id = selected_item2_id.replace(';', ' ; ').replace(':', ' : ').replace(',', ' , ')
    if '' in (selected_item1_id, selected_item2_id):
        comparison_result = ""
    else:
        # comparison_result = compare_strings_with_strike_and_bold(selected_item1_id, selected_item2_id)
        comparison_result = get_line_difference(selected_item1_id, selected_item2_id)

    comparison_result = comparison_result.replace(' ;', ';<br>').replace(' :', ':<br>')
    return jsonify({"result": comparison_result})


if __name__ == '__main__':
    app.run(debug=True, port=5200)
