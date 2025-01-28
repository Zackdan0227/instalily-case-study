// api.js

export const getAIMessage = async (message) => {
  try {
    const response = await fetch("http://localhost:5001/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    // Only log the received data
    console.log("📥 Backend Response:", {
      data: data,
      response: data.response
    });

    return data;
  } catch (error) {
    console.error("🚨 API Error:", error.message);
    throw error;
  }
};
