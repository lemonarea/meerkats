# Python libraries
import streamlit as st
import pandas as pd
import os
import hashlib
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Local imports
# import the page title
from wofofiles.globfuncs import get_app_title
# import the menu
from wofofiles.menu import app_menu
# import the database connection
from wofofiles.conn import username, password, host, port, database
import pandas as pd

# Page config
st.set_page_config(
    page_title=get_app_title(),
    layout='centered',
    initial_sidebar_state="collapsed"
)

# Create a connection string for the MySQL database
connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string, echo=True)

# Hashing the password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Users CRUD
def users_page():

    # Add a new user
    with st.popover("New ✙"):    
        user_code = st.text_input("User Code")
        user_name = st.text_input("User Name")
        password = st.text_input("Password", type="password")

        if st.button("Add"):
            if user_code and user_name and password:
                hashed_password = hash_password(password)
                try:
                    with engine.begin() as connection:
                        insert_query = text("INSERT INTO users (UserCode, UserName, Password) VALUES (:user_code, :user_name, :password)")
                        connection.execute(insert_query, {'user_code': user_code, 'user_name': user_name, 'password': hashed_password})
                        st.success(f"User '{user_name}' added successfully!")
                except IntegrityError:
                    st.error(f"Failed to add user: User code '{user_code}' already exists.")
                except SQLAlchemyError as e:
                    st.error(f"Failed to add user: {str(e.__dict__['orig'])}")
            else:
                st.warning("Please enter all user details before adding.")

    # View existing users as a table
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT UserCode, UserName FROM users"))
            users = result.fetchall()
            if users:
                df = pd.DataFrame(users, columns=["User Code", "User Name"])

                # Adding 'Delete' and 'Change Password' columns
                df["Delete"] = False  # Default 'Select' column with False value
                df["Change Password"] = False  # Default column for Change Password

                # Editable data table with 'Select' checkbox and 'Change Password' button
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Delete": st.column_config.CheckboxColumn("Delete"),
                        "User Code": st.column_config.NumberColumn("User Code"),
                        "User Name": st.column_config.TextColumn("User Name"),
                        "Change Password": st.column_config.CheckboxColumn("Change Password"),
                    },
                    hide_index=True,
                    key="editable_users",
                    use_container_width=True
                )

                # Handle edits
                if st.button("Update ↻"):
                    for idx, row in edited_df.iterrows():
                        original = df.iloc[idx]
                        if row["User Code"] != original["User Code"] or row["User Name"] != original["User Name"]:
                            try:
                                update_query = text(""" 
                                    UPDATE users 
                                    SET UserCode = :new_user_code, UserName = :new_user_name 
                                    WHERE UserCode = :original_user_code
                                """)
                                params = {
                                    'new_user_code': row["User Code"],
                                    'new_user_name': row["User Name"],
                                    'original_user_code': original["User Code"]
                                }
                                with engine.begin() as connection:
                                    connection.execute(update_query, params)
                                st.success(f"User '{original['User Code']}' updated successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to update user: {str(e.__dict__['orig'])}")

                # Handle deletion
                rows_to_delete = edited_df[edited_df["Delete"] == True]
                if not rows_to_delete.empty:
                    if st.button("Delete ✖"):
                        for _, row in rows_to_delete.iterrows():
                            try:
                                with engine.begin() as connection:
                                    delete_query = text("DELETE FROM users WHERE UserCode = :user_code")
                                    connection.execute(delete_query, {'user_code': row["User Code"]})
                                st.success(f"User '{row['User Code']}' deleted successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to delete user: {str(e.__dict__['orig'])}")

                # Handle password change
                rows_to_change_password = edited_df[edited_df["Change Password"] == True]
                if not rows_to_change_password.empty:
                    for _, row in rows_to_change_password.iterrows():
                        new_password = st.text_input(f"New password for {row['User Name']} {row['User Code']}", type="password", key=f"new_password_{row['User Code']}")
                        if st.button(f"Change Password"):
                            if new_password:
                                hashed_new_password = hash_password(new_password)
                                try:
                                    with engine.begin() as connection:
                                        update_password_query = text("""
                                            UPDATE users
                                            SET Password = :new_password
                                            WHERE UserCode = :user_code
                                        """)
                                        connection.execute(update_password_query, {'new_password': hashed_new_password, 'user_code': row["User Code"]})
                                    st.success(f"Password for User Code '{row['User Code']}' updated successfully!")
                                except SQLAlchemyError as e:
                                    st.error(f"Failed to change password: {str(e.__dict__['orig'])}")
                            else:
                                st.warning(f"Please enter a new password for {row['User Code']}.")

            else:
                st.write("No users found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve users: {str(e.__dict__['orig'])}")

