from werkzeug.contrib.profiler import ProfilerMiddleware
from main import app

app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
app.run(debug=True)
