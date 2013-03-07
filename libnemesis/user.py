import srusers
from team import *
from college import *

class User:
    @classmethod
    def create_user(cls, username, password=None):
        if User.can_authenticate(username, password):
            return AuthenticatedUser(username, password)
        else:
            return User(username)

    @classmethod
    def can_authenticate(cls, username, password):
        return password is not None and srusers.user(username).bind(password)

    @classmethod
    def from_flask_request(cls, req):
        form = req.form
        if req.form.has_key("username") and req.form.has_key("password"):
            return User.create_user(form["username"], form["password"])
        else:
            return NullUser()

    def __init__(self, username):
        self._user = srusers.user(username)
        if not self._user.in_db:
            raise Exception("user does not exist in database")

    @property
    def username(self):
        return self._user.username

    @property
    def teams(self):
        teams = set()
        teams.update(self._valid_team_groups())
        return teams

    @property
    def colleges(self):
        print self._user
        print self._user.groups()
        return [College(g) for g in self._user.groups()\
                if College.is_valid_college_name(g)]

    @property
    def is_teacher(self):
        print self._user.in_db
        return "teachers" in self._user.groups()

    def can_register_users(self):
        return False

    @property
    def is_blueshirt(self):
        return "mentors" in self._user.groups()

    def can_view_details(self, other_user_or_username):
        #if it's a string return the internal comparison with a user object
        if isinstance(other_user_or_username, basestring):
            other_user_or_username = User(other_user_or_username)

        return self._can_view_details(other_user_or_username)

    def _valid_team_groups(self):
        return [Team(g) for g in self._user.groups() if Team.valid_team_name(g)]

    def _can_view_details(self, user_object):
        return False

    def __eq__(self, other):
        if isinstance(other, User) or isinstance(other, AuthenticatedUser):
            return self._user.username == other._user.username
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class AuthenticatedUser(User):
    def __init__(self, username, password):
        self._user = srusers.user(username)
        assert self._user.bind(password)
        self._user = srusers.user(username)
        self._password = password

    def can_register_users(self):
        return self.is_teacher or self.is_blueshirt

    def _can_view_details(self, user_object):
        return self._can_view_if_teacher(user_object) or self._can_view_if_blueshirt(user_object)

    def _any_college_has_member(self, user_object):
        for college in self.colleges:
            for user in college.users:
                if user == user_object:
                    return True
        return False

    def _any_team_has_member(self, user_object):
        for team in self.teams:
            for user in team.users:
                if user == user_object:
                    return True
        return False

    def _can_view_if_teacher(self, user_object):
        return self.is_teacher and self._any_college_has_member(user_object)

    def _can_view_if_blueshirt(self, user_object):
        return self.is_blueshirt and self._any_team_has_member(user_object)

class NullUser:
    def __init__(self):
        self.can_register_users = False
        self.username = ""
