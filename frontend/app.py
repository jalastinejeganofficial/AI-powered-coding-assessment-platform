from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import requests
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'ai-interview-simulator-secret-key'

# Backend API configuration
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
API_BASE_URL = f"{BACKEND_URL}/api/v1"

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        
        # Prepare payload for API request
        payload = {
            "username": username,
            "email": email,
            "full_name": full_name,
            "password": password
        }
        
        try:
            # Make request to backend API
            response = requests.post(f"{API_BASE_URL}/user/", json=payload)
            
            if response.status_code == 200:
                flash('Registration successful!', 'success')
                return redirect(url_for('login'))
            else:
                # Safely parse error response
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', f'Registration failed with status {response.status_code}')
                except ValueError:
                    error_msg = f'Registration failed: {response.text}'
                flash(f'Registration failed: {error_msg}', 'error')
        except requests.exceptions.ConnectionError:
            flash('Error connecting to backend: Could not reach server', 'error')
        except Exception as e:
            flash(f'Error connecting to backend: {str(e)}', 'error')
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        # Get form data
        username_or_email = request.form['username']
        password = request.form['password']
        
        try:
            # Make login request to backend API
            payload = {
                "username_or_email": username_or_email,
                "password": password
            }
            
            response = requests.post(f"{API_BASE_URL}/user/login", json=payload)
            
            if response.status_code == 200:
                user_data = response.json()
                # Store user info in session
                session['user_id'] = user_data['id']
                session['username'] = user_data['username']
                session['email'] = user_data['email']
                session['full_name'] = user_data['full_name']
                
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', 'Invalid credentials')
                except ValueError:
                    error_msg = 'Invalid credentials'
                flash(error_msg, 'error')
        except requests.exceptions.ConnectionError:
            flash('Error connecting to backend: Could not reach server', 'error')
        except Exception as e:
            flash(f'Error during login: {str(e)}', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard"""
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access the dashboard', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    
    try:
        # Get user details from backend
        user_response = requests.get(f"{API_BASE_URL}/user/{user_id}")
        
        if user_response.status_code == 200:
            user_data = user_response.json()
        else:
            user_data = {
                'id': session['user_id'],
                'username': session.get('username', 'Unknown'),
                'email': session.get('email', ''),
                'full_name': session.get('full_name', 'Unknown'),
                'total_score': 0,
                'interview_count': 0
            }
        
        # Get user's interview history
        interview_response = requests.get(f"{API_BASE_URL}/interview/user/{user_id}/sessions?limit=5")
        
        if interview_response.status_code == 200:
            try:
                interview_history = interview_response.json()
            except ValueError:
                interview_history = []
        else:
            interview_history = []
        
        return render_template('dashboard.html', 
                             user=user_data, 
                             interview_history=interview_history)
    except requests.exceptions.ConnectionError:
        flash('Error connecting to backend: Could not reach server', 'error')
        return render_template('dashboard.html', 
                             user={'username': session.get('username', 'Unknown')}, 
                             interview_history=[])
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', 
                             user={'username': session.get('username', 'Unknown')}, 
                             interview_history=[])

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@app.route('/interviews')
def interviews():
    """Interview management page"""
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access interviews', 'error')
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    username = session.get('username', 'Unknown User')
    
    # Get user's interview history
    try:
        interview_response = requests.get(f"{API_BASE_URL}/interview/user/{user_id}/sessions?limit=10")
        if interview_response.status_code == 200:
            try:
                interview_history = interview_response.json()
            except ValueError:
                interview_history = []
        else:
            interview_history = []
    except Exception:
        interview_history = []
    
    return render_template('interviews.html', 
                         user_id=user_id, 
                         username=username,
                         interview_history=interview_history)

@app.route('/interview/start', methods=['POST'])
def start_interview():
    """Start a new interview session for logged in user"""
    # Check if user is logged in
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Please log in to start an interview"})
    
    user_id = session['user_id']
    interview_type = request.json.get('interview_type', 'dsa')
    
    payload = {
        "user_id": user_id,
        "interview_type": interview_type
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/interview/start", json=payload)
        
        if response.status_code == 200:
            try:
                interview_data = response.json()
                return jsonify({"success": True, "session_id": interview_data['id']})
            except ValueError:
                return jsonify({"success": False, "error": "Invalid response from backend"})
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', f'Failed to start interview: {response.status_code}')
            except ValueError:
                error_msg = f'Failed to start interview: {response.text}'
            return jsonify({"success": False, "error": error_msg})
    except requests.exceptions.ConnectionError:
        return jsonify({"success": False, "error": "Could not connect to backend server"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/interview/<int:session_id>')
def interview(session_id):
    """Interview session page"""
    try:
        # Get interview session details
        session_response = requests.get(f"{API_BASE_URL}/interview/{session_id}")
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            
            # Get user details
            user_response = requests.get(f"{API_BASE_URL}/user/{session_data['user_id']}")
            user_data = user_response.json() if user_response.status_code == 200 else {}
            
            # Get interview questions
            questions_response = requests.get(f"{API_BASE_URL}/interview/{session_id}/questions")
            questions = questions_response.json() if questions_response.status_code == 200 else []
            
            return render_template('interview.html', 
                                 session=session_data, 
                                 user=user_data,
                                 questions=questions, 
                                 session_id=session_id)
        else:
            flash('Interview session not found', 'error')
            return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error accessing interview: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/submit_response', methods=['POST'])
def submit_response():
    """Submit response to a question"""
    data = request.json
    
    payload = {
        "interview_session_id": data['session_id'],
        "interview_question_id": data['question_id'],
        "response_text": data['response'],
        "programming_language": data.get('language', 'python'),
        "execution_time": data.get('execution_time')
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/interview/{data['session_id']}/response", json=payload)
        
        if response.status_code == 200:
            try:
                result = response.json()
                return jsonify({"success": True, "result": result})
            except ValueError:
                return jsonify({"success": False, "error": "Invalid response from backend"})
        else:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', f'Failed to submit response: {response.status_code}')
            except ValueError:
                error_msg = f'Failed to submit response: {response.text}'
            return jsonify({"success": False, "error": error_msg})
    except requests.exceptions.ConnectionError:
        return jsonify({"success": False, "error": "Could not connect to backend server"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/leaderboard')
def leaderboard():
    """Leaderboard page"""
    try:
        response = requests.get(f"{API_BASE_URL}/leaderboard/")
        
        if response.status_code == 200:
            try:
                leaderboard_data = response.json()
            except ValueError:
                leaderboard_data = []
                flash('Received invalid data from backend', 'error')
        else:
            leaderboard_data = []
            flash(f'Failed to load leaderboard: {response.status_code}', 'error')
        
        return render_template('leaderboard.html', leaderboard=leaderboard_data)
    except requests.exceptions.ConnectionError:
        flash('Error connecting to backend: Could not reach server', 'error')
        return render_template('leaderboard.html', leaderboard=[])
    except Exception as e:
        flash(f'Error loading leaderboard: {str(e)}', 'error')
        return render_template('leaderboard.html', leaderboard=[])

@app.route('/api/users/<int:user_id>')
def get_user_api(user_id):
    """Get user details from backend"""
    try:
        response = requests.get(f"{API_BASE_URL}/user/{user_id}")
        
        if response.status_code == 200:
            try:
                return jsonify(response.json())
            except ValueError:
                return jsonify({"error": "Invalid response from backend"}), 500
        else:
            return jsonify({"error": "User not found"}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Could not connect to backend server"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)