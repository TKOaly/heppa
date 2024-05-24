from flask import redirect, render_template, request, url_for
from flask_login import login_required, current_user, login_manager
from flask_babel import gettext

from application import app, db
from application.candidates import models
from application.candidates.models import Candidate
from application.candidates.forms import CandidateForm
from application.candidates.forms import EditForm

from application.votes.models import Approval
from application.votes.models import Veto

from application.auth.models import User

@app.route("/candidates/", methods=["GET"])
@app.route("/candidates", methods=["GET"])
def candidates_index():
    candidates = Candidate.query.filter_by(selected=False).all()

    for c in candidates:
        vetos = Veto.query.filter_by(candidate_id=c.id)
        vetoers = []
        for veto in vetos:
            vetoers.append(User.query.get(veto.voter_id).name)
        setattr(c, "vetoers", vetoers)

        approvers = []
        for approval in c.approvals:
            approvers.append(User.query.get(approval.voter_id).name)
        setattr(c, "approvers", approvers)

        setattr(c, "approval", len(c.approvals))
        setattr(c, "veto", len(c.vetoers))

        setattr(c, "nominator", User.query.get(c.nominator_id).name)

        if current_user.is_active:
            setattr(c, "approved",
                    Approval.query.filter_by(voter_id=current_user.id, candidate_id=c.id).count() > 0)
            setattr(c, "vetoed",
                    Veto.query.filter_by(voter_id=current_user.id, candidate_id=c.id).count() > 0)
            
        displayed_tags = []
        for tag in c.tags:
            displayed_tags.append(tag.name)
        setattr(c, "displayed_tags", displayed_tags)

    candidates = sorted(candidates, key=lambda c: c.approval, reverse=True)
    candidates = sorted(candidates, key=lambda c: c.veto)
    
    return render_template("candidates/list.html",
                            winning=Candidate.find_winning_candidates(),
                            candidates=candidates,
                            n_of_voters=User.how_many_voters())

@app.route("/candidates/selected/")
def candidates_index_selected():
    candidates = Candidate.query.filter_by(selected=True).all()
    displayed_tags = []
    for c in candidates:
        for tag in c.tags:
            displayed_tags.append(tag.name)
        setattr(c, "displayed_tags", displayed_tags)

        setattr(c, "nominator", User.query.get(c.nominator_id).name)
    
    candidates = sorted(candidates, key=lambda c: c.date_modified)

    return render_template("candidates/selected.html", candidates=candidates)

@app.route("/candidates/new/")
@login_required
def candidates_form():
    return render_template("candidates/new.html", form=CandidateForm())

@app.route("/candidates/selected/<candidate_id>/", methods=["POST"])
@login_required
def candidates_set_selected(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    candidate.selected = True
    db.session().commit()

    return redirect(url_for("candidates_index"))

@app.route("/candidates/edit/<candidate_id>/", methods=["POST", "GET"])
@login_required
def candidates_edit(candidate_id):
    candidate = Candidate.query.get(candidate_id)
    
    if request.method == "GET":
        return render_template("candidates/edit.html",
        form=EditForm(obj=candidate), candidate=candidate)

    if candidate.nominator_id != current_user.id:
        return render_template("candidates/edit.html", error=gettext("You can't edit other people's candidates!"),
        form=EditForm(obj=candidate), candidate=candidate)

    form = EditForm(request.form)

    candidate.name = form.name.data
    candidate.selected = form.selected.data
    candidate.url = form.url.data
    candidate.description = form.description.data

    db.session.commit()

    return redirect(url_for("candidates_index"))

@app.route("/candidates/delete/<candidate_id>/", methods=["POST"])
@login_required
def candidates_delete(candidate_id):
    candidate = Candidate.query.get(candidate_id)

    if candidate.nominator_id != current_user.id:
        return render_template("candidates/edit.html", error=gettext("You can't delete other people's candidates!"),
            form=EditForm(obj=candidate), candidate=candidate)

    db.session().delete(candidate)
    db.session().commit()

    return redirect(url_for("candidates_index"))

@app.route("/candidates/approved/<candidate_id>/", methods=["POST"])
@login_required
def candidates_set_approved(candidate_id):
    approval = Approval.query.filter_by(candidate_id=candidate_id, voter_id=current_user.id).first()

    if (approval == None):
        new_approval = Approval(current_user.id, candidate_id)
        db.session().add(new_approval)
    else:
        db.session().delete(approval)

    db.session().commit()

    return redirect(url_for("candidates_index"))

@app.route("/candidates/veto/<candidate_id>/", methods=["POST"])
@login_required
def candidates_set_veto(candidate_id):
    veto = Veto.query.filter_by(candidate_id=candidate_id, voter_id=current_user.id).first()

    if (veto == None):
        new_veto = Veto(current_user.id, candidate_id)
        db.session().add(new_veto)
    else:
        db.session().delete(veto)

    db.session().commit()

    return redirect(url_for("candidates_index"))

@app.route("/candidates/", methods=["POST"])
@login_required
def candidates_create():
    form = CandidateForm(request.form)

    if not form.validate():
        return render_template("tasks/new.html", form=form)

    candidate = Candidate(form.name.data, current_user.id, form.url.data, form.description.data)

    db.session().add(candidate)
    db.session().commit()

    return redirect(url_for("candidates_index"))
