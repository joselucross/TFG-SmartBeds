import smartbeds.vars as v
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import url_for
from smartbeds.routes import webapi as api


@v.app.route('/', methods=['GET'])
def home():
    context = {"page": {"page": 'home'}, "info": get_info(), "title": "Inicio"}
    if context['info']['login']:
        mod_request()
        response, code = api.beds()
        context['beds'] = response.get_json()["beds"]
    return render_template('home.html', **context)


@v.app.route('/auth', methods=['GET', 'POST'])
def login():
    context = {"page": {"page": 'login', "bad": False}, "info": get_info(), "title": "Iniciar Sesión"}
    if request.method == "POST":
        response, code = api.auth()
        if code == 200:
            response_json = response.get_json()
            session['token'] = response_json['token']
            session['role'] = response_json['role']
            session['username'] = response_json['username']
            return redirect(url_for("home"))
        context["page"]['nick'] = request.form['user']
        context["page"]['bad'] = True
        return render_template('auth/login.html', **context)
    else:
        return render_template('auth/login.html', **context)


@v.app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect(url_for("home"))


@v.app.route('/bed/<bedname>', methods=['GET'])
def cama(bedname):
    #TODO: Check Permsision
    context = {'page': {'page': 'bed','bed_info': bedname}, 'info': get_info(), "title": "Cama"}
    return render_template('cama.html', **context)


@v.app.route('/bed/mod', methods=['PUT'])
def modifica_cama():
    mod_request()  # Introducimos el token
    return api.bedmod()


@v.app.route('/bed/add', methods=['PUT'])
def nueva_cama():
    mod_request()  # Introducimos el token
    return api.bedadd()


@v.app.route('/bed/del', methods=['DELETE'])
def borrar_cama(bedname):
    mod_request()  # Introducimos el token
    return api.beddel()


@v.app.route('/beds', methods=['GET'])
def camas():
    context = {"page": {"page": 'admin_beds'}, "info": get_info(), "title": "Administrar camas"}
    mod_request()
    response, code = api.beds()
    context['beds'] = response.get_json()["beds"]
    return render_template('camas.html', **context)


def get_info():
    if 'token' in session:
        try:
            return {"login": True, "role": session['role'], "user": session['username']}
        except KeyError:
            return {"login": False}
    else:
        return {"login": False}


def mod_request():
    data = dict(request.form)
    data['token'] = session['token']
    request.form = data  # Técnicamente esta operación no es legal, pero funciona
