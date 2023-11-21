# preload.py at each level defines special variables and/or functions to be
# inherited by pages farther down the tree.

# LOOK AND FEEL

cs_base_color = "#A31F34"  # the base color
cs_course_number = 'P41A'
cs_header = cs_course_number  # the upper-left corner
cs_icon_url = 'COURSE/favicon_local.gif'  # the favicon, if any
# the 'header' text for the page
cs_long_name = cs_content_header = "Welcome to Phys 41A"
cs_title = cs_course_number # the browser's title bar
cs_breadcrumbs_html = ''

# don't try to parse markdown inside of these tags
cs_markdown_ignore_tags = ('script', 'svg', 'textarea')

# defines the menu at the top of the page in the default template.
# each dictionary defines one menu item and should contain two keys:
#  * text: the text to show for the link
#  * link: the target of the link (either a URL or another list of this same form)
cs_top_menu = [
    {'text': 'Home', 'link': 'COURSE'},
    {'text': 'Resources', 'link': 'COURSE/material/resources'},
    {'text': 'Lectures', 'link': 'COURSE/material/lectures'},
    {'text': 'Labs', 'link': [
        {'text': 'Prelabs', 'link': 'COURSE/material/prelabs'},
        {'text': 'Labs', 'link': 'COURSE/material/labs'},
    ]},
    {'text': 'Exercises', 'link': 'COURSE/material/exercises'},
    {"link": "COURSE/progress", "text": "Progress"},
#    {'text': 'Sample Menu', 'link': [
#                                     {'link': 'COURSE/calendar', 'text': 'Calendar and Handouts'},
#                                     {'link': 'COURSE/announcements', 'text': 'Archived Announcements'},
#                                     'divider',
#                                     {'link': 'COURSE/information', 'text': 'Basic Information'},
#                                     {'link': 'COURSE/schedule_staff', 'text': 'Schedule and Staff'},
#                                     {'link': 'COURSE/grading', 'text': 'Grading Policies'},
#                                     {'link': 'COURSE/collaboration', 'text': 'Collaboration Policy'},
#                                    ]},
#    {'text': 'Piazza', 'link': 'https://piazza.com/mit/spring17/601'},
]

user_menu_options_permissions = [
    {"entry": {"text": "Student Progress", "link": "COURSE/staff/progress"}, "permissions": {"grade"}},
]

def user_menu_options(context):
    user_info = context.get("cs_user_info", None)
    if user_info is None:
        return []

    user_permissions = user_info.get("permissions")
    custom_user_menu = []
    for user_menu_entry in user_menu_options_permissions:
        required_persmission = user_menu_entry["permissions"]
        user_has_permission = any((p in required_persmission) for p in user_permissions)

        if user_has_permission:
            custom_user_menu.append(user_menu_entry["entry"])

    return custom_user_menu


# AUTHENTICATION
cs_require_confirm_email = False
cs_auth_type = 'login'  # use the default (username/password based) authentication method
# for actually running a course at MIT, I like using OpenID Connect instead (https://oidc.mit.edu/).

# custom XML tag handling, copied from one i wrote for 6.01 ages ago.  can
# probably largely be ignored (or can be updated to handle other kinds of
# tags).
import re
import hashlib
import subprocess
import shutil
def environment_matcher(tag):
    return re.compile("""<%s>(?P<body>.*?)</%s>""" % (tag, tag), re.MULTILINE|re.DOTALL)
def cs_course_handle_custom_tags(text):
    # CHECKOFFS AND CHECK YOURSELFS
    checkoffs = 0
    def docheckoff(match):
        nonlocal checkoffs
        d = match.groupdict()
        checkoffs += 1
        return '<div class="checkoff"><b>Checkoff %d:</b><p>%s</p><p><span id="queue_checkoff_%d"></span></p></div>' % (checkoffs, d['body'], checkoffs)
    text=re.sub(environment_matcher('checkoff'), docheckoff, text)

    checkyourself = 0
    def docheckyourself(match):
        nonlocal checkyourself
        d = match.groupdict()
        checkyourself += 1
        return '<div class="question"><b>Check Yourself %d:</b><p>%s</p><p><span id="queue_checkyourself_%d"></span></p></div>' % (checkyourself, d['body'], checkyourself)
    text=re.sub(environment_matcher('checkyourself'), docheckyourself, text)

    return text


