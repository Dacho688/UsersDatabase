import sqlite3
import gradio as gr

DB_FILE = "./users_database.db"

def initialize_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL
            )
        ''')
    conn.commit()
    conn.close()

initialize_db() # Call this once when your application starts

def add_user(name, email):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    if len(name)==0:
        name=None
    if len(email)==0:
        email=None
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        return "User added successfully!"
    except sqlite3.IntegrityError as e:
        if "UNIQUE" in e.args[0]:
            err = "Error: Email already exists."
            return err
        elif "NOT NULL" in e.args[0]:
            if "email" in e.args[0]:
                return "Error: Email can't be blank."
            elif "name" in e.args[0]:
                return "Error: Name can't be blank."
        else:
            return f"Error: {e}"
    except Exception as e:
        return e
    finally:
        conn.close()
        
def get_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM users")
    column_names = [description[0] for description in cursor.description]
    users = cursor.fetchall()
    table = gr.DataFrame(users,headers=column_names)
    conn.close()
    return table

with gr.Blocks() as demo:
    gr.Markdown("## User Management with SQLite")
    with gr.Row():
        name_input = gr.Textbox(label="Name")
        email_input = gr.Textbox(label="Email")
        add_button = gr.Button("Add User")
        
    output_message = gr.Textbox(label="Status")
        
    gr.Markdown("### Current Users")
    users_table = gr.Dataframe()
    demo.load(get_users, outputs=users_table) #get users on app launch
    add_button.click(add_user, inputs=[name_input, email_input], outputs=output_message)\
                     .then(get_users,outputs=users_table)
    
if __name__ == "__main__":
    demo.launch()