from flask import Flask, render_template, request, redirect, url_for
import uuid


app = Flask(__name__, template_folder='templates')

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
# Basically the home page
# Added sortedTasks which uses lambda (inline function) to sort the tasks by priority
@app.route('/')
def index():
    sortedTasks = sorted(tasks, key=lambda x: priorityOrder[x['priority']])
    return render_template("index.html", tasks=sortedTasks)


#Adds a task to a list with a name and a priority
#request.form.get('task') gets the task name and ('priority') gets the priority (high, medium, low)
@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    priority = request.form.get('priority')
    id = str(uuid.uuid4())
    tasks.append({"task": task, "done": False, "priority": priority, "id": id})
    return redirect(url_for('index'))


# Edits a task in the list, it connects to edit.html which loads a page available to edit name and priority of the task 
# returns to index.html after edited
# with added sorting, now function gets id, find it and it edits the task
@app.route("/edit/<string:taskID>", methods=['GET', 'POST'])
def edit(taskID):
    index = findtaskID(taskID)
    if index is not None:
        task = tasks[index]
    if request.method == 'POST':
        task['task'] = request.form.get('task')
        task['priority'] = request.form.get('priority')
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





# RUnning the app
if __name__ == "__main__":
    app.run(debug = True)