# PYTHON SANDBOX

csq_python3 = True
csq_python_sandbox = "python"
csq_python_sandbox_type = "python"
# something like the following can be used to use a sandboxed python
# interpreter on the production copy (after following the directions at
# https://catsoop.mit.edu/website/docs/installing/server_configuration for
# setting up the sandbox):
if 'localhost' in cs_url_root:
    # locally, just use the system Python install
    csq_python_sandbox_interpreter = "/Users/alexherrera/miniconda3/envs/p41a/bin/python3.11"
else:
    # on the server, use the properly sandboxed python
    csq_python_sandbox_interpreter = "/home/catsoop/miniconda3/envs/p41a/bin/python"

try:
    csq_sandbox_options["do_rlimits"] = False
except:
    csq_sandbox_options = {"do_rlimits": False}

# PERMISSIONS

# users' roles are determined by the files in the __USERS__ directory.  each
# has the form username.py other information (such as a section number, if
# relevant) can be stored there as well but the system will look for role =
# "Student" or similar, and use that to set the user's permissions.
#
#  view: allowed to view the contents of a page
#  submit: allowed to submit to a page
#  view_all: always allowed to view every page, regardless of when it releases
#  submit_all: always allowed to submit to every question, regardless of when it releases or is due
#  impersonate: allowed to view the page "as" someone else
#  admin: administrative tasks (such as modifying group assignments)
#  whdw: allowed to see "WHDW" page (Who Has Done What)
#  email: allowed to send e-mail through CAT-SOOP
#  grade: allowed to submit grades
cs_default_role = 'Guest'
cs_permissions = {'Admin': ['view_all', 'submit_all', 'impersonate', 'admin', 'whdw', 'email', 'grade'],
            #   'Instructor': ['view_all', 'submit_all', 'impersonate', 'admin', 'whdw', 'email', 'grade'],
               'TA': ['view_all', 'submit_all', 'impersonate', 'whdw', 'email', 'grade'],
            #    'UTA': ['view_all', 'submit_all', 'impersonate', 'grade'],
            #    'LA': ['view_all', 'submit_all','impersonate', 'grade'],
               'Student': ['view', 'submit'],
               'Guest': ['view']}


# TIMING

# release and due dates can always be specified in absolute terms:
#   "YYYY-MM-DD:HH:MM"
# the following allows the use of relative times (and/or per-section times)
# section_times maps section names to times (below, the default section has
# lecture at 8am on Tuesdays)
# this allows setting, e.g.,  cs_release_date = "lec:2" to mean "release this
# at lecture time in week 2"
# different sections will get different times if they are specified below.
# adding section = 2, for example, to someone's __USERS__ file will cause the
# system to look up the key 2 in the dictionary below.
cs_first_monday = '2017-02-06:00:00'
section_times = {'default': {'lec': 'T:08:00', 'lab': 'T:09:00', 'lab_due':'M+:22:00', 'soln':'S+:08:00', 'tut':'W:08:00'},

}

def cs_realize_time(meta, rel):
    try:
        start, end = rel.split(':')
        section = cs_user_info.get('section', 'default')
        rel = section_times.get(section, {}).get(start, section_times['default'].get(start, 'NEVER'))
        meta['cs_week_number'] = int(end)
    except:
        pass
    return csm_time.realize_time(meta,rel)

import time
from datetime import datetime

# cs_post_load is invoked after the page is loaded but before it is rendered.
# the example below shows the time at which the current page was last modified
# (based on the Git history).
def cs_create_user(context):
    cs_username = context["cs_username"]

    if cs_username is None or cs_username == "None":
        return

    try:
        course_root = os.path.abspath(os.path.join(
            context['cs_data_root'], 'courses', context['cs_path_info'][0]))
        user_file = os.path.join(course_root, "__USERS__", f"{cs_username}.py")
        if not os.path.exists(user_file):
            subprocess.check_output(
                f' echo "role=\\"Student\\"" > {user_file}', shell=True)
    except:
        pass

