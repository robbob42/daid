document.getElementById('dm').addEventListener('click', () => sendMessage({ action: 'Registering', role: 'Dungeon Master' }));
document.getElementById('storyteller').addEventListener('click', () => sendMessage({ action: 'Registering', role: 'Storyteller' }));
document.getElementById('hero').addEventListener('click', () => sendMessage({ action: 'Registering', role: 'Hero Creator' }));
document.getElementById('monster').addEventListener('click', () => sendMessage({ action: 'Registering', role: 'Monster Creator' }));
document.getElementById('map').addEventListener('click', () => sendMessage({ action: 'Registering', role: 'Map Generator' }));
document.getElementById('fight').addEventListener('click', () => sendMessage({ action: 'Registering', role: 'Fight Manager' }));
document.getElementById('reset').addEventListener('click', () => sendMessage({ action: 'Reset' }));

function sendMessage(data) {
  chrome.runtime.sendMessage({ action: 'sendSocketMessage', data: data });
  window.close();
}

// background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'sendSocketMessage') {
    sendWebSocketMessage(request.data);
  }
});

function sendWebSocketMessage(data) {
  const socket = new WebSocket('ws://localhost:8765');

  socket.onopen = () => {
    socket.send(JSON.stringify(data)); // Send JSON-encoded data
  };

  socket.onerror = (error) => {
    console.error('WebSocket Error:', error);
  };
}
