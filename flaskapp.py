from flask import Flask, render_template, url_for, flash, redirect
from forms import LoginForm, AdminLoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '66334d8be4b779a6f829916546c8e7df'


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return 'about page'

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	formAdmin = AdminLoginForm()

	if form.validate_on_submit():
		if form.login.data == 'admin':
			flash('Zalogowano pomyślnie', 'success')
			return redirect(url_for('home'))
		else:
			flash('Logowanie nieudane. Sprawdź poprawność wpisanych danych', 'danger')	

	return render_template('login.html', title='Zaloguj się', form=form)

if __name__ == '__main__':
	app.run(debug=True)