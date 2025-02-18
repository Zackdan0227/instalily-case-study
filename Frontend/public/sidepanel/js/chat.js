document.addEventListener('DOMContentLoaded', function() {
    const messagesContainer = document.getElementById('messages-container');
    const input = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    let loading = false;

    // Configure marked options for security
    marked.setOptions({
        headerIds: false,
        mangle: false
    });

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function createMessageElement(role, content) {
        const messageContainer = document.createElement('div');
        messageContainer.className = `${role}-message-container`;

        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        
        // Use marked for assistant messages, plain text for user messages
        if (role === 'assistant') {
            contentDiv.innerHTML = marked.parse(content);
        } else {
            contentDiv.textContent = content;
        }

        messageDiv.appendChild(contentDiv);
        messageContainer.appendChild(messageDiv);
        return messageContainer;
    }

    async function handleSend() {
        if (input.value.trim() === '' || loading) return;

        const userMessage = input.value;
        messagesContainer.appendChild(createMessageElement('user', userMessage));
        input.value = '';
        scrollToBottom();

        loading = true;
        sendButton.disabled = true;
        input.disabled = true;

        try {
            const data = await getAIMessage(userMessage);
            if (data && data.response) {
                messagesContainer.appendChild(createMessageElement('assistant', data.response));
                scrollToBottom();
            }
        } catch (error) {
            console.error('Error:', error);
            messagesContainer.appendChild(
                createMessageElement('assistant', `Error: ${error.message}`)
            );
        } finally {
            loading = false;
            sendButton.disabled = false;
            input.disabled = false;
        }
    }

    sendButton.addEventListener('click', handleSend);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            handleSend();
            e.preventDefault();
        }
    });
});