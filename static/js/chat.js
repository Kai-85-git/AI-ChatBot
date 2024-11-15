document.addEventListener('DOMContentLoaded', function() {
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const messagesContainer = document.getElementById('messages');

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function createMessageElement(message, isAi) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isAi ? 'ai' : 'user'}`;

        const headerDiv = document.createElement('div');
        headerDiv.className = 'message-header';
        
        const usernameSpan = document.createElement('strong');
        usernameSpan.textContent = message.username;
        
        const timestampSpan = document.createElement('small');
        timestampSpan.className = 'text-muted';
        const timestamp = new Date(message.timestamp);
        timestampSpan.textContent = timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = message.content;

        headerDiv.appendChild(usernameSpan);
        headerDiv.appendChild(timestampSpan);
        messageDiv.appendChild(headerDiv);
        messageDiv.appendChild(contentDiv);

        return messageDiv;
    }

    messageForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) return;

        messageInput.value = '';
        messageInput.disabled = true;

        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Add user message
            messagesContainer.appendChild(createMessageElement(data.user_message, false));
            // Add AI response
            messagesContainer.appendChild(createMessageElement(data.ai_message, true));
            
            scrollToBottom();
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to send message. Please try again.');
        } finally {
            messageInput.disabled = false;
            messageInput.focus();
        }
    });

    // Scroll to bottom on initial load
    scrollToBottom();
});
