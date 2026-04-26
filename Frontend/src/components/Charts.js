import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter
} from 'recharts';

function Charts({ charts }) {
  if (!charts || charts.length === 0) {
    return null;
  }

  const renderChart = (chart, index) => {
    const { type, title, data, xKey, yKeys, colors } = chart;

    switch (type) {
      case 'line':
        return (
          <div key={index} className="chart-wrapper">
            <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>{title}</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={xKey} />
                <YAxis />
                <Tooltip />
                <Legend />
                {yKeys.map((key, idx) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={colors[idx] || '#8884d8'}
                    strokeWidth={2}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        );

      case 'bar':
        return (
          <div key={index} className="chart-wrapper">
            <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>{title}</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey={xKey} />
                <YAxis />
                <Tooltip />
                <Legend />
                {yKeys.map((key, idx) => (
                  <Bar
                    key={key}
                    dataKey={key}
                    fill={colors[idx] || '#8884d8'}
                  />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </div>
        );

      case 'pie':
        return (
          <div key={index} className="chart-wrapper">
            <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>{title}</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percentage }) => `${name}: ${percentage}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {data.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={colors[idx] || '#8884d8'} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        );

      case 'scatter':
        return (
          <div key={index} className="chart-wrapper">
            <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>{title}</h3>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                <CartesianGrid />
                <XAxis type="number" dataKey="x" name={chart.xLabel || 'X'} />
                <YAxis type="number" dataKey="y" name={chart.yLabel || 'Y'} />
                <Tooltip cursor={{ strokeDasharray: '3 3' }} />
                <Legend />
                <Scatter name={title} data={data} fill={colors[0] || '#8884d8'} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        );

      case 'boxplot':
        return (
          <div key={index} className="chart-wrapper">
            <h3 style={{ textAlign: 'center', marginBottom: '20px' }}>{title}</h3>
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '300px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', padding: '20px' }}>
              {data.map((item, i) => {
                const { min, q1, median, q3, max } = item;
                const range = max - min;
                const scale = (val) => 260 - ((val - min) / range) * 220; // Map values to SVG coordinates (inverted y)
                
                return (
                  <svg key={i} width="200" height="300" viewBox="0 0 200 300">
                    {/* Whiskers (Vertical Lines) */}
                    <line x1="100" y1={scale(min)} x2="100" y2={scale(q1)} stroke="#e2e8f0" strokeWidth="2" strokeDasharray="4" />
                    <line x1="100" y1={scale(q3)} x2="100" y2={scale(max)} stroke="#e2e8f0" strokeWidth="2" strokeDasharray="4" />
                    
                    {/* Horizontal Caps */}
                    <line x1="80" y1={scale(min)} x2="120" y2={scale(min)} stroke="#e2e8f0" strokeWidth="2" />
                    <line x1="80" y1={scale(max)} x2="120" y2={scale(max)} stroke="#e2e8f0" strokeWidth="2" />
                    
                    {/* The Box (Q1 to Q3) */}
                    <rect x="70" y={scale(q3)} width="60" height={scale(q1) - scale(q3)} fill="#8884d8" stroke="#e2e8f0" strokeWidth="2" fillOpacity="0.7" />
                    
                    {/* Median Line */}
                    <line x1="70" y1={scale(median)} x2="130" y2={scale(median)} stroke="#f8fafc" strokeWidth="3" />
                    
                    {/* Labels */}
                    <text x="140" y={scale(max)} fill="#94a3b8" fontSize="10">Max: {max.toFixed(1)}</text>
                    <text x="140" y={scale(q3)} fill="#94a3b8" fontSize="10">Q3: {q3.toFixed(1)}</text>
                    <text x="140" y={scale(median)} fill="#f8fafc" fontSize="10" fontWeight="bold">Med: {median.toFixed(1)}</text>
                    <text x="140" y={scale(q1)} fill="#94a3b8" fontSize="10">Q1: {q1.toFixed(1)}</text>
                    <text x="140" y={scale(min)} fill="#94a3b8" fontSize="10">Min: {min.toFixed(1)}</text>
                    <text x="100" y="290" fill="#e2e8f0" fontSize="12" textAnchor="middle">{item.column || chart.title}</text>
                  </svg>
                );
              })}
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div>
      <h2 style={{ textAlign: 'center', marginBottom: '30px', color: '#e2e8f0' }}>
        📊 Data Visualizations
      </h2>
      {charts.map((chart, index) => renderChart(chart, index))}
    </div>
  );
}

export default Charts;