# Groups CRUD
def groups_page():

    # Add a new group
    with st.popover("New ✙"):    
        group_code = st.text_input("Group Code")
        group_name = st.text_input("Group Name")

        if st.button("Add"):
            if group_code and group_name:
                try:
                    with engine.begin() as connection:
                        insert_query = text("INSERT INTO `groups` (GroupCode, GroupName) VALUES (:group_code, :group_name)")
                        connection.execute(insert_query, {'group_code': group_code, 'group_name': group_name})
                        st.success(f"Group '{group_name}' added successfully!")
                except IntegrityError:
                    st.error(f"Failed to add group: Group code '{group_code}' already exists.")
                except SQLAlchemyError as e:
                    st.error(f"Failed to add group: {str(e.__dict__['orig'])}")
            else:
                st.warning("Please enter all group details before adding.")

    # View existing groups as a table
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT GroupCode, GroupName FROM `groups`"))
            groups = result.fetchall()
            if groups:
                df = pd.DataFrame(groups, columns=["Group Code", "Group Name"])

                # Adding 'Delete' column
                df["Delete"] = False  # Default 'Select' column with False value

                # Editable data table with 'Select' checkbox
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Delete": st.column_config.CheckboxColumn("Delete"),
                        "Group Code": st.column_config.NumberColumn("Group Code"),
                        "Group Name": st.column_config.TextColumn("Group Name"),
                    },
                    hide_index=True,
                    key="editable_groups",
                    use_container_width=True
                )

                # Handle edits
                if st.button("Update ↻"):
                    for idx, row in edited_df.iterrows():
                        original = df.iloc[idx]
                        if row["Group Code"] != original["Group Code"] or row["Group Name"] != original["Group Name"]:
                            try:
                                update_query = text(""" 
                                    UPDATE `groups` 
                                    SET GroupCode = :new_group_code, GroupName = :new_group_name 
                                    WHERE GroupCode = :original_group_code
                                """)
                                params = {
                                    'new_group_code': row["Group Code"],
                                    'new_group_name': row["Group Name"],
                                    'original_group_code': original["Group Code"]
                                }
                                with engine.begin() as connection:
                                    connection.execute(update_query, params)
                                st.success(f"Group '{original['Group Code']}' updated successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to update group: {str(e.__dict__['orig'])}")

                # Handle deletion
                rows_to_delete = edited_df[edited_df["Delete"] == True]
                if not rows_to_delete.empty:
                    if st.button("Delete ✖"):
                        for _, row in rows_to_delete.iterrows():
                            try:
                                with engine.begin() as connection:
                                    delete_query = text("DELETE FROM `groups` WHERE GroupCode = :group_code")
                                    connection.execute(delete_query, {'group_code': row["Group Code"]})
                                st.success(f"Group '{row['Group Code']}' deleted successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to delete group: {str(e.__dict__['orig'])}")

            else:
                st.write("No groups found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve groups: {str(e.__dict__['orig'])}")

