import os
import psycopg2
from flask import Flask, render_template, jsonify, request

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "tododb"),
            user=os.getenv("DB_USER", "postgres"),#"user"),
            password=os.getenv("DB_PASSWORD", "password"),
            port=5432
        )
        return conn
    except Exception as e:
        print("DB connection failed:", e)
        return None
    
def init_db():
    print("Creando tabla...")
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    task TEXT NOT NULL,
                    completed BOOLEAN NOT NULL DEFAULT FALSE
                );
            """)
            conn.commit()
            cur.close()
            conn.close()
            print("DB initialized")
        except Exception as e:
            print("Error initializing DB:", e)


def sync_todos():
    global todos
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, task, completed FROM todos")
            rows = cur.fetchall()
            todos = [
                {
                    'id': row[0],
                    'task': row[1],
                    'completed': row[2]
                }
                for row in rows
            ]
            cur.close()
            conn.close()
        except Exception as e:
            print("Error syncing todos:", e)

app = Flask(__name__)

# Simple in-memory database for demonstration
todos = []

@app.route('/')
def index():
    return render_template('index.html', todos=todos)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, task, completed FROM todos")
            rows = cur.fetchall()
            todos.clear()
            for row in rows:
                todos.append({
                    'id': row[0],
                    'task': row[1],
                    'completed': row[2]
                })
            cur.close()
            conn.close()
        except Exception as e:
            print("Error fetching todos:", e)
    return jsonify(todos)

@app.route('/api/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    if data and 'task' in data:
        conn = get_db_connection()
        if conn:
            #print("existe conexion")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO todos (task, completed) VALUES (%s, %s) RETURNING id",
                (data['task'], False)
            )
            new_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            
            sync_todos()

            return jsonify(
                {
                    'id': new_id,
                    'task': data['task'],
                    'completed': False
                }
            ), 201
        new_todo = {
            'id': len(todos) + 1,
            'task': data['task'],
            'completed': False
        }
        todos.append(new_todo)
        return jsonify(new_todo), 201
    return jsonify({"error": "Task field missing"}), 400

@app.route('/api/todos/<int:todo_id>/complete', methods=['PUT'])
def set_complete(todo_id):
    for todo in todos:
        if todo['id'] == todo_id:
            todo['completed'] = True
            conn = get_db_connection()
            if conn:
                try:
                    cur = conn.cursor()
                    cur.execute(
                        "UPDATE todos SET completed = TRUE WHERE id = %s",
                        (todo_id,)
                    )
                    conn.commit()
                    cur.close()
                    conn.close()
                    sync_todos()

                except Exception as e:
                    print("Error updating todo:", e)
            return jsonify(todo)
    return jsonify({"error": "Todo not found"}), 404

@app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    global todos
    initial_len = len(todos)
    todos = [todo for todo in todos if todo['id'] != todo_id]
    if len(todos) < initial_len:
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "DELETE FROM todos WHERE id = %s",
                    (todo_id,)
                )
                conn.commit()
                cur.close()
                conn.close()

                sync_todos()
            except Exception as e:
                print("Error deleting todo:", e)
        return jsonify({"success": True})
    return jsonify({"error": "Todo not found"}), 404

if __name__ == '__main__':
    print("Iniciando aplicacion")
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)