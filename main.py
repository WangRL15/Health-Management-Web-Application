from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# MySQL配置
username = ''
password = ''
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{username}:{password}@localhost/test'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# 數據庫模型
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # 增加長度以適應哈希後的密碼
    email = db.Column(db.String(120), unique=True, nullable=False)
    height = db.Column(db.Float)
    weight = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 添加創建時間

class Workout(db.Model):
    __tablename__ = 'workouts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    date = db.Column(db.DateTime, nullable=False)
    exercise_type = db.Column(db.String(100))
    sets = db.Column(db.Integer)
    reps = db.Column(db.Integer)
    weight = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DietLog(db.Model):
    __tablename__ = 'diet_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    date = db.Column(db.DateTime, nullable=False)
    food_name = db.Column(db.String(100))
    calories = db.Column(db.Float)
    protein = db.Column(db.Float)
    carbs = db.Column(db.Float)
    fat = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ExerciseLog(db.Model):
    __tablename__ = 'exercise_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    date = db.Column(db.DateTime, nullable=False)
    calories_burned = db.Column(db.Float)
    duration = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class HealthGoal(db.Model):
    __tablename__ = 'health_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    target_weight = db.Column(db.Float)
    target_bmi = db.Column(db.Float)
    target_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


#路由
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # 檢查用戶名是否已存在
        if User.query.filter_by(username=username).first():
            flash('用戶名已存在')
            return redirect(url_for('register'))
            
        # 檢查郵箱是否已存在
        if User.query.filter_by(email=email).first():
            flash('郵箱已被使用')
            return redirect(url_for('register'))
            
        # 創建新用戶
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            email=email
        )
        
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('註冊成功，請登入')
            return redirect(url_for('login'))
        except Exception as e:
            print(e)
            db.session.rollback()
            flash('註冊失敗，請稍後再試')
            return redirect(url_for('register'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('登入成功！')
            return redirect(url_for('profile'))
        flash('用戶名或密碼錯誤')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('您已成功登出')
    return redirect(url_for('login'))

# 檢查用戶是否已登入的裝飾器
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('請先登入')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return redirect(url_for('profile'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        user.height = request.form.get('height', type=float)
        user.weight = request.form.get('weight', type=float)
        try:
            db.session.commit()
            flash('個人資料更新成功')
        except:
            db.session.rollback()
            flash('更新失敗，請稍後再試')
    return render_template('profile.html', user=user)

@app.route('/workout', methods=['GET', 'POST'])
def workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_workout = Workout(
            user_id=session['user_id'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            exercise_type=request.form['exercise_type'],
            sets=request.form.get('sets', type=int),
            reps=request.form.get('reps', type=int),
            weight=request.form.get('weight', type=float)
        )
        db.session.add(new_workout)
        db.session.commit()
        flash('Workout added successfully')
    workouts = Workout.query.filter_by(user_id=session['user_id']).all()
    return render_template('workout.html', workouts=workouts)

@app.route('/diet', methods=['GET', 'POST'])
def diet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_diet_log = DietLog(
            user_id=session['user_id'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            food_name=request.form['foodName'],
            calories=request.form.get('calories', type=float),
            protein=request.form.get('protein', type=float),
            carbs=request.form.get('carbs', type=float),
            fat=request.form.get('fat', type=float)
        )
        db.session.add(new_diet_log)
        db.session.commit()
        flash('Diet log added successfully')
    diet_logs = DietLog.query.filter_by(user_id=session['user_id']).all()
    return render_template('diet.html', diet_logs=diet_logs)

@app.route('/exercise', methods=['GET', 'POST'])
def exercise():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        new_exercise_log = ExerciseLog(
            user_id=session['user_id'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            calories_burned=request.form.get('calories_burned', type=float),
            duration=request.form.get('duration', type=int)
        )
        db.session.add(new_exercise_log)
        db.session.commit()
        flash('Exercise log added successfully')
    exercise_logs = ExerciseLog.query.filter_by(user_id=session['user_id']).all()
    return render_template('exercise.html', exercise_logs=exercise_logs)

@app.route('/analysis')
def analysis():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    
    # 獲取數據用於分析
    diet_logs = DietLog.query.filter_by(user_id=session['user_id']).all()
    exercise_logs = ExerciseLog.query.filter_by(user_id=session['user_id']).all()
    
    # 處理數據用於圖表顯示
    diet_data = {str(log.date.date()): log.calories for log in diet_logs}
    exercise_data = {str(log.date.date()): log.calories_burned for log in exercise_logs}

    # 調試資訊
    print("Diet Data:", diet_data)
    print("Exercise Data:", exercise_data)

    return render_template('analysis.html', 
                         diet_data=json.dumps(diet_data),
                         exercise_data=json.dumps(exercise_data))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)