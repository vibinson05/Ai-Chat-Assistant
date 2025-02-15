import { useState, useEffect, useRef } from "react";
import axios from "axios";
import { Send, Mic, Trash2 } from "lucide-react";
import "./App.css";
import { useNavigate } from "react-router-dom";

function App() {
  const [userInput, setUserInput] = useState("");
  const [chat, setChat] = useState([]);
  const [isListening, setIsListening] = useState(false);
  const chatBoxRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/history")
      .then((response) => setChat(response.data))
      .catch((error) => console.error("Error fetching history:", error));
  }, []);

  useEffect(() => {
    chatBoxRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  const handleLogout = async () => {
    await fetch("http://127.0.0.1:8000/logout", {
      method: "POST",
      credentials: "include",
    });
    navigate("/login");
  };

  const handleMicClick = () => {
    if (!("SpeechRecognition" in window || "webkitSpeechRecognition" in window)) {
      alert("Your browser does not support speech recognition.");
      return;
    }

    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.continuous = false;
    recognition.lang = "en-US";

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);

    recognition.onresult = (event) => {
      const speechToText = event.results[0][0].transcript;
      setUserInput(speechToText);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      setIsListening(false);
    };

    recognition.start();
  };

  const handleSend = async () => {
    if (!userInput.trim()) return;

    const userMessage = { user: userInput, bot: "Typing..." };
    setChat([...chat, userMessage]);

    try {
      const response = await axios.post("http://127.0.0.1:8000/chat", { message: userInput });
      const botResponse = { user: userInput, bot: response.data.reply };
      setChat([...chat, botResponse]);
    } catch (error) {
      console.error("Error:", error);
      const errorMessage = { user: userInput, bot: "Error processing your request." };
      setChat([...chat, errorMessage]);
    }

    setUserInput("");
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      e.preventDefault(); // Prevent default behavior
      handleSend();
    }
  };

  const handleClearHistory = async () => {
    try {
      await axios.delete("http://127.0.0.1:8000/clear_history");
      setChat([]);
    } catch (error) {
      console.error("Error clearing history:", error);
    }
  };

  return (
    <div className="app-container">
      <div className="sidebar">
        <div className="sidebar-title">Chat Assistant</div>

        <div className="chat-history">
          <h3>Chat History</h3>
          {chat.map((msg, index) => (
            <div key={index} className="history-item">
              {msg.user.length > 30 ? msg.user.substring(0, 30) + "..." : msg.user}
            </div>
          ))}
        </div>

        <button className="clear-history-btn" onClick={handleClearHistory}  >
          <Trash2 size={18} /> Clear Chat History
        </button>
        <button className="btn btn-danger" onClick={handleLogout}  >
          Logout
        </button>
      </div>

      <div className="chat-section">
        <div className="chat-box">
          {chat.map((msg, index) => (
            <div key={index} className="message">
              <strong>You:</strong> {msg.user}
              <br />
              <strong>Gemini:</strong> {msg.bot}
            </div>
          ))}
          <div ref={chatBoxRef}></div>
        </div>

        <div className="input-section">
          <input
            type="text"
            placeholder="Enter a prompt..."
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            onKeyDown={handleKeyPress} 
          />
          <button onClick={handleSend}>
            <Send size={24} />
          </button>
          <button onClick={handleMicClick}  onKeyDown={handleKeyPress} className={isListening ? "listening" : ""}>
            <Mic size={24} color={isListening ? "red" : "black"} />
          </button>
        </div>

        <p className="footer">Gemini can make mistakes. Verify important info.</p>
      </div>
    </div>
  );
}

export default App;