# Sections CRUD
def sections_page():

    # Add a new section
    with st.popover("New ✙"):    
        section_code = st.text_input("Section Code")
        section_name = st.text_input("Section Name")

        if st.button("Add"):
            if section_code and section_name:
                try:
                    with engine.begin() as connection:
                        insert_query = text("INSERT INTO sections (SectionCode, SectionName) VALUES (:section_code, :section_name)")
                        connection.execute(insert_query, {'section_code': section_code, 'section_name': section_name})
                        st.success(f"Section '{section_name}' added successfully!")
                except IntegrityError:
                    st.error(f"Failed to add section: Section code '{section_code}' already exists.")
                except SQLAlchemyError as e:
                    st.error(f"Failed to add section: {str(e.__dict__['orig'])}")
            else:
                st.warning("Please enter all section details before adding.")

    # View existing sections as a table
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT SectionCode, SectionName FROM sections"))
            sections = result.fetchall()
            if sections:
                df = pd.DataFrame(sections, columns=["Section Code", "Section Name"])

                # Adding 'Delete' column
                df["Delete"] = False  # Default 'Select' column with False value

                # Editable data table with 'Select' checkbox
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Delete": st.column_config.CheckboxColumn("Delete"),
                        "Section Code": st.column_config.NumberColumn("Section Code"),
                        "Section Name": st.column_config.TextColumn("Section Name"),
                    },
                    hide_index=True,
                    key="editable_sections",
                    use_container_width=True
                )

                # Handle edits
                if st.button("Update ↻"):
                    for idx, row in edited_df.iterrows():
                        original = df.iloc[idx]
                        if row["Section Code"] != original["Section Code"] or row["Section Name"] != original["Section Name"]:
                            try:
                                update_query = text(""" 
                                    UPDATE sections 
                                    SET SectionCode = :new_section_code, SectionName = :new_section_name 
                                    WHERE SectionCode = :original_section_code
                                """)
                                params = {
                                    'new_section_code': row["Section Code"],
                                    'new_section_name': row["Section Name"],
                                    'original_section_code': original["Section Code"]
                                }
                                with engine.begin() as connection:
                                    connection.execute(update_query, params)
                                st.success(f"Section '{original['Section Code']}' updated successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to update section: {str(e.__dict__['orig'])}")

                # Handle deletion
                rows_to_delete = edited_df[edited_df["Delete"] == True]
                if not rows_to_delete.empty:
                    if st.button("Delete ✖"):
                        for _, row in rows_to_delete.iterrows():
                            try:
                                with engine.begin() as connection:
                                    delete_query = text("DELETE FROM sections WHERE SectionCode = :section_code")
                                    connection.execute(delete_query, {'section_code': row["Section Code"]})
                                st.success(f"Section '{row['Section Code']}' deleted successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to delete section: {str(e.__dict__['orig'])}")

            else:
                st.write("No sections found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve sections: {str(e.__dict__['orig'])}")

# Pages CRUD
def pages_page():

    # Add a new page
    
    with st.popover("New ✙"):    
        page_ref = st.text_input("Page Reference")
        page_name = st.text_input("Page Name")

        if st.button("Add"):
            if page_ref and page_name:
                try:
                    with engine.begin() as connection:
                        insert_query = text("INSERT INTO pages (PageRef, PageName) VALUES (:page_ref, :page_name)")
                        connection.execute(insert_query, {'page_ref': page_ref, 'page_name': page_name})
                        st.success(f"Page '{page_name}' added successfully!")
                except IntegrityError:
                    st.error(f"Failed to add page: Page reference '{page_ref}' already exists.")
                except SQLAlchemyError as e:
                    st.error(f"Failed to add page: {str(e.__dict__['orig'])}")
            else:
                st.warning("Please enter all page details before adding.")

    # View existing pages as a table

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT PageRef, PageName FROM pages"))
            pages = result.fetchall()
            if pages:
                df = pd.DataFrame(pages, columns=["Page Reference", "Page Name"])

                # Adding a 'Select' column for row selection
                df["Delete"] = False  # Default 'Select' column with False value

                # Editable data table with 'Select' checkbox
                edited_df = st.data_editor(
                    df,
                    column_config={
                        "Delete": st.column_config.CheckboxColumn("Delete"),
                        "Page Reference": st.column_config.TextColumn("Page Reference"),
                        "Page Name": st.column_config.TextColumn("Page Name"),
                    },
                    hide_index=True,
                    key="editable_pages",
                    use_container_width=True
                )

                # Handle edits
                if st.button("Update ↻"):
                    for idx, row in edited_df.iterrows():
                        original = df.iloc[idx]
                        if row["Page Reference"] != original["Page Reference"] or row["Page Name"] != original["Page Name"]:
                            try:
                                with engine.begin() as connection:
                                    update_query = text("""
                                        UPDATE pages 
                                        SET PageRef = :new_page_ref, PageName = :new_page_name 
                                        WHERE PageRef = :original_page_ref
                                    """)
                                    connection.execute(update_query, {
                                        'new_page_ref': row["Page Reference"],
                                        'new_page_name': row["Page Name"],
                                        'original_page_ref': original["Page Reference"]
                                    })
                                st.success(f"Page '{original['Page Reference']}' updated successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to update page: {str(e.__dict__['orig'])}")

                # Handle deletion
                rows_to_delete = edited_df[edited_df["Delete"] == True]
                if not rows_to_delete.empty:
                    if st.button("Delete ✖"):
                        for _, row in rows_to_delete.iterrows():
                            try:
                                with engine.begin() as connection:
                                    delete_query = text("DELETE FROM pages WHERE PageRef = :page_ref")
                                    connection.execute(delete_query, {'page_ref': row["Page Reference"]})
                                st.success(f"Page '{row['Page Reference']}' deleted successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to delete page: {str(e.__dict__['orig'])}")
            else:
                st.write("No pages found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve pages: {str(e.__dict__['orig'])}")

