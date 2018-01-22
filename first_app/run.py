from hello_world import app
import os

app.secret_key = os.urandom(24)
app.run(debug=True)
#port = int(os.environ.get('PORT', 5000))

