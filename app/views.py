from flask import current_app as app
from flask import render_template, request, redirect, url_for, session, flash
from . import db
from .models import Project, Task, Subtask
from datetime import datetime

@app.route('/')
def dashboard():
    projects = Project.query.all()
    return render_template('dashboard.html', projects=projects)

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    return render_template('project_detail.html', project=project)

@app.route('/create_project', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        name = request.form['name']
        status = request.form['status']
        allocated_budget = request.form['allocated_budget']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form['end_date'] else None
        
        new_project = Project(name=name, status=status, allocated_budget=allocated_budget, start_date=start_date, end_date=end_date)
        db.session.add(new_project)
        db.session.commit()

        return redirect(url_for('dashboard'))
    
    return render_template('create_project.html')

@app.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        project.name = request.form['name']
        project.status = request.form['status']
        project.allocated_budget = request.form['allocated_budget']
        project.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        project.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form['end_date'] else None
        
        db.session.commit()
        return redirect(url_for('dashboard'))
    
    return render_template('edit_project.html', project=project)

@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/add_task/<int:project_id>', methods=['GET', 'POST'])
def add_task(project_id):
    project = Project.query.get_or_404(project_id)
    task = Task(progress=0, payment_progress=0, cost=0, outgoing_costs=0, start_date=datetime.now(), end_date=None)
    
    if request.method == 'POST':
        name = request.form['name']
        status = request.form['status']
        payment_progress = request.form['payment_progress']
        cost = request.form['cost']
        outgoing_costs = request.form['outgoing_costs']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form['end_date'] else None
        
        new_task = Task(name=name, status=status, progress=0, payment_progress=payment_progress, cost=cost, outgoing_costs=outgoing_costs, start_date=start_date, end_date=end_date, project_id=project.id)
        db.session.add(new_task)
        db.session.commit()

        subtask_names = request.form.getlist('subtask_name[]')
        subtask_statuses = request.form.getlist('subtask_status[]')
        for subtask_name, subtask_status in zip(subtask_names, subtask_statuses):
            if subtask_name:
                status = 'done' if subtask_status == 'on' else 'planned'
                new_subtask = Subtask(name=subtask_name, status=status, task_id=new_task.id)
                db.session.add(new_subtask)
        db.session.commit()
        
        return redirect(url_for('project_detail', project_id=project.id))
    
    return render_template('add_task.html', project=project, task=task)

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        task.name = request.form['name']
        task.status = request.form['status']
        task.payment_progress = request.form['payment_progress']
        task.cost = request.form['cost']
        task.outgoing_costs = request.form['outgoing_costs']
        task.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        task.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d') if request.form['end_date'] else None
        task.last_payment_date = datetime.strptime(request.form['last_payment_date'], '%Y-%m-%d') if request.form.get('last_payment_date') else None

        # Proses pembaruan subtask yang ada
        subtask_ids = request.form.getlist('subtasks')
        for subtask in task.subtasks:
            if str(subtask.id) in subtask_ids:
                subtask.status = 'done'
            else:
                subtask.status = 'planned'  # Atau status default lainnya

        # Proses penambahan subtask baru jika ada yang ditambahkan
        subtask_names = request.form.getlist('subtask_name[]')
        subtask_statuses = request.form.getlist('subtask_status[]')
        for subtask_name, subtask_status in zip(subtask_names, subtask_statuses):
            if subtask_name:
                status = 'done' if subtask_status == 'on' else 'planned'
                new_subtask = Subtask(name=subtask_name, status=status, task_id=task.id)
                db.session.add(new_subtask)
        
        db.session.commit()
        
        return redirect(url_for('project_detail', project_id=task.project_id))
    
    return render_template('edit_task.html', task=task)

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project_id = task.project_id
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/delete_subtask/<int:subtask_id>', methods=['POST'])
def delete_subtask(subtask_id):
    subtask = Subtask.query.get_or_404(subtask_id)
    task_id = subtask.task_id
    db.session.delete(subtask)
    db.session.commit()
    return redirect(url_for('edit_task', task_id=task_id))

@app.route('/financial_statistics', methods=['GET', 'POST'])
def financial_statistics():
    if 'total_budget' not in session:
        session['total_budget'] = 0

    if request.method == 'POST':
        total_budget = int(request.form['budget'])
        session['total_budget'] = total_budget

    projects = Project.query.all()
    total_budget = session['total_budget']
    total_allocation = sum(project.allocated_budget for project in projects)
    total_remaining = total_budget - total_allocation
    
    return render_template('financial_statistics.html', projects=projects, total_budget=total_budget, total_allocation=total_allocation, total_remaining=total_remaining)

@app.route('/set_budget', methods=['POST'])
def set_budget():
    total_budget = int(request.form['budget'])
    session['total_budget'] = total_budget
    return redirect(url_for('financial_statistics'))
