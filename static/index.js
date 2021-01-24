console.log('static/index.js');
namespace = 'http:127.0.0.1:5000/test';

const sio = io('/test');

const socketIO = io('/completed');

// confirm celery task is received by server
sio.on('celery_task_received', msg => {
  console.log('Celery Task POST response', msg);
});


// listen for Celery Task Update
sio.on('celery_bg_task', msg => {
  console.log('Celery Task Update', msg);
});


function requestCeleryTask () {
  sio.emit('celery_bg');
}

  
// on connect to the socket
sio.on('connect', () => {
  console.log('Connected to the socket!');
});


// on disconnect to the socket
sio.on('disconnect', () => {
  console.log('Disconnected from the socket!');
});


