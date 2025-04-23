import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const mockData = {
  "Are all people equal?": {
    chatGptStyle: "Equality is a fundamental concept in many societies...",
    humphreyStyle: "Ah, well, one must be cautious with such a simplistic question, Minister..."
  },
  "How can we achieve educational fairness?": {
    chatGptStyle: "Educational fairness can be achieved through policies that ensure equal access...Educational fairness can be achieved through policies that ensure equal access...Educational fairness can be achieved through policies that ensure equal access...Educational fairness can be achieved through policies that ensure equal access...",
    humphreyStyle: "Ah, yes, educational fairness—such an admirable goal, Minister, but one fraught with complexities...Ah, yes, educational fairness—such an admirable goal, Minister, but one fraught with complexities...Ah, yes, educational fairness—such an admirable goal, Minister, but one fraught with complexities..."
  },
  "Do humans need to work?": {
    chatGptStyle: "Work is an essential part of human life, providing not only the means for survival...",
    humphreyStyle: "Ah, the question of whether humans need to work—how delightfully modern! Minister..."
  }
};


/** Utility to normalize user input for data lookup. */
function normalizeQuestion(str) {
  if (!str) return "";
  let lower = str.toLowerCase().trim();
  return lower.replace(/[?.!,]+$/g, "").trim();
}

function App() {
  const [question, setQuestion] = useState('');
  const [conversation, setConversation] = useState([]);
  const textareaRef = useRef(null);

  // Auto-resize the textarea every time "question" changes.
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [question]);

  const handleQuestionChange = (event) => {
    setQuestion(event.target.value);
  };

  const handlePdfUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || file.type !== "application/pdf") {
      alert("Please upload a valid PDF file.");
      return;
    }
  
    try {
      // Step 1: Request signed URL from backend
      console.log("Fetching upload url:...")
      const res = await axios.post("http://34.55.234.72:8000/api/generate-upload-url", {
        filename: file.name,
      });
      console.log("Signed upload URL:", res.data)
      const signedUrl = res.data.url;

      // Step 2: Upload file directly to GCS
      await axios.put(signedUrl, file, {
        headers: {
          "Content-Type": "application/pdf",
        },
      });
  
      alert("✅ PDF uploaded successfully!");
  
    } catch (error) {
      console.error("Upload failed:", error);
      alert("❌ Upload failed. Please check the console.");
    }
  };

  // Called when the user presses Enter (without Shift) or clicks send button.
  const getResponse = () => {
    if (!question.trim()) return;

    const normalized = normalizeQuestion(question);
    let entryKey = null;
    Object.keys(mockData).forEach((k) => {
      if (normalizeQuestion(k) === normalized) {
        entryKey = k;
      }
    });

    let newEntry = null;
    if (entryKey) {
      newEntry = {
        question,
        chatGptStyle: mockData[entryKey].chatGptStyle,
        humphreyStyle: mockData[entryKey].humphreyStyle,
        selectedStyle: null
      };
    } else {
      newEntry = {
        question,
        chatGptStyle: "Sorry, I don't have an answer to that question.",
        humphreyStyle: "",
        selectedStyle: null
      };
    }

    setConversation([...conversation, newEntry]);
    setQuestion(''); // Clear the textarea
  };

  const setFinalAnswer = (index, style) => {
    const updated = [...conversation];
    updated[index].selectedStyle = style;
    setConversation(updated);
  };

  // Render final answer based on selected style.
  const renderFinalAnswer = (entry) => {
    if (entry.selectedStyle === 'chatGpt') {
      return (
        <div className="answer-bubble chatGpt-bubble">
          <span className="icon">🤖</span>
          <div>{entry.chatGptStyle}</div>
          
        </div>
      );
    } else if (entry.selectedStyle === 'humphrey') {
      return (
        <div className="answer-bubble humphrey-bubble">
          <span className="icon">👔</span>
          <div>{entry.humphreyStyle}</div>
        </div>
      );
    }
    return null;
  };

  const clearChatHistory = () => {
    setConversation([]);
  };

  return (
    <div className="app-container">
      {/* Left Sidebar */}
      <div className="sidebar">
          <div className="sidebar-header">
      <div className="sidebar-logo-frame">
        <img
          src="/image/himanagerlogo.png"
          alt="Hi Manager Logo"
          className="sidebar-logo"
          />
        </div>
        <h2 className="sidebar-title">Hi Manager Chatbot</h2>
      </div>

        <div className="sidebar-body">
          <div className="api-indicator">
            <div className="api-indicator-icon">✓</div>
            <span>API key already provided!</span>
          </div>
          <a
            href="https://example.com/blog"
            target="_blank"
            rel="noreferrer"
            className="blog-link"
          >
            Build Humphrey Style!
          </a>
          <button className="clear-btn" onClick={clearChatHistory}>
            Clear Chat History
          </button>
          <div className="upload-section">
          <label htmlFor="pdf-upload" className="upload-label">Upload PDF</label>
              <input
                id="pdf-upload"
                type="file"
                accept="application/pdf"
                onChange={handlePdfUpload}
              />
        </div>
        </div>
      </div>

      {/* Right Chat Panel */}
      <div className="chat-panel">
        <div className="chat-messages">
          {conversation.map((entry, index) => (
            <div key={index} className="chat-block">
              <div className="question-bubble">
                <strong></strong> {entry.question}
              </div>
              {!entry.selectedStyle && (
                <div className="answers-group">
                  <div className="answer-bubble chatGpt-bubble">
                    <span className="icon">🤖</span>

                    <div>{entry.chatGptStyle}</div>
                    {/* ←── 新增这行 */}
                    <button onClick={() => alert('Citations!')}>
                      See Citations
                    </button>
                  </div>
                  {entry.humphreyStyle && (
                    <div className="answer-bubble humphrey-bubble">
                      <span className="icon">👔</span>
                      <div>{entry.humphreyStyle}</div>
                    </div>
                  )}
                  <div className="choose-buttons">
                    <button onClick={() => setFinalAnswer(index, 'chatGpt')}>
                      Like ChatGPT Answer
                    </button>
                    {entry.humphreyStyle && (
                      <button onClick={() => setFinalAnswer(index, 'humphrey')}>
                        Like Humphrey Answer
                      </button>
                    )}
                  </div>
                </div>
              )}
              {entry.selectedStyle && (
                <div className="final-answer">
                  <strong>
                    Final Answer ({entry.selectedStyle === 'chatGpt' ? 'ChatGPT' : 'Humphrey'} Style):
                  </strong>
                  {renderFinalAnswer(entry)}
                </div>
              )}
            </div>
          ))}
        </div>
        
        {/* Chat Input Area */}
        <div className="chat-input-wrapper">
          <textarea
            ref={textareaRef}
            className="chat-input"
            placeholder="How may I assist you today?"
            value={question}
            onChange={handleQuestionChange}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                getResponse();
              }
            }}
          />
          <button className="send-icon-btn" onClick={getResponse}>
            <span className="send-icon">&#x27A4;</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;











