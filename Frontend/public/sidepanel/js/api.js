const API_URL = 'http://localhost:5001/chat';

async function getAIMessage(message) {
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();
        console.log('📥 Backend Response:', {
            data: data,
            response: data.response
        });

        return data;
    } catch (error) {
        console.error('🚨 API Error:', error.message);
        throw error;
    }
}