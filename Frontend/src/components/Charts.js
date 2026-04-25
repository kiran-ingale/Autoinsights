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
  ResponsiveContainer
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