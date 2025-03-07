let activeGeminiTabId = null; // Global variable to store the active Gemini tab ID

function generateUUID() { // Add this function to generate UUIDs
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'sendSocketMessage') {
        let tabId = activeGeminiTabId; // Use the stored activeGeminiTabId
        if (tabId === undefined) {
            tabId = "popup"; // Or any other identifier for non-tab contexts
        }
        sendWebSocketMessage(request.data, tabId);
    }
});

chrome.tabs.onRemoved.addListener((tabId, removeInfo) => {
    if (tabId === activeGeminiTabId) {
      activeGeminiTabId = null; // Clear the stored ID when the tab is closed
    }
  });
  
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && tab.url.startsWith('https://gemini.google.com/')) {
        activeGeminiTabId = tabId; // Store the tab ID when a Gemini tab is active


        
        // Inject the script to add the custom button
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            function: () => {
                // Create the button element
                const customButton = document.createElement('button');
                customButton.textContent = 'My Custom Button';
                customButton.id = 'myCustomButton';
        
                // Style the button with a D&D theme
                customButton.style.position = 'fixed';
                customButton.style.bottom = '10px';
                customButton.style.right = '10px';
                customButton.style.backgroundColor = '#555'; // Darker background
                customButton.style.color = '#d4af37'; // Gold text color
                customButton.style.border = '2px solid #d4af37'; // Gold border
                customButton.style.padding = '8px 12px';
                customButton.style.fontFamily = 'MedievalSharp, serif'; // D&D font
                customButton.style.fontSize = '16px';
                customButton.style.borderRadius = '5px';
                customButton.style.cursor = 'pointer';
                customButton.style.zIndex = '9999'; // Ensure it's on top

                // Add an event listener to send clipboard text to server
                customButton.addEventListener('click', async () => {
                    try {
                        const clipboardText = await navigator.clipboard.readText();
                        // Send a message to the background script
                        chrome.runtime.sendMessage({ action: 'sendSocketMessage', data: JSON.parse(clipboardText) });
                    } catch (err) {
                        console.error('Failed to read or send clipboard contents: ', err);
                    }
                });
  
                // Append the button to the body
                document.body.appendChild(customButton);
            }
        });


        chrome.action.openPopup();
    }
});


// WebSocket setup outside sendWebSocketMessage
const socket = new WebSocket('ws://localhost:8765');
let heartbeatInterval;

socket.onopen = () => {
  // Start the heartbeat after the connection is established
  heartbeatInterval = setInterval(() => {
    socket.send(JSON.stringify({ action: 'Heartbeat' }));
  }, 25000); // Send heartbeat every 25 seconds

  socket.send(JSON.stringify({ action: 'Heartbeat' }));
};

socket.onmessage = (event) => {
  try {
    const messageData = JSON.parse(event.data);
    // Find the tab with the matching tabId
    chrome.tabs.query({ url: 'https://gemini.google.com/*' }, (tabs) => {
      const targetTab = tabs.find(tab => tab.id === messageData.tab_id);
      if (targetTab) {
        // Inject a script to paste the message into the specified element
        chrome.scripting.executeScript({
          target: { tabId: targetTab.id },
          function: (message) => {
            const messageElement = document.querySelector('#app-root > main > side-navigation-v2 > bard-sidenav-container > bard-sidenav-content > div.content-wrapper > div > div.content-container > chat-window > div > input-container > div > input-area-v2 > div > div > div.text-input-field_textarea-wrapper.ng-tns-c3688966844-2 > div > div > rich-textarea > div.ql-editor.ql-blank.textarea.new-input-ui > p');
            if (messageElement) {
              messageElement.textContent = message; // Paste the message

              // Add a delay before clicking the submit button
              setTimeout(() => {
                // const submitButton = document.querySelector('#app-root > main > side-navigation-v2 > bard-sidenav-container > bard-sidenav-content > div.content-wrapper > div > div.content-container > chat-window > div > input-container > div > input-area-v2 > div > div > div.trailing-actions-wrapper.ng-tns-c3688966844-2 > div > div.mat-mdc-tooltip-trigger.send-button-container.ng-tns-c3688966844-2.inner.ng-star-inserted.visible > button');
                // if (submitButton) {
                //   submitButton.click();
                // } else {
                //   console.error("Submit button not found.");
                // }
                const enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    which: 13,
                    keyCode: 13,
                    bubbles: true,
                    cancelable: true
                  });
                
                  messageElement.dispatchEvent(enterEvent);
              }, 500); // Adjust the delay (in milliseconds) as needed

            } else {
              console.error("Message element not found.");
            }
          },
          args: [messageData.message] // Pass the message content
        });
      } else {
        console.error("Tab not found for message:", messageData);
      }
    });
  } catch (error) {
    console.error("Error parsing server response:", error);
  }
};

socket.onerror = (error) => {
    console.error('WebSocket Error:', error);
};

socket.onclose = (event) => {
    clearInterval(heartbeatInterval); // Clear the interval on close
};

function sendWebSocketMessage(data, tabId) {
    data.uuid = generateUUID();
    data.tabId = tabId;
    console.log(data, tabId)
    socket.send(JSON.stringify(data)); // Use the existing socket connection
}