# Creating CRUD for the users access control
def access_control_page():
    # Load all options for dropdowns
    try:
        with engine.connect() as connection:
            users = connection.execute(text("SELECT UserCode, UserName FROM users")).fetchall()
            groups = connection.execute(text("SELECT GroupCode, GroupName FROM `groups`")).fetchall()
            sections = connection.execute(text("SELECT SectionCode, SectionName FROM sections")).fetchall()
            pages = connection.execute(text("SELECT PageRef, PageName FROM pages")).fetchall()

            # Create dictionaries for dropdowns
            user_options = {f"{user.UserName} ({user.UserCode})": user.UserCode for user in users}
            group_options = {"None": None} | {group.GroupName: group.GroupCode for group in groups}
            section_options = {"None": None} | {section.SectionName: section.SectionCode for section in sections}
            page_options = {page.PageName: page.PageRef for page in pages}

    except SQLAlchemyError as e:
        st.error(f"Failed to load options: {str(e.__dict__['orig'])}")
        return

    # Add a new access control entry
    with st.popover("New ✙"):
        selected_user = st.selectbox("Select User", options=list(user_options.keys()))
        selected_group = st.selectbox("Select Group", options=list(group_options.keys()))
        selected_section = st.selectbox("Select Section", options=list(section_options.keys()))
        selected_page = st.selectbox("Select Page", options=list(page_options.keys()))

        if st.button("Add"):
            if selected_user and selected_page:
                try:
                    with engine.begin() as connection:
                        insert_query = text("""
                            INSERT INTO access_control (UserCode, GroupCode, SectionCode, PageRef) 
                            VALUES (:user_code, :group_code, :section_code, :page_ref)
                        """)
                        connection.execute(insert_query, {
                            'user_code': user_options[selected_user],
                            'group_code': group_options[selected_group],
                            'section_code': section_options[selected_section],
                            'page_ref': page_options[selected_page]
                        })
                        st.success("Access control added successfully!")
                except IntegrityError:
                    st.error("Failed to add access control : Integrity error.")
                except SQLAlchemyError as e:
                    st.error(f"Failed to add access control : {str(e.__dict__['orig'])}")
            else:
                st.warning("Please select all required details before adding.")

    # View existing access control entries as a table
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT ac.UserCode, u.UserName, ac.GroupCode, g.GroupName, 
                       ac.SectionCode, s.SectionName, ac.PageRef, p.PageName
                FROM access_control ac
                JOIN users u ON ac.UserCode = u.UserCode
                LEFT JOIN `groups` g ON ac.GroupCode = g.GroupCode
                LEFT JOIN sections s ON ac.SectionCode = s.SectionCode
                LEFT JOIN pages p ON ac.PageRef = p.PageRef
            """)
            entries = connection.execute(query).fetchall()
            if entries:
                df = pd.DataFrame(entries, columns=["User Code", "User Name", "Group Code", "Group Name", "Section Code", "Section Name", "Page Ref", "Page Name"])

                # Adding 'Delete' column
                df["Delete"] = False  # Default 'Select' column with False value

                # Combine User Name and User Code for display
                df["User Display"] = df.apply(lambda row: f"{row['User Name']} ({row['User Code']})", axis=1)

                # Editable data table with dropdowns
                edited_df = st.data_editor(
                    df[["User Display", "Group Name", "Section Name", "Page Name", "Delete"]],
                    column_config={
                        "Delete": st.column_config.CheckboxColumn("Delete"),
                        "User Display": st.column_config.SelectboxColumn("User Display", options=list(user_options.keys())),
                        "Group Name": st.column_config.SelectboxColumn("Group Name", options=list(group_options.keys())),
                        "Section Name": st.column_config.SelectboxColumn("Section Name", options=list(section_options.keys())),
                        "Page Name": st.column_config.SelectboxColumn("Page Name", options=list(page_options.keys())),
                    },
                    hide_index=True,
                    key="editable_access_control",
                    use_container_width=True
                )

                # Handle edits
                if st.button("Update ↻"):
                    for idx, row in edited_df.iterrows():
                        original = df.iloc[idx]
                        if (row["User Display"] != original["User Display"] or row["Group Name"] != original["Group Name"] or
                            row["Section Name"] != original["Section Name"] or row["Page Name"] != original["Page Name"]):
                            try:
                                update_query = text("""
                                    UPDATE access_control 
                                    SET UserCode = :new_user_code, GroupCode = :new_group_code, 
                                        SectionCode = :new_section_code, PageRef = :new_page_ref 
                                    WHERE UserCode = :original_user_code AND PageRef = :original_page_ref
                                """)
                                params = {
                                    'new_user_code': user_options[row["User Display"]],
                                    'new_group_code': group_options[row["Group Name"]],
                                    'new_section_code': section_options[row["Section Name"]],
                                    'new_page_ref': page_options[row["Page Name"]],
                                    'original_user_code': original["User Code"],
                                    'original_page_ref': original["Page Ref"]
                                }
                                with engine.begin() as connection:
                                    connection.execute(update_query, params)
                                st.success(f"Access control entry for User '{original['User Name']}' updated successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to update access control entry: {str(e.__dict__['orig'])}")

                # Handle deletion
                rows_to_delete = edited_df[edited_df["Delete"] == True]
                if not rows_to_delete.empty:
                    if st.button("Delete ✖"):
                        for _, row in rows_to_delete.iterrows():
                            try:
                                with engine.begin() as connection:
                                    delete_query = text("DELETE FROM access_control WHERE UserCode = :user_code AND PageRef = :page_ref")
                                    connection.execute(delete_query, {'user_code': user_options[row["User Display"]], 'page_ref': page_options[row["Page Name"]]})
                                st.success(f"Access control entry for User '{row['User Display']}' deleted successfully!")
                            except SQLAlchemyError as e:
                                st.error(f"Failed to delete access control entry: {str(e.__dict__['orig'])}")

            else:
                st.write("No access control entries found.")
    except SQLAlchemyError as e:
        st.error(f"Failed to retrieve access control entries: {str(e.__dict__['orig'])}")

# Add the access control page to the MAC page
def mac_page():
    st.title("Meerkat Access Control")

    # Select page to manage
    page = st.selectbox("**:blue[Select a page ⤵]**", ("", "Manage Users", "Manage Groups", "Manage Sections", "Manage Pages", "Manage Permissions"))

    if page == "Manage Users":
        users_page()
    if page == "Manage Groups":
        groups_page()
    if page == "Manage Sections":
        sections_page()     
    if page == "Manage Pages":
        pages_page()       
    if page == "Manage Permissions":
        access_control_page()

# Display the MAC page if this script is run
def main():
    # Check if the user is logged in
    if st.session_state.get('logged_in'):
        try:
            with engine.connect() as connection:
                user_group_query = text("""
                    SELECT g.GroupName 
                    FROM users u
                    JOIN access_control ac ON u.UserCode = ac.UserCode
                    JOIN `groups` g ON ac.GroupCode = g.GroupCode
                    WHERE u.UserCode = :user_code
                """)
                result = connection.execute(user_group_query, {'user_code': st.session_state.get('user_code')}).fetchone()
                user_group = result.GroupName if result else None
                st.session_state['user_group'] = user_group
        except SQLAlchemyError as e:
            st.error(f"Failed to retrieve user group: {str(e.__dict__['orig'])}")
            return

        # Check user access to the MAC page if the group is admin
        if st.session_state.get('user_group') == 'Admin':
            mac_page()
        else:
            st.warning("You do not have permission to access this page.")

        # Sidebar with navigation options
        with st.sidebar:
            st.write(f"Welcome, {st.session_state['user_name']}!")
            # the main menu
            app_menu()
    else:
        st.warning("You must log in to access this page.")
        st.stop()  # Stops execution if not logged in

if __name__ == "__main__":
    main()