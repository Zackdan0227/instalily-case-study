// ChatWindow.js

import React, { useState, useEffect, useRef } from "react";
import "./ChatWindow.css";
import { getAIMessage } from "../api/api";
import { marked } from "marked";

function ChatWindow() {

  const defaultMessage = [{
    role: "assistant",
    content: "Hi, how can I help you today?"
  }];

  const [messages, setMessages] = useState(defaultMessage);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);  // ✅ Added loading state

  const messagesEndRef = useRef(null);

  // Configure marked options for better markdown rendering
  marked.setOptions({
    breaks: true,  // Adds <br> on single line breaks
    gfm: true      // GitHub Flavored Markdown
  });

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (input.trim() === "" || loading) return;

    const userMessage = { role: "user", content: input };
    setMessages(prevMessages => [...prevMessages, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const data = await getAIMessage(input);
      
      // Log only the received response
      console.log("🤖 Processing Response:", {
        receivedData: data
      });

      // Check if we have a valid response
      if (!data || !data.response) {
        throw new Error("No response received from server");
      }

      const newMessage = {
        role: "assistant",
        content: data.response
      };

      setMessages(prevMessages => [...prevMessages, newMessage]);

    } catch (error) {
      console.error("Error:", error.message);
      setMessages(prevMessages => [...prevMessages, {
        role: "assistant",
        content: `Error: ${error.message}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  const renderMessage = (message) => {
    console.log("🎨 Rendering message:", {
      role: message.role,
      contentLength: message.content?.length,
      contentType: typeof message.content
    });

    try {
      // Convert markdown to HTML and sanitize
      const htmlContent = marked(message.content);
      console.log("✨ Converted markdown to HTML:", {
        originalLength: message.content?.length,
        htmlLength: htmlContent?.length
      });
      
      return (
        <div className={`message ${message.role}-message`}>
          <div 
            className="message-content"
            dangerouslySetInnerHTML={{
              __html: htmlContent
            }}
          />
        </div>
      );
    } catch (error) {
      console.error("❌ Error rendering message:", error);
      return (
        <div className={`message ${message.role}-message error`}>
          <div className="message-content">
            Error rendering message: {error.message}
          </div>
        </div>
      );
    }
  };

  return (
    <div className="messages-container">
      {messages.map((message, index) => {
        console.log(`📝 Rendering message ${index}:`, {
          role: message.role,
          hasContent: !!message.content,
          contentLength: message.content?.length
        });
        
        return (
          <div key={index} className={`${message.role}-message-container`}>
            {message.content && renderMessage(message)}
          </div>
        );
      })}
      {loading && (
        <div className="typing-indicator">
          <span></span>
          <span></span>
          <span></span>
        </div>
      )}
      <div ref={messagesEndRef} />

      <div className="input-area">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
          onKeyPress={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              handleSend();
              e.preventDefault();
            }
          }}
          disabled={loading} // ✅ Disable input when loading
        />
        <button className="send-button" onClick={handleSend} disabled={loading}>
          {loading ? "..." : "Send"} {/* ✅ Show loading state */}
        </button>
      </div>
    </div>
  );
}

export default ChatWindow;
