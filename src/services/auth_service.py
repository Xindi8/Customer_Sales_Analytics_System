import getpass
from src.db.repository import dbFunctions
from src.domain.models import User

def login(repo: dbFunctions):
    while True:
        try:
            userID = int(input("\nPlease enter UserID:").strip())
            break
        except ValueError:
            print("\n[X]Invalid ID. UserID must be Integer!")

    rs_user = repo.login_verify(userID)
    if not rs_user:
        print("\n[X] User Does not Exist!Please sign up first!\n")
        return None

    while True:
        password = getpass.getpass("\nPlease enter Password: ").strip()
        if not password:
            print("\n[X] Password cannot be empty!")
        else:
            break

    if password == rs_user.psw:
        return rs_user
    else:
        print("[X] Password is not correct!")
        return None

def register(repo: dbFunctions):
    while True:
        userName = input("\nPlease enter your name:").strip()
        if not userName:
            print("\n[X] userName cannot be empty!")
        else:
            break

    while True:
        email = input("\nPlease enter email address:").strip().lower()
        if not email:
            print("\n[X] email cannot be empty!")
        elif "@" not in email:
            print("\n[X] PLease enter correct email!")
        else:
            break

    while True:
        password = getpass.getpass("\nPlease enter Password: ").strip()
        if not password:
            print("\n[X] password cannot be empty!")
        else:
            break

    if repo.check_email(email):
        print("\n[X] This email address already registered!\n")
        return None

    rs_user = repo.insert_customer(userName, email, password)
    print("\n[✓] Sign up sucessfully!\n")
    print("\nPlease remember your user id is :\n", rs_user.uid)
    print("\n[......] Loading customer page\n")
    return rs_user
