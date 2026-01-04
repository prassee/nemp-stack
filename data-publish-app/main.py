from ddl import create_database, execute_ddl, grant_privileges
from add_users import update_random_users

DATABASE_NAME = "mixpanel"


def main():
    # create_database(DATABASE_NAME)
    # execute_ddl("ddl/mixpanel_events.sql", DATABASE_NAME)
    # grant_privileges(DATABASE_NAME, "mysql")
    update_random_users(database=DATABASE_NAME)


if __name__ == "__main__":
    main()