def cs_post_load(context):
    cs_create_user(context)

    if 'cs_long_name' in context:
        context['cs_content_header'] = context['cs_long_name']
        context['cs_title'] = '%s | %s' % (context['cs_long_name'], context['cs_title'])
    try:
        loc = os.path.abspath(os.path.join(context['cs_data_root'], 'courses', *context['cs_path_info']))
        git_info = subprocess.check_output(["git", "log", "--pretty=format:%h %ct",
                                            "-n1", "--", "content.catsoop",
                                            "content.md", "content.xml",
                                            "content.py"], cwd=loc)
        h, t = git_info.split()
        t = context['csm_time'].long_timestamp(datetime.fromtimestamp(float(t))).replace(';', ' at')
        context['cs_footer'] = 'This page was last updated on %s (revision <code>%s</code>).<br/>&nbsp;<br/>' % (t, h.decode())
    except:
        pass
    
    if not globals().get("allow_guest") and (cs_username is None or cs_username == "None"):
        context["cs_content"] = "You must be logged in to view this page."

# Assignments
from datetime import datetime, timedelta, MAXYEAR
from typing import Dict, List, Literal, Tuple, Union

NOW = datetime.now()

def cs_date_to_datetime(timestring):
    """
    Converts cs_release/due_dates into datetime objects for easier use in the back end.
    """
    if timestring == "NEVER":
        return datetime(year=MAXYEAR, month=12, day=31, hour=23, minute=59, second=59)
    elif timestring == "ALWAYS":
        return datetime(year=1900, month=1, day=1, hour=0, minute=0, second=0)
    elif timestring[0].isdigit():
        # absolute times are specified as strings 'YYYY-MM-DD:HH:MM'
        return datetime.strptime(timestring, "%Y-%m-%d:%H:%M")
    else:
        raise Exception("Invalid time style: %s" % timestring)

class Material:
    """
    Base class for all material in the course.
    """
    def __init__(self, folder:str, name:str, cs_long_name:str, cs_release_date:str, cs_due_date:str):
        self.folder = folder
        self.name = name
        self.cs_long_name = cs_long_name
        if not cs_release_date:
            cs_release_date = "ALWAYS"
        self.cs_release_date = cs_release_date
        if not cs_due_date:
            cs_due_date = "NEVER"
        self.cs_due_date = cs_due_date
        self.dt_release_date = cs_date_to_datetime(cs_release_date)
        self.dt_due_date = cs_date_to_datetime(cs_due_date)

    def preload_vars(self):
        return (self.cs_long_name, self.cs_release_date, self.cs_due_date)

    def path(self):
        return f"COURSE/material/{self.folder}/{self.name}"

    def is_released(self):
        return NOW >= self.dt_release_date

    def is_due(self):
        return NOW >= self.dt_due_date

    def content_link(self):
        return f"* <a href='{self.path()}'>{self.cs_long_name}</a> (Due: {self.dt_due_date.strftime('%m/%d @ %I:%M %p')})\n\n"    

class Lecture(Material):
    def __init__(self, name, cs_release_date, urls):
        self.urls = urls
        super(Lecture, self).__init__("lectures", name, None, cs_release_date, None)
    
    def content_link(self):
        s = f"<h2><u>{self.name} ({self.dt_release_date.strftime('%m/%d').replace('0', '')})</u></h2>\n\n"
        for title, url in self.urls:
            s += f"* <a target='_blank' rel='noopener noreferrer' href='{url}'>{title}</a>\n"
        return s + "\n"

class MaterialManager:
    """
    Helper class to easily manage the material in the course.
    """
    def __init__(self):
        self.material: Dict[str, List[Material]] = dict()

    def add(self, material:List[Material]):
        if not isinstance(material, list):
            material = [material]
        for mat in material:
            self.material[mat.folder] = self.material.get(mat.folder, []) + [mat]

    def get(self, folder, name:str=None, status:Literal["released", "unreleased", "all"]="all") -> Union[Material, List[Material]]:
        mats = self.material.get(folder, [])
        if name is not None:
            for m in mats:
                if m.name == name:
                    return m
            return None
        else:
            if status == "all":
                return mats
            elif status == "released":
                return [m for m in mats if m.is_released()]
            elif stats == "unreleased":
                return [m for m in mats if not m.is_released()]

    def content_directory(self, folder):
        mats = self.material.get(folder, [])
        s = ""
        for mat in mats:
            if not mat.is_released():
                if is_staff():
                    s += f"<b style='color:#5454FF;'>The following content will become available to students at {mat.dt_release_date}.</b><br/>\n\n" + mat.content_link()
            else:
                s += mat.content_link()
        return s

