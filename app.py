from flask import Flask, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL
import os
from datetime import datetime
from dotenv import load_dotenv

# Loading my .env which has the DB information
load_dotenv()

#import session to keep the same sorting method active when page refreshed.
app = Flask(__name__, template_folder='templates')
app.secret_key = 'PalitoGoat3047'


# Connecting to database with information from .env
# Template from stack overlow
db = MySQL()
app.config['MYSQL_DATABASE_USER'] = os.getenv('DB_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.getenv('DB_NAME')
app.config['MYSQL_DATABASE_HOST'] = os.getenv('DB_HOST')
db.init_app(app)






# Loading the tasks and connecting to index.html
# Now that i added sessions, get the sorting method from session and send it to html as well
# if none, default is by priority
@app.route('/')
def index():
    sortMethod = session.get('sortMethod', 'bypriority')
    hideC = session.get('hideC', False)
    sortedTasks = performSortAndHideC(sortMethod, hideC)
    errorMessage = session.get('errorMessage', None)
    return render_template("index.html", tasks=sortedTasks, currSortMeth=sortMethod, errorMessage=errorMessage, hideC=hideC)


#Adds a task to a list with a name and a priority
#request.form.get('task') gets the task name and ('priority') gets the priority (high, medium, low)
@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    priority = request.form.get('priority')
    dueDate = request.form.get('duedate') 

    if dueDate == '':
        dueDate = None
    #throw error message when task is empty name
    if not task:
        session['errorMessage'] = 'Name of task should not be empty. Thanks!'
        return redirect(url_for('index'))
    
    conn = db.connect()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO TASKS (task, priority, dueDate, done) VALUES (%s, %s, %s, %s)", 
                   (task, priority, dueDate, False))
    
    conn.commit()
    cursor.close()
    conn.close()



    if session.get('errorMessage'):
        session['errorMessage'] = None

    return redirect(url_for('index'))


# Edits a task in the list, it connects to edit.html which loads a page available to edit name and priority of the task 
# returns to index.html after edited
# with added sorting, now function gets id, find it and it edits the task
@app.route("/edit/<string:taskID>", methods=['GET', 'POST'])
def edit(taskID):

    if session['errorMessage']:
        session['errorMessage'] = None

    # connect to the database and fetch the task with the given taskID
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TASKS WHERE id = %s", (taskID,))
    task = cursor.fetchone() # fetchone() returns a single row, so I can use it directly
    cursor.close()
    conn.close()

    if request.method == 'POST':

        taskName = request.form.get('task')

        #throw error to html if task name is empty
        if not taskName:
            session['errorMessage'] = 'Name of task should not be empty. Thanks!'
            errorMessage = session.get('errorMessage')
            return render_template("edit.html", task=task, taskID=taskID, errorMessage = errorMessage)
        

        priority = request.form.get('priority')
        dueDate = request.form.get('dueDate')
        conn = db.connect()
        cursor = conn.cursor() 
        cursor.execute("UPDATE TASKS SET task = %s, priority = %s, dueDate = %s WHERE id = %s",
        (taskName, priority, dueDate, taskID))
        conn.commit()
        cursor.close()
        conn.close()


        return redirect(url_for('index'))
    else:
        return render_template("edit.html", task=task, taskID=taskID)


# checks the item off
# I used not done because if i want to uncheck it again I can always just click check again
@app.route("/check/<string:taskID>")
def check(taskID):
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT done FROM TASKS WHERE id = %s", (taskID,)) # will return only the done status and not full row
    result = cursor.fetchone() # fetchone() returns a single row, so I can use it directly
    

    if result is not None:
        res = result[0] # this is how i access when i select and only returns specific value and not full row
        cursor.execute("UPDATE TASKS SET done = %s WHERE id = %s", (not res, taskID))
        conn.commit()
        


    cursor.close()
    conn.close()
    return redirect(url_for('index'))



# Deletes the task from the list. Simple as del is already built in python
@app.route("/delete/<string:taskID>")
def delete(taskID):
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TASKS WHERE id = %s", (taskID,))
    index = cursor.fetchone()

    if index is not None:
        cursor.execute("DELETE FROM TASKS WHERE id = %s", (taskID,))
        conn.commit()

    cursor.close()
    conn.close()
    return redirect(url_for('index'))


#sort function that receives form from html and calls helper sort function that sorts based on way of sorting
# stores the current sorting method in session so when it refreshes, it would be the same
@app.route("/sort", methods=['POST'])
def sort():
    sortOpt = request.form.get('sortOpt')
    session['sortMethod'] = sortOpt
    return redirect(url_for('index'))



# getting the checkbox from html and setting it to not session of hideCompletedTasks
#index calls the helper function with the sorted tasks that returns without the completed tasks
@app.route("/hideCompletedTasks", methods=['POST'])
def hideCompletedTasks():
    session['hideC'] = not session.get('hideC', False)
    return redirect(url_for('index'))


    






#helper function to perform sort and takes the sorted tasks(users choice on sort) and returns only teh ones that are not done yet
# receives by priority or by date and adjusts accordingly
# if not by priority it just returns tasks since it is already sorted by added date
def performSortAndHideC(method, hideC):
    conn = db.connect()
    cursor = conn.cursor()

    if method == 'bypriority':
        cursor.execute("SELECT * FROM TASKS ORDER BY priority")
        sortedTasks = cursor.fetchall()
        
    elif method == 'byduedate':
        cursor.execute("SELECT * FROM TASKS ORDER BY dueDate")
        sortedTasks = cursor.fetchall()
    else:
        cursor.execute("SELECT * FROM TASKS ORDER BY creation")
        sortedTasks = cursor.fetchall()
    

    result = []
    for task in sortedTasks:
        result.append({
            'id': task[0],
            'task': task[1],
            'priority': task[2],
            'dueDate': task[3],
            'done': task[4],
            'creation': task[5]
        })

    
    if (hideC):
        filtered = []
        for i in range(len(result)):
            if not result[i]['done']:
                filtered.append(result[i])

        return filtered
    

    cursor.close()
    conn.close()
    return result


# RUnning the app

if __name__ == "__main__":
    app.run(debug = True)