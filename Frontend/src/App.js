import ChatBox from "./components/ChatBox";
import "./App.css";

function App() {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="topbar-inner">
          <div className="brand">
            <div className="brand-mark" aria-hidden="true">
              AI
            </div>
            <div className="brand-text">
              <div className="brand-title">AutoInsights</div>
              <div className="brand-subtitle">Multi-agent data analysis</div>
            </div>
          </div>
          <div className="topbar-actions">
            <span className="pill pill-neutral">Local dev</span>
            <span className="pill pill-accent">FastAPI + React</span>
          </div>
        </div>
      </header>
      <main>
        <ChatBox />
      </main>
    </div>
  );
}

export default App;