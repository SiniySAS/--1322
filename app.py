from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- Модели ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default="active")


with app.app_context():
    db.create_all()


# --- HTML-главная страница ---
@app.route('/')
def home():
    return render_template('index.html')


# --- API ---
@app.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([
        {"id": p.id, "name": p.name, "description": p.description, "user_id": p.user_id}
        for p in projects
    ])


@app.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json()
    new_project = Project(
        user_id=data['user_id'],
        name=data['name'],
        description=data.get('description', '')
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({"message": "Project created successfully"}), 201



@app.route('/')
def index():
    return """
    <h1>Серверная часть платформы для тестирования прототипов игр</h1>
    <p>Доступные маршруты:</p>
    <ul>
        <li><a href="/users">/users</a> — список пользователей</li>
        <li><a href="/projects">/projects</a> — список проектов</li>
        <li>POST /projects — создать проект</li>
        <li>POST /sessions — начать тестовую сессию</li>
        <li>POST /sessions/&lt;id&gt;/stop — завершить сессию</li>
    </ul>
    """


if __name__ == '__main__':
    app.run(debug=True)
