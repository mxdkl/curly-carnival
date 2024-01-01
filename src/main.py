from database import Database


def main():
    db = Database()
    db.searchDatabase("PhoneNumber", "+14085551234")


if __name__ == "__main__":
    main()
