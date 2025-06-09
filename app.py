import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
import os
from datetime import datetime, timedelta

app = Flask(__name__)

TASKS_FILE = 'tasks.csv'
EXPECTED_COLUMNS = ['id', 'name', 'start_date', 'due_date', 'priority', 'status']

def init_csv():
    if not os.path.exists(TASKS_FILE):
        df = pd.DataFrame(columns=EXPECTED_COLUMNS)
        df.to_csv(TASKS_FILE, index=False, encoding='utf-8')
    else:
        # Check if CSV is empty or has incorrect headers
        try:
            df = pd.read_csv(TASKS_FILE, encoding='utf-8')
            if df.empty or list(df.columns) != EXPECTED_COLUMNS:
                # Recreate with correct headers if empty or malformed
                df = pd.DataFrame(columns=EXPECTED_COLUMNS)
                df.to_csv(TASKS_FILE, index=False, encoding='utf-8')
        except pd.errors.EmptyDataError: # Handles case where file exists but is empty
             df = pd.DataFrame(columns=EXPECTED_COLUMNS)
             df.to_csv(TASKS_FILE, index=False, encoding='utf-8')


def get_all_tasks():
    init_csv()
    try:
        tasks_df = pd.read_csv(TASKS_FILE, encoding='utf-8')
        if tasks_df.empty:
            return pd.DataFrame(columns=EXPECTED_COLUMNS) # Return empty DataFrame with columns
        # Ensure all columns are present, fill with default if not (though init_csv should prevent this)
        for col in EXPECTED_COLUMNS:
            if col not in tasks_df.columns:
                tasks_df[col] = None # Or some other default
        return tasks_df
    except FileNotFoundError:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)


def save_tasks(tasks_df):
    tasks_df.to_csv(TASKS_FILE, index=False, encoding='utf-8')

def get_next_id(tasks_df):
    if tasks_df.empty or 'id' not in tasks_df.columns or tasks_df['id'].isnull().all():
        return 1
    return tasks_df['id'].max() + 1

@app.route('/')
def index():
    tasks_df = get_all_tasks()

    # Ensure 'due_date' is datetime for sorting, handle potential errors
    if not tasks_df.empty and 'due_date' in tasks_df.columns:
        tasks_df['due_date'] = pd.to_datetime(tasks_df['due_date'], errors='coerce')
        tasks_df = tasks_df.sort_values(by='due_date', ascending=True)
        # Convert back to string for display if needed, or handle in template
        # tasks_df['due_date'] = tasks_df['due_date'].dt.strftime('%Y-%m-%d')
    else: # If tasks_df is empty or no due_date, create an empty list or handle as appropriate
        tasks_list = []

    today = datetime.now().date()
    notifications = []
    processed_tasks_list = []

    if not tasks_df.empty:
        for _, row in tasks_df.iterrows():
            task = row.to_dict()

            # Date handling
            start_date_obj = pd.to_datetime(task.get('start_date'), errors='coerce').date() if pd.notnull(task.get('start_date')) else None
            due_date_obj = pd.to_datetime(task.get('due_date'), errors='coerce').date() if pd.notnull(task.get('due_date')) else None

            task['start_delayed'] = False
            if start_date_obj and start_date_obj < today and task.get('status') == '未着手':
                task['start_delayed'] = True

            task['due_delayed'] = False
            if due_date_obj and due_date_obj < today and task.get('status') != '完了':
                task['due_delayed'] = True

            # Ensure dates are strings for template if they were converted
            if start_date_obj:
                task['start_date'] = start_date_obj.strftime('%Y-%m-%d')
            if due_date_obj:
                task['due_date'] = due_date_obj.strftime('%Y-%m-%d')


            # Notification for tasks due within 3 days
            if due_date_obj and task.get('status') != '完了':
                if (due_date_obj - today).days <= 3 and (due_date_obj - today).days >= 0:
                    notifications.append(task)

            processed_tasks_list.append(task)

    return render_template('index.html', tasks=processed_tasks_list, notifications=notifications)

