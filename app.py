from flask import Flask, request, render_template, copy_current_request_context, current_app
from flask_socketio import SocketIO, send, emit, disconnect
from flask_celery import make_celery
import eventlet
eventlet.monkey_patch()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

broker_url = 'redis://'

app.config.update(
  CELERY_BROKER_URL = broker_url,
  result_backend = 'redis://'
)

sio = SocketIO(app, message_queue='redis://', cors_allowed_origins='*')

celery = make_celery(app)


@app.route('/')
def index():
  return render_template('index.html')


@sio.on('connect', namespace='/test')
def socket_connect_event():
  print('connected')
  emit('client_connected', {'msg': 'Connected to the Socket Server'})  


# background task with celery
@celery.task(name="celery_background_task")
def celery_bg_task():
  with app.app_context():
    socketio = SocketIO(current_app, message_queue='redis://')
    print('Background Task Starting ...')
    socketio.sleep(10)
    socketio.emit('celery_bg_task', {'msg': 'Celery Background Task Done'}, namespace='/test')
    print('Background Task Done with Celery')


@sio.on('celery_bg', namespace = '/test')
def celery_bg():
  print('Celery Background Task Request Received')
  celery_bg_task.delay()
  sio.emit('celery_task_received', {'msg': 'Celery Task is being processed'}, namespace='/test')


# task from another process (thread)
def task():
  sio.sleep(10)
  with app.test_request_context('/'):
    sio.emit('update_status', {'msg': 'Status Updated Successfully'}, namespace='/test')
    print('Background task done!')



@sio.on('subscribe', namespace='/test')
def subscribe(data):
  status = data['status']
  # user = data['user']
  print('subscribed with status : ', status );
  sio.start_background_task(task)


# receive msg from client
@sio.on('send_msg', namespace='/test')
def send_msg(data):
  msg = data['msg']
  print('Client :', msg)
  emit('msg_status', {'msg': 'Message Received'})


# disconnect from the server
@sio.on('disconnect_server', namespace='/test')
def disconnect_server(data):
  print('Client says', data['msg'])

  @copy_current_request_context
  def can_disconnect():
    print('request object : ', request)
    emit('disconnect_response', {'msg': 'Disconnected Successfully!'}, namespace='/test')
    disconnect()
    print('Disconnected!')
  can_disconnect()

# start server 
if __name__ == '__main__':
  sio.run(app, debug=True)

