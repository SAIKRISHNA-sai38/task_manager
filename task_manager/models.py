from task_manager import db, login_manager
from task_manager import bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)

    tasks = db.relationship('Task', backref='owner', lazy=True)

    @property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(
            plain_text_password
        ).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(
            self.password_hash,
            attempted_password
        )


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(length=200), nullable=False)
    deadline = db.Column(db.String(length=30))
    category = db.Column(db.String(length=30))
    priority = db.Column(db.String(length=20), default='Medium')
    completed = db.Column(db.Boolean, default=False)



    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )

    def __repr__(self):
        return f'<Task {self.title}>'