# Add material
material_manager = MaterialManager()
material_manager.add([
    Lecture("Lecture 1", "2023-09-28:09:00", [
        ("Slides", "https://drive.google.com/file/d/1Aqsl_OH-NYlkHKdcZHPyuI4ivxECyEG2/view?usp=sharing"),
        ("lab1_class_data", "https://docs.google.com/spreadsheets/d/1dPN6qy5IzO_RARFnXUWhkAxVZrIHbvZFIBk4wksK9Cg/edit?usp=sharing"),
        ("lec1.ipynb", "https://colab.research.google.com/drive/1-yqIttxf2yMAJQnzJgpKQOgG5ZOmWR_4?usp=sharing"),
    ]),
    Lecture("Lecture 2", "2023-09-29:09:00", [
        ("lec2.ipynb", "https://colab.research.google.com/drive/1DPK08ChCyPeC72RgBc2XRTTS56kl7Kmz?usp=sharing"),
    ])
])
material_manager.add([
    Material("exercises", "ex1", "Exercise 1", "2023-11-20:09:00", "2023-11-22:23:59"),
])

# Grading functions
def get_page_stats(path, auto_ext=None, user=None):
    from collections import OrderedDict

    if auto_ext is None:
        auto_ext = []
    if user is None:
        user = cs_username
    try:
        x = csm_tutor.compute_page_stats(globals(), user, [cs_course] + path, ['question_info', 'state', 'actions', 'manual_grades'])
    except:
        link = "/".join(path)
        raise Exception(f"An error occurred when trying to parse the following path:\n'{link}'. Are you sure this file exists?")
    qi = x['question_info']
    np = OrderedDict((i, j['csq_npoints']) for i,j in qi.items())

    bests = {k: 0 for k in qi}
    times = {k: None for k in qi}
    dues = {k: None for k in qi}
    exts = {k: False for k in qi}
    raws = {k: 0 for k in qi}
    latenesses = {k: 0 for k in qi}
    late_by = {k: 0 for k in qi}
    # look through all actions, looking for the one that maximizes score
    for a in x['actions']:
        if a['action'] != 'submit':
            continue
        else:
            t = csm_time.from_detailed_timestamp(a['timestamp'])
            d = csm_time.from_detailed_timestamp(a['due_date'])
            for n in a['names']:
                if n not in bests:
                    continue
                try:
                    gmode = qi[n].get("csq_grading_mode",None)
                    if gmode == "manual":
                      s=0
                      for i in x['manual_grades']:
                        if i['qname']==n:
                          s=i['score']
                    else:
                      try:
                          s = max(0.0, min(1.0, float(csm_tutor.read_checker_result(globals(), a['checker_ids'][n])['score'])))
                      except:
                          s = max(0.0, min(1.0, a['scores'][n]))
                except:
                    continue
                # edue = d + timedelta(seconds=get_extension(path, n, exts, auto_ext))

                # l = late_penalty(qi[n], t, edue)  # this has to be here because of extensions
                # print(l)
                real_score = s
                if real_score >= bests[n]:
                    bests[n] = real_score
                    raws[n] = s
                    # latenesses[n] = l
                    times[n] = t
                    # dues[n] = edue
    # finally, go through and set scores that were overridden.
    for n in np:
        for so in cs_user_info.get('score_override', []):
            if all(i==j for i,j in zip(so[0], path + [n])):
                bests[n] = so[1]
                raws[n] = so[1]
                latenesses[n] = None
    w_norm = sum(np.values())
    np = {k: v/w_norm for k,v in np.items()}
    names = list(qi)
    dnames = {i: qi[i].get('csq_display_name', i) for i in names}
    return {'time': times, 'raw': raws, 'late': latenesses, 'score': bests, 'weight': np, 'names': list(names), 'dnames': dnames, 'ext': exts, 'late_by': late_by, 'due':dues}

def progress_page(user=None, only_released=True, with_name=False):
    bh = ""
    if user == "all_students":
        for username in sorted_usernames():
            user_info = csm_auth._get_user_information(globals(), dict(username = username), cs_course, username)
            if user_info["role"] == "Student":
                bh += username
                bh += progress_page(username, only_released, with_name=True)
    else:
        bh += f"<catsoop-section>Exercises</catsoop-section>"
        if only_released:
            for ex in material_manager.get("exercises", status="released"):
                bh += f"<catsoop-subsection>{ex.cs_long_name}</catsoop-subsection>"
                bh += progress_table_exercise(ex.name, user)[1]
        else:
            for ex in material_manager.get("exercises"):
                unreleased = not ex.is_released()
                bh += f"<catsoop-subsection>{ex.cs_long_name} {f'(Releasing: {ex.dt_release_date})' if unreleased else ''}</catsoop-subsection>"
                bh += progress_table_exercise(ex.name, user)[1]
    return bh

