# -*- coding: utf-8 -*-
from src.security.passlib_setup import pwd_context
from getpass import getpass
import pickle


class User():
    def __init__(self, username, groups = []):
        self.username = username
        self.password = pwd_context.encrypt(getpass())
        self.groups = groups

    def __str__(self) :
        return "User {}\nGroups: {}\nphash:{}\n".format(self.username,
            self.groups, self.password)

    def set_password(self):
        self.password = pwd_context.encrypt(getpass())
        print("Password changed successfully")

    def set_groups(self, groups):
        self.groups = groups
        print("Groups changed to: {}".format(groups))

class UserData:
    """
    Class for storing and accessing user data and hashed' passwords.
    All changes must be saved explicitly with the save() function
    to be stored.
    Loads stored register at initiation.
    """

    def __init__(self, filename="data_userpass"):
        self.users = []
        self.datafile = filename


    def add_user(self, username, groups=[]):
        """Add user to register with unique name and a password-hash
        Username must be 3 characters or more, and cannot contain spaces
        """
        if self.is_user(username):
            print("User {} already exists".format(username))
            return False
        elif len(username) < 3 or " " in username:
            print("Username must contain atleast 3 characters and no spaces")
        else:
            self.users.append(User(username, groups))
            return True


    def remove_user(self, username):
        "Remove a user from register"
        user = self.find_user(username)
        if user:
            self.users.remove(user)
            return True
        else:
            print("User {} not found...".format(username))
            return False


    def find_user(self, username):
        "Return user with given username"
        for user in self.users:
            if user.username == username:
                return user

    def verify(self, username, pwd):
        "Verify username and password are correct and valid"
        user = self.find_user(username)
        if user:
            return pwd_context.verify(pwd, user.password)
        else:
            print("User {} not found".format(username))
            return False

    def list_users(self):
        "Lists all users in register"
        print("Saved users: \n---------------\n")
        for user in self.users:
            print("{} in {}".format(user.username, user.groups))
            # print("{}".format(item)   )
        print("\n----------------\n")


    def is_user(self, username):
        "Check if username is contained in register"
        if self.find_user(username):
            return True
        else: return False


    def save(self):
        "Save users in pickled file, overwriting previous (if any) files"
        with open("{}.pcl".format(self.datafile), 'wb') as outfile:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(self.users, outfile, pickle.HIGHEST_PROTOCOL)


    def load(self):
        "Load users from pickled file"
        with open("{}.pcl".format(self.datafile), 'rb') as infile:
            self.users = pickle.load(infile)
