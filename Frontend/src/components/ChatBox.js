import { useEffect, useMemo, useRef, useState } from "react";

import { analyzeQuery, formatApiError } from "../api";
import Charts from "./Charts";
import FileUpload from "./FileUpload";

const CHAT_HISTORY_KEY = "autoinsights.chatHistory";
const UPLOADED_FILE_KEY = "autoinsights.uploadedFile";
const UPLOADED_FILE_NAME_KEY = "autoinsights.uploadedFileName";

const getTimestamp = () =>
  new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });

const formatMessageContent = (content, type) => {
  if (!content || type === "user") {
    return content;
  }

  // Convert markdown-style headings to cleaner readable sections.
  return content
    .split("\n")
    .map((line) => line.replace(/^#{1,6}\s+/, ""))
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
};

function ChatBox() {
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState(() => {
    try {
      const saved = localStorage.getItem(CHAT_HISTORY_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [loading, setLoading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(
    () => localStorage.getItem(UPLOADED_FILE_KEY) || null,
  );
  const [uploadedFileName, setUploadedFileName] = useState(
    () => localStorage.getItem(UPLOADED_FILE_NAME_KEY) || null,
  );
  const logRef = useRef(null);

  const quickPrompts = useMemo(
    () => [
      "Give me a quick profile of this dataset.",
      "Show trends and outliers with visuals.",
      "What are the top correlations I should care about?",
    ],
    [],
  );

  useEffect(() => {
    localStorage.setItem(CHAT_HISTORY_KEY, JSON.stringify(chatHistory));
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [chatHistory]);

  useEffect(() => {
    if (uploadedFile) {
      localStorage.setItem(UPLOADED_FILE_KEY, uploadedFile);
    } else {
      localStorage.removeItem(UPLOADED_FILE_KEY);
    }
  }, [uploadedFile]);

  useEffect(() => {
    if (uploadedFileName) {
      localStorage.setItem(UPLOADED_FILE_NAME_KEY, uploadedFileName);
    } else {
      localStorage.removeItem(UPLOADED_FILE_NAME_KEY);
    }
  }, [uploadedFileName]);

  const handleFileUpload = (filename, originalName = filename) => {
    setUploadedFile(filename);
    setUploadedFileName(originalName);
    setChatHistory((prev) => [
      ...prev,
      {
        type: "system",
        content: `Dataset "${originalName}" uploaded successfully! You can now ask questions about this data.`,
        time: getTimestamp(),
      },
    ]);
  };

  const handleSubmit = async () => {
    if (!input.trim()) return;

    const userMessage = input.trim();
    setInput("");

    setChatHistory((prev) => [
      ...prev,
      {
        type: "user",
        content: userMessage,
        time: getTimestamp(),
      },
    ]);

    setLoading(true);

    try {
      const res = await analyzeQuery(userMessage, uploadedFile);

      setChatHistory((prev) => [
        ...prev,
        {
          type: "ai",
          content: res.text,
          charts: res.charts || [],
          steps: res.steps || [],
          time: getTimestamp(),
        },
      ]);
    } catch (err) {
      setChatHistory((prev) => [
        ...prev,
        {
          type: "error",
          content: formatApiError(
            err,
            "Error connecting to backend. Please try again.",
          ),
          time: getTimestamp(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const applyQuickPrompt = (prompt) => setInput(prompt);

  const clearConversation = () => {
    setChatHistory([]);
  };

  return (
    <div className="chat-layout">
      <aside className="left-panel panel">
        <div className="panel-title">
          <h3>Workspace</h3>
          <span className="pill pill-neutral">v1</span>
        </div>
        <FileUpload onFileUpload={handleFileUpload} disabled={loading} />
        <div className="dataset-card">
          <div className="dataset-label">Active dataset</div>
          <div className="dataset-value">
            {uploadedFileName || uploadedFile || "None"}
          </div>
          <div className="dataset-hint">
            Upload a file to unlock analysis & visualizations.
          </div>
        </div>
        <ul className="hint-list">
          <li>Upload CSV, XLSX, XLS, or JSON datasets.</li>
          <li>Ask descriptive, diagnostic, or comparative questions.</li>
          <li>Review generated charts and agent execution steps.</li>
        </ul>
      </aside>

      <section className="chat-panel panel">
        <div className="chat-header">
          <div>
            <div className="chat-title">AI Analyst</div>
            <div className="chat-subtitle">
              Ask questions • get charts • see agent steps
            </div>
          </div>
          <div className="chat-actions">
            <span className="pill pill-neutral">{chatHistory.length} msgs</span>
            {uploadedFile && (
              <span className="pill pill-accent">
                Dataset: {uploadedFileName || uploadedFile}
              </span>
            )}
            <button
              type="button"
              className="btn btn-ghost"
              onClick={clearConversation}
              disabled={loading || chatHistory.length === 0}
            >
              Clear
            </button>
          </div>
        </div>

        <div className="message-log" ref={logRef} role="log" aria-live="polite">
        {chatHistory.length === 0 && (
          <div className="empty-state">
            <div className="empty-hero" aria-hidden="true">
              <div className="empty-orb" />
              <div className="empty-orb orb2" />
              <div className="empty-orb orb3" />
            </div>
            <div className="empty-title">Start an analysis</div>
            <div className="empty-text">
              Upload a dataset on the left, then ask a question like “show trends
              and outliers” or “what correlations matter most?”
            </div>
          </div>
        )}

        {chatHistory.map((message, index) => (
          <div key={index} className={`row ${message.type === "user" ? "user" : ""}`}>
            <div className="avatar" aria-hidden="true">
              {message.type === "user" ? "U" : message.type === "ai" ? "AI" : "•"}
            </div>
            <div className={`bubble ${message.type}`}>
              <div className="bubble-header">
                <strong>{message.type.toUpperCase()}</strong>
                <span>{message.time || "--:--"}</span>
              </div>
              {message.type === "ai" &&
                message.charts &&
                message.charts.length > 0 && (
                  <div>
                    <Charts charts={message.charts} />
                  </div>
                )}

              <div className="message-content">
                {formatMessageContent(message.content, message.type)}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="empty-state">
            <div className="loading-row">
              <div className="spinner" aria-hidden="true" />
              <div>
                <div className="empty-title">Analyzing</div>
                <div className="empty-text">Agents are working on your query…</div>
              </div>
            </div>
          </div>
        )}
        </div>

        <div className="quick-prompts">
          {quickPrompts.map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => applyQuickPrompt(prompt)}
              disabled={loading}
            >
              {prompt}
            </button>
          ))}
        </div>

        <div className="composer">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          placeholder="Ask questions about your data..."
          disabled={loading}
          rows={2}
          aria-label="Ask the AI analyst"
        />
        <button
          onClick={handleSubmit}
          disabled={loading || !input.trim()}
          className="btn btn-primary"
        >
          {loading ? "Analyzing..." : "Send"}
        </button>
        </div>

      </section>
    </div>
  );
}

export default ChatBox;
