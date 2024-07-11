from . import db
from datetime import datetime

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    allocated_budget = db.Column(db.Integer, nullable=False, default=0)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.Date, nullable=True)

    @property
    def total_tasks(self):
        return Task.query.filter_by(project_id=self.id).count()

    @property
    def work_progress(self):
        total_tasks = self.total_tasks
        if total_tasks == 0:
            return 0
        total_progress = sum(task.work_progress for task in self.tasks)
        return total_progress // total_tasks

    @property
    def total_payment_progress(self):
        total_outgoing_costs = sum(task.outgoing_costs for task in self.tasks)
        if self.allocated_budget == 0:
            return 0
        return (total_outgoing_costs / self.allocated_budget) * 100

    @property
    def total_cost(self):
        return sum(task.cost for task in self.tasks)

    @property
    def remaining_budget(self):
        return self.allocated_budget - self.total_cost

    @property
    def last_payment_date(self):
        dates = [task.last_payment_date for task in self.tasks if task.last_payment_date is not None]
        return max(dates) if dates else None

    @property
    def total_payment(self):
        return sum(task.outgoing_costs for task in self.tasks)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    progress = db.Column(db.Integer, nullable=False, default=0)
    payment_progress = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    outgoing_costs = db.Column(db.Integer, nullable=False, default=0)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.Date, nullable=True)
    last_payment_date = db.Column(db.Date, nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    project = db.relationship('Project', backref=db.backref('tasks', lazy=True))
    subtasks = db.relationship('Subtask', backref='task', lazy=True, cascade="all, delete-orphan")

    @property
    def total_payment(self):
        return self.outgoing_costs

    @property
    def work_progress(self):
        total_subtasks = len(self.subtasks)
        if total_subtasks == 0:
            return 0
        completed_subtasks = sum(1 for subtask in self.subtasks if subtask.status == 'done')
        return (completed_subtasks / total_subtasks) * 100


class Subtask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='planned')
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