@app.route('/add', methods=['POST'])
def add_task():
    tasks_df = get_all_tasks()

    task_name = request.form.get('name')
    start_date = request.form.get('start_date')
    due_date = request.form.get('due_date')
    priority = request.form.get('priority')

    if not all([task_name, start_date, due_date, priority]):
        # Handle missing fields if necessary, though 'required' in HTML should prevent most
        return redirect(url_for('index'))

    new_id = get_next_id(tasks_df)

    new_task = pd.DataFrame([{
        'id': new_id,
        'name': task_name,
        'start_date': start_date,
        'due_date': due_date,
        'priority': priority,
        'status': '未着手' # Default status
    }])

    updated_tasks_df = pd.concat([tasks_df, new_task], ignore_index=True)
    save_tasks(updated_tasks_df)

    return redirect(url_for('index'))

@app.route('/update_status/<int:task_id>', methods=['POST'])
def update_status(task_id):
    tasks_df = get_all_tasks()
    new_status = request.form.get('status')

    if not tasks_df.empty and task_id in tasks_df['id'].values:
        tasks_df.loc[tasks_df['id'] == task_id, 'status'] = new_status
        save_tasks(tasks_df)

    # It's good practice to redirect to the referrer or a default if referrer is not available.
    # For simplicity, always redirecting to index.
    return redirect(request.referrer or url_for('index'))

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    tasks_df = get_all_tasks()

    if not tasks_df.empty and task_id in tasks_df['id'].values:
        tasks_df = tasks_df[tasks_df['id'] != task_id]
        save_tasks(tasks_df)

    return redirect(url_for('index'))

@app.route('/search')
def search_tasks():
    query = request.args.get('query', '').strip().lower()
    tasks_df = get_all_tasks()

    today = datetime.now().date()
    notifications = [] # Recalculate notifications for search results context as well

    if not tasks_df.empty:
        # Ensure 'due_date' is datetime for sorting and notification logic
        tasks_df['due_date'] = pd.to_datetime(tasks_df['due_date'], errors='coerce')

        if query:
            # Filter by name (case-insensitive partial match)
            # Ensure 'name' column is treated as string
            tasks_df_filtered = tasks_df[tasks_df['name'].astype(str).str.lower().str.contains(query)]
        else:
            # If query is empty, show all tasks (or handle as preferred)
            tasks_df_filtered = tasks_df.copy() # Use a copy to avoid modifying original df

        # Sort results by due_date
        if not tasks_df_filtered.empty:
             tasks_df_filtered = tasks_df_filtered.sort_values(by='due_date', ascending=True)

        processed_tasks_list = []
        for _, row in tasks_df_filtered.iterrows():
            task = row.to_dict()

            start_date_obj = pd.to_datetime(task.get('start_date'), errors='coerce').date() if pd.notnull(task.get('start_date')) else None
            due_date_obj = row['due_date'].date() if pd.notnull(row['due_date']) else None # Use already converted due_date

            task['start_delayed'] = False
            if start_date_obj and start_date_obj < today and task.get('status') == '未着手':
                task['start_delayed'] = True

            task['due_delayed'] = False
            if due_date_obj and due_date_obj < today and task.get('status') != '完了':
                task['due_delayed'] = True

            # Convert dates to string for display
            if start_date_obj:
                task['start_date'] = start_date_obj.strftime('%Y-%m-%d')
            if due_date_obj:
                task['due_date'] = due_date_obj.strftime('%Y-%m-%d')

            # Notification logic for filtered tasks
            if due_date_obj and task.get('status') != '完了':
                if (due_date_obj - today).days <= 3 and (due_date_obj - today).days >= 0:
                    # Check if this specific task variant (could be different if original tasks_df was modified)
                    # is already in a global notification list or add it.
                    # For simplicity, we are creating notifications scoped to the search result.
                    notifications.append(task)

            processed_tasks_list.append(task)

        return render_template('index.html', tasks=processed_tasks_list, notifications=notifications, search_query=query)

    else: # If tasks_df itself is empty
        return render_template('index.html', tasks=[], notifications=notifications, search_query=query)

if __name__ == '__main__':
    init_csv() # Ensure CSV is ready at startup
    app.run(debug=True)
