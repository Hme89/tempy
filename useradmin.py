#!/usr/bin/python

from src.security.userlib import UserData
import getpass
import cmd


class Cli(cmd.Cmd):
    """Simple cli for StamPi user manipulation"""
    def __init__(self):
        """
        Loads user database on startup, or creates a new empty one
        if one is not found.
        """
        cmd.Cmd.__init__(self)
        self.prompt = ":->"
        self.intro = ("\nUser editor for StamPi\n")
        self.user_db = UserData()
        try:
            self.user_db.load()
        except FileNotFoundError as e:
            print("Datafile {} not found, creating new...".format(
            self.user_db.datafile))

    def do_print(self, args):
        """Print user details"""
        print(self.user_db.find_user(args.split(" ")[0]))

    def do_verify(self, args):
        """Verify username and password"""
        usr = args.split(" ")[0]
        print(self.user_db.verify(usr, getpass.getpass()))

    def do_add(self, args):
        """Add user with group permissions to database:
        ~$ add 'username' 'group1' 'group2'..."""
        args = args.split(" ")

        if self.user_db.is_user(args[0]):
            print("User {} already in database".format(args[0]))
            return

        if len(args) == 1:
            if self.user_db.add_user(args[0]):
                print("User {} added successfully".format(args[0]))
        elif len(args) > 1:
            if self.user_db.add_user(args[0], args[1:]):
                print('User {} added successfully with groups:'.format(args[0]))
                print(args[1:])
        else:
            print("Provide username, and optionally groups in list G1 G2 ...")


    def do_remove(self, args):
        """Remove user from database"""
        username = args.split(" ")[0]
        if self.user_db.remove_user(username):
            print("User {} removed successfully".format(username))

    def do_setpass(self, args):
        """Edit user password"""
        username = args.split(" ")[0]
        try:
            user = self.user_db.find_user(username)
            if user:
                user.set_password()
            else:
                print("User {} not found".format(username))
        except:
            print("Provide username")

    def do_setgroups(self, args):
        """Edit user groups.
        ~$ setgroups 'username' 'group1' 'group2'... """
        args = args.split(" ")
        try:
            user = self.user_db.find_user(args[0])
            if user:
                user.set_groups(args[1:])
            else:
                print("User {} not found".format(args[0]))
        except:
            print("Provide username")



    def do_list(self, args):
        """List all current users"""
        self.user_db.list_users()


    def do_save(self, args):
        """Save current database to file"""
        self.user_db.save()

    def do_exit(self, args):
        """ Saves current state and exits"""
        self.user_db.save()
        print("\nHave a nice day!")
        return -1

    def do_EOF(self, args):
        """ Saves current state and exits"""
        return self.do_exit(args)



if __name__ == "__main__":
    try:
        cmd = Cli()
        cmd.cmdloop()
    except KeyboardInterrupt:
        cmd.do_exit(0)
