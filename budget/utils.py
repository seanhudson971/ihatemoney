from functools import wraps
from flask import redirect, url_for, session, request

from models import Bill, Project
from forms import BillForm

def get_billform_for(project):
    """Return an instance of BillForm configured for a particular project."""
    payers = []
    ids = []
    for m in project.active_members:
        payers.append( (str(m.id), m.name) )
        ids.append( str(m.id) )
    form = BillForm()
    form.payed_for.choices = form.payer.choices = payers
    form.payed_for.data = ids
    return form

def requires_auth(f):
    """Decorator checking that the user do have access to the given project id.

    If not, redirects to an authentication page, otherwise display the requested
    page.
    """

    @wraps(f)
    def decorator(*args, **kwargs):
        # if a project id is specified in kwargs, check we have access to it
        # get the password matching this project id
        # pop project_id out of the kwargs
        project_id = kwargs.pop('project_id')
        project = Project.query.get(project_id)
        if not project:
            return redirect(url_for("create_project", project_id=project_id))

        if project.id in session and session[project.id] == project.password:
            # add project into kwargs and call the original function
            kwargs['project'] = project
            return f(*args, **kwargs)
        else:
            # redirect to authentication page
            return redirect(url_for("authenticate",
                project_id=project.id, redirect_url=request.url))
    return decorator