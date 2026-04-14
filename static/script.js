document.addEventListener('DOMContentLoaded', function() {
    loadTodos();
});

// --- UTILITY FUNCTION TO GET DOM ELEMENTS ---
const todoInput = document.getElementById('todo-input');
const todoList = document.getElementById('todo-list');

// --- CORE API INTERACTION ---

async function loadTodos() {
    try {
        const response = await fetch('/api/todos');
        const todos = await response.json();
        renderTodos(todos);
    } catch (error) {
        console.error('Error loading todos:', error);
    }
}

async function addTodo() {
    const taskText = todoInput.value.trim();
    if (!taskText) {
        alert('Por favor, introduce una tarea.');
        return;
    }

    try {
        const response = await fetch('/api/todos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ task: taskText })
        });
        const todo = await response.json();
        if (response.ok) {
            todoInput.value = ''; // Limpiar input
            // Refrescar la lista en lugar de re-renderizar todo para mejor rendimiento
            const newTodoElement = createTodoElement(todo);
            todoList.prepend(newTodoElement); // Añadir al principio
        } else {
            alert('Error al añadir la tarea.');
        }
    } catch (error) {
        console.error('Error adding todo:', error);
        alert('Error de red al añadir la tarea.');
    }
}

async function toggleComplete(todoId) {
    try {
        const response = await fetch(`/api/todos/${todoId}/complete`, {
            method: 'PUT'
        });
        const todo = await response.json();
        if (response.ok) {
            const listItem = document.querySelector(`.todo-item[data-id="${todoId}"]`);
            if (listItem) {
                if (todo.completed) {
                    listItem.classList.add('completed');
                } else {
                    listItem.classList.remove('completed');
                }
            }
        } else {
            alert('No se pudo actualizar el estado.');
        }
    } catch (error) {
        console.error('Error toggling complete:', error);
    }
}

async function deleteTodo(todoId) {
    if (!confirm('¿Estás seguro de que quieres eliminar esta tarea?')) return;

    try {
        const response = await fetch(`/api/todos/${todoId}`, {
            method: 'DELETE'
        });
        if (response.ok) {
            const elementToDelete = document.querySelector(`.todo-item[data-id="${todoId}"]`);
            if (elementToDelete) {
                elementToDelete.remove();
            }
        } else {
            alert('Error al eliminar la tarea.');
        }
    } catch (error) {
        console.error('Error deleting todo:', error);
    }
}

// --- RENDERING/VIEW FUNCTIONS ---

function createTodoElement(todo) {
    const li = document.createElement('li');
    li.className = `todo-item ${todo.completed ? 'completed' : ''}`;
    li.setAttribute('data-id', todo.id);

    li.innerHTML = `
        <span class="task-text">${todo.task}</span>
        <div class="actions">
            <button class="complete-btn" onclick="toggleComplete(${todo.id})">
                ${todo.completed ? '✔️' : '✔️'}
            </button>
            <button class="delete-btn" onclick="deleteTodo(${todo.id})">Eliminar</button>
        </div>
    `;
    return li;
}

function renderTodos(todos) {
    const todoList = document.getElementById('todo-list');
    todoList.innerHTML = ''; // Limpiar la lista

    if (todos.length === 0) {
        todoList.innerHTML = '<p style="text-align:center; color: #888;">¡Aún no tienes tareas. Añade una!</p>';
        return;
    }

    // Renderizar la lista de tareas
    // Nota: Aunque la plantilla Python ya renderiza los existentes, 
    // si la recargamos o añadimos nuevos, usaremos esta función.
    todos.forEach(todo => {
        const element = createTodoElement(todo);
        todoList.appendChild(element);
    });
}
