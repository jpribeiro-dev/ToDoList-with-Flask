from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__, template_folder='templates')

# Start with an empty list of tasks that will be stored in memory
# In the future I will connect this to a database to store tasks and priorities
tasks = []

# Loading the tasks and connecting to index.html
# Basically the home page
@app.route('/')
def index():
    return render_template("index.html", tasks=tasks)


#Adds a task to a list with a name and a priority
#request.form.get('task') gets the task name and ('priority') gets the priority (high, medium, low)
@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    priority = request.form.get('priority')
    tasks.append({"task": task, "done": False, "priority": priority})
    return redirect(url_for('index'))


# Edits a task in the list, it connects to edit.html which loads a page available to edit name and priority of the task 
# returns to index.html after edited
@app.route("/edit/<int:index>", methods=['GET', 'POST'])
def edit(index):
    task = tasks[index]
    if request.method == 'POST':
        task['task'] = request.form.get('task')
        task['priority'] = request.form.get('priority')
        return redirect(url_for('index'))
    else:
        return render_template("edit.html", task=task, index=index)


# checks the item off
# I used not done because if i want to uncheck it again I can always just click check again
@app.route("/check/<int:index>")
def check(index,):
    tasks[index]['done'] = not tasks[index]['done']
    return redirect(url_for('index'))



# Deletes the task from the list. Simple as del is already built in python
@app.route("/delete/<int:index>")
def delete(index):
    del tasks[index]
    return redirect(url_for('index'))





# RUnning the app
if __name__ == "__main__":
    app.run(debug = True)