def progress_table_exercise(name, user=None):
    path = ["material", "exercises", name]
    auto_ext = []
    x = get_page_stats(path, auto_ext, user)

    p2 = '__'.join(path)
    bh = ""
    bh+='<center>'
    bh+='<table border="1">'
    bh+='<tr><td colspan="5" align="center"><b>%s</b> (<a onclick="toggle_details(\'%s\')" style="cursor:pointer;">show/hide details</a>)</td></tr>' % (path[-1].upper(), p2)
    # bh+='<tr class="details_%s" style="display:none;"><th>Question</th><th>Weight</th><th>Submitted</th><th>Raw Score</th><th>Lateness Multiplier</th><th>Final Score</th></tr>' % p2
    bh+='<tr class="details_%s" style="display:none;"><th>Question</th><th>Submitted</th><th>Raw Score</th><th>Weight</th><th>Final Score</th></tr>' % p2
    o = 0.0
    for i in x['names']:
        ext = ' <small><font color="darkgreen">ext</font></small>' if x['ext'][i] else ''
        if x['weight'][i] == 0:
            continue
        bh+='<tr class="details_%s" style="display:none;">' % p2
        bh+='<td>%s</td>' % x['dnames'][i]
        bh+='<td>%s</td>' % ('❌' if x['time'][i] is None else x['time'][i].strftime('%Y-%m-%d, %H:%M:%S'))
        bh+='<td>%.02f</td>' % x['raw'][i]
        bh+='<td>%.02f</td>' % x['weight'][i]
        # bh+='<td>%s%s</td>' % (('%.02f%%' % (x['late'][i]*100)) if x['late'][i] is not None else 'N/A', ext)
        bh+='<td>%.02f</td>' % (x['weight'][i]*x['score'][i]) # x['score'][i]
        o += x['weight'][i]*x['score'][i]
        bh+='</tr>'
    bh+='<tr><td colspan="4" align="right">Overall:</td><td>%.02f</td></tr>' % o
    bh+='</table>'
    bh+='</center>'
    return [o,bh]

# Restricted functions for use in staff-only pages
from functools import wraps

def is_staff():
    staff = False
    try:
        staff = cs_user_info.get('role') in {'TA', 'Admin'}
    except:
        pass
    return staff

class UserNotAuthorizedError(Exception):
    def __init__(self, message):
        self.message = message

def is_user_authorized(required_persmission = "admin"):
    return required_persmission in cs_user_info.get("permissions", set())

def restricted_fn(required_persmission = "admin"):
    """This decorator will stop unauthorized users from calling functions they
    shouldn't be allowed to. Throws an error if user not authorized"""
    def actual_wrapper(fn):
        @wraps(fn)
        def restricted_fn(*args, **kwargs):
            if not is_user_authorized(required_persmission):
                raise UserNotAuthorizedError("User not authorized to call {fn}".format(fn = fn.__name__))
            else:
                return fn(*args, **kwargs)
        return restricted_fn
    return actual_wrapper

@restricted_fn("grade")
def list_users():
    users = csm_user.all_users_info(globals(), cs_course)
    users_info = dict()
    for username in users:
        users_info[username] = csm_auth._get_user_information(globals(), dict(username = username), cs_course, username)
    return [user for _, user in users_info.items()]

@restricted_fn("grade")
def sorted_usernames():
    users = list_users()
    return sorted([s.get("username") for s in users])

@restricted_fn("grade")
def student_dropdown(student, form_target, all_option=False):
    student_dropdown = f"""<form action="{form_target}"><select name="student" onchange="this.form.submit()" style="width: 200px;">"""
    if all_option:
        student_dropdown += f"""<option value="all_students">all students</option>\n"""

    for username in sorted_usernames():
        student_dropdown += f"""<option value="{username}" {'selected="selected"' if username == student else ""}>{username}</option>\n"""
    student_dropdown += "</select></form>"
    return student_dropdown
