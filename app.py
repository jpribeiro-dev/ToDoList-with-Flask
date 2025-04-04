from flask import Flask, render_template, request, redirect, url_for, session
import uuid
from datetime import datetime

#import session to keep the same sorting method active when page refreshed.
app = Flask(__name__, template_folder='templates')
app.secret_key = 'PalitoGoat3047'

# Start with an empty list of tasks that will be stored in memory
# In the future I will connect this to a database to store tasks and priorities
tasks = []


# This is for sorting the tasks by higher to lower priority
priorityOrder = {"high": 1, "medium": 2, "low": 3}

def findtaskID(taskID):
    for i in range(len(tasks)):
        if tasks[i]['id'] == taskID:
            return i
    return None



# Loading the tasks and connecting to index.html
# Now that i added sessions, get the sorting method from session and send it to html as well
# if none, default is by priority
@app.route('/')
def index():
    sortMethod = session.get('sortMethod', 'bypriority')
    sortedTasks = performSort(sortMethod)
    hideC = session.get('hideC', False)
    hideCtasks = hideCompletedTasksHelper(hideC, sortedTasks)
    errorMessage = session.get('errorMessage', None)
    return render_template("index.html", tasks=hideCtasks, currSortMeth=sortMethod, errorMessage=errorMessage, hideC=hideC)


#Adds a task to a list with a name and a priority
#request.form.get('task') gets the task name and ('priority') gets the priority (high, medium, low)
@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    priority = request.form.get('priority')
    dueDate = request.form.get('duedate') 

    #throw error message when task is empty name
    if not task:
        session['errorMessage'] = 'Name of task should not be empty. Thanks!'
        return redirect(url_for('index'))

    id = str(uuid.uuid4())
    tasks.append({"task": task, "done": False, "priority": priority, "dueDate": dueDate, "id": id})

    if session.get('errorMessage'):
        session['errorMessage'] = None

    return redirect(url_for('index'))


# Edits a task in the list, it connects to edit.html which loads a page available to edit name and priority of the task 
# returns to index.html after edited
# with added sorting, now function gets id, find it and it edits the task
@app.route("/edit/<string:taskID>", methods=['GET', 'POST'])
def edit(taskID):
    index = findtaskID(taskID)

    if session['errorMessage']:
        session['errorMessage'] = None
    if index is not None:
        task = tasks[index]
    if request.method == 'POST':

        taskName = request.form.get('task')

        #throw error to html if task name is empty
        if not taskName:
            session['errorMessage'] = 'Name of task should not be empty. Thanks!'
            errorMessage = session.get('errorMessage')
            return render_template("edit.html", task=task, taskID=taskID, errorMessage = errorMessage)
        
        task['task'] = request.form.get('task')
        task['priority'] = request.form.get('priority')
        task['dueDate'] = request.form.get('dueDate')


        return redirect(url_for('index'))
    else:
        return render_template("edit.html", task=task, taskID=taskID)


# checks the item off
# I used not done because if i want to uncheck it again I can always just click check again
@app.route("/check/<string:taskID>")
def check(taskID):
    index = findtaskID(taskID)
    if index is not None:
        tasks[index]['done'] = not tasks[index]['done']
    return redirect(url_for('index'))



# Deletes the task from the list. Simple as del is already built in python
@app.route("/delete/<string:taskID>")
def delete(taskID):
    index = findtaskID(taskID)
    if index is not None:
        del tasks[index]
    return redirect(url_for('index'))


#sort function that receives form from html and calls helper sort function that sorts based on way of sorting
# stores the current sorting method in session so when it refreshes, it would be the same
@app.route("/sort", methods=['POST'])
def sort():
    sortOpt = request.form.get('sortOpt')
    session['sortMethod'] = sortOpt
    return redirect(url_for('index'))



@app.route("/hideCompletedTasks", methods=['POST'])
def hideCompletedTasks():
    session['hideC'] = not session.get('hideC', False)
    return redirect(url_for('index'))


    


def hideCompletedTasksHelper(hideC, hideCTasks):
    if (hideC):
        filtered = []
        for i in range(len(hideCTasks)):
            if not hideCTasks[i]['done']:
                filtered.append(hideCTasks[i])

        return filtered
    
    return hideCTasks



#helper function to perform sort
# receives by priority or by date and adjusts accordingly
# if not by priority it just returns tasks since it is already sorted by added date
def performSort(method):
    if method == 'bypriority':
        return sorted(tasks, key=lambda x: priorityOrder[x['priority']])
    elif method == 'byduedate':
        return sorted(tasks, key=lambda x:datetime.strptime(x.get('dueDate') or '2039-01-01', "%Y-%m-%d"))
    
    return tasks


# RUnning the app

if __name__ == "__main__":
    app.run(debug = True)