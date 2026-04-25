import React from "react";

function AgentSteps({ steps }) {
  const agentNames = [
    "Interface Agent",
    "Data Acquisition Agent",
    "Inspector Agent",
    "Clean Agent",
    "EDA Agent",
    "Feature Agent",
    "Stat Agent",
    "Insight Agent",
    "Reporting Agent"
  ];

  return (
    <div>
      <h4>Agent Workflow Progress</h4>
      <div>
        {agentNames.map((agent, index) => (
          <div
            key={index}
            className={`steps-item ${steps.length > index ? "active" : ""}`}
          >
            <strong>{agent}</strong>
            {steps.length > index && (
              <div className="upload-details">
                {steps[index]}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

export default AgentSteps;
