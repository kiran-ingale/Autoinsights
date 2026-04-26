import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, Any
from scipy import stats

UPLOAD_DIR = Path("Backend/uploads")

def load_dataset(filename: str) -> pd.DataFrame:
    """Load dataset from uploaded file"""
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise FileNotFoundError(f"File {filename} not found")

    file_extension = file_path.suffix.lower()

    try:
        if file_extension == '.csv':
            return pd.read_csv(file_path)
        elif file_extension in ['.xlsx', '.xls']:
            return pd.read_excel(file_path)
        elif file_extension == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
            # Handle different JSON formats
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                # Try to convert dict to DataFrame
                return pd.DataFrame([data]) if all(isinstance(v, (int, float, str)) for v in data.values()) else pd.DataFrame(data)
            else:
                raise ValueError("Unsupported JSON format")
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        raise ValueError(f"Error loading file: {str(e)}")

def analyze_dataset(df: pd.DataFrame, query: str) -> Dict[str, Any]:
    """Analyze dataset based on query and return insights and charts"""

    working_df = df.copy()
    working_df.columns = [str(col).strip().lower() for col in working_df.columns]

    # Basic dataset info
    dataset_info = {
        'rows': len(working_df),
        'columns': len(working_df.columns),
        'column_names': working_df.columns.tolist(),
        'data_types': working_df.dtypes.to_dict(),
        'missing_values': working_df.isnull().sum().to_dict()
    }

    # Determine analysis type based on query keywords
    query_lower = query.lower()

    if any(word in query_lower for word in ['trend', 'time', 'over time', 'temporal']):
        return analyze_trends(working_df, dataset_info)
    elif any(word in query_lower for word in ['correlation', 'relationship', 'correlate']):
        return analyze_correlations(working_df, dataset_info)
    elif any(word in query_lower for word in ['distribution', 'histogram', 'frequency']):
        return analyze_distributions(working_df, dataset_info)
    elif any(word in query_lower for word in ['summary', 'overview', 'describe']):
        return analyze_summary(working_df, dataset_info)
    elif any(word in query_lower for word in ['outlier', 'anomaly', 'extreme']):
        return analyze_outliers(working_df, dataset_info)
    else:
        # General analysis
        return analyze_general(working_df, dataset_info)

def analyze_trends(df: pd.DataFrame, dataset_info: Dict) -> Dict[str, Any]:
    """Analyze trends in time series data"""
    text = f"""
## Trend Analysis Report

### Dataset Overview
- **Records**: {dataset_info['rows']:,}
- **Variables**: {dataset_info['columns']}

### Analysis Results
"""

    charts = []

    # Find potential time/date columns
    date_cols = []
    for col in df.columns:
        if df[col].dtype in ['datetime64[ns]', 'object']:
            try:
                pd.to_datetime(df[col])
                date_cols.append(col)
            except:
                continue

    # Find numeric columns for trending
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if date_cols and numeric_cols:
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col])

        for num_col in numeric_cols[:3]:  # Analyze up to 3 numeric columns
            trend_data = df.groupby(df[date_col].dt.date)[num_col].mean().reset_index()
            trend_data = trend_data.sort_values(date_col)

            # Calculate trend
            if len(trend_data) > 2:
                x = np.arange(len(trend_data))
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, trend_data[num_col])

                trend_direction = "increasing" if slope > 0 else "decreasing"
                significance = "significant" if p_value < 0.05 else "not significant"

                text += f"""
### {num_col.title()} Trend
- **Direction**: {trend_direction} ({slope:.4f} per period)
- **Significance**: {significance} (p-value: {p_value:.4f})
- **R-squared**: {r_value**2:.4f}
"""

                # Create chart data
                chart_data = []
                for _, row in trend_data.iterrows():
                    chart_data.append({
                        'date': str(row[date_col]),
                        num_col: float(row[num_col])
                    })

                charts.append({
                    'type': 'line',
                    'title': f'{num_col.title()} Trend Over Time',
                    'data': chart_data,
                    'xKey': 'date',
                    'yKeys': [num_col],
                    'colors': ['#8884d8']
                })

    else:
        text += "\n### No Clear Time Series Data Found\n"
        text += "Available columns: " + ", ".join(df.columns.tolist())
        text += "\n\nConsider uploading data with date/time columns for trend analysis."

    return {
        'text': text,
        'charts': charts,
        'steps': [
            'Data loaded successfully',
            'Time series columns identified',
            'Trend analysis performed',
            'Statistical significance calculated',
            'Visualizations generated'
        ]
    }

def analyze_correlations(df: pd.DataFrame, dataset_info: Dict) -> Dict[str, Any]:
    """Analyze correlations between variables"""
    text = f"""
## Correlation Analysis Report

### Dataset Overview
- **Records**: {dataset_info['rows']:,}
- **Variables**: {dataset_info['columns']}

### Correlation Analysis
"""

    charts = []

    # Get numeric columns
    numeric_df = df.select_dtypes(include=[np.number])

    if len(numeric_df.columns) >= 2:
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr()

        # Find strongest correlations
        correlations = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                if not np.isnan(corr_value):
                    correlations.append((col1, col2, abs(corr_value), corr_value))

        correlations.sort(key=lambda x: x[2], reverse=True)

        text += "\n### Strongest Correlations:\n"
        for col1, col2, abs_corr, corr in correlations[:5]:
            strength = "Strong" if abs_corr > 0.7 else "Moderate" if abs_corr > 0.3 else "Weak"
            direction = "positive" if corr > 0 else "negative"
            text += f"- **{col1} vs {col2}**: {strength} {direction} correlation ({corr:.3f})\n"

            # Create heatmap data (top correlations)
            if len(correlations) > 0:
                top_corr = correlations[:min(10, len(correlations))]
                
                # Add a scatter plot for the #1 correlation
                col1_top, col2_top, _, _ = top_corr[0]
                scatter_data = []
                # Sample data if too large for performance
                sample_size = min(500, len(df))
                sample_df = df[[col1_top, col2_top]].sample(sample_size).dropna()
                for _, row in sample_df.iterrows():
                    scatter_data.append({
                        'x': float(row[col1_top]),
                        'y': float(row[col2_top])
                    })
                
                charts.append({
                    'type': 'scatter',
                    'title': f'Correlation: {col1_top.title()} vs {col2_top.title()}',
                    'data': scatter_data,
                    'xKey': 'x',
                    'yKeys': ['y'],
                    'xLabel': col1_top.title(),
                    'yLabel': col2_top.title(),
                    'colors': ['#8884d8']
                })

                charts.append({
                    'type': 'bar',
                    'title': 'Top Variable Correlations',
                    'data': [
                        {'correlation': f"{col1} vs {col2}", 'strength': abs(corr)}
                        for col1, col2, _, corr in top_corr
                    ],
                    'xKey': 'correlation',
                    'yKeys': ['strength'],
                    'colors': ['#82ca9d']
                })

    else:
        text += "\n### Insufficient Numeric Data\n"
        text += f"Found {len(numeric_df.columns)} numeric columns. Need at least 2 for correlation analysis."

    return {
        'text': text,
        'charts': charts,
        'steps': [
            'Numeric variables identified',
            'Correlation matrix calculated',
            'Strong relationships identified',
            'Correlation heatmap generated'
        ]
    }

def analyze_distributions(df: pd.DataFrame, dataset_info: Dict) -> Dict[str, Any]:
    """Analyze data distributions"""
    text = f"""
## Distribution Analysis Report

### Dataset Overview
- **Records**: {dataset_info['rows']:,}
- **Variables**: {dataset_info['columns']}

### Distribution Analysis
"""

    charts = []

    # Analyze numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    for col in numeric_cols[:3]:  # Analyze up to 3 columns
        data = df[col].dropna()

        if len(data) > 0:
            mean_val = data.mean()
            median_val = data.median()
            std_val = data.std()
            min_val = data.min()
            max_val = data.max()

            # Test for normality
            try:
                _, p_value = stats.shapiro(data.sample(min(5000, len(data))))
                normality = "approximately normal" if p_value > 0.05 else "not normal"
            except:
                normality = "could not determine"

            text += f"""
### {col.title()} Distribution
- **Mean**: {mean_val:.2f}
- **Median**: {median_val:.2f}
- **Std Dev**: {std_val:.2f}
- **Range**: {min_val:.2f} to {max_val:.2f}
- **Distribution**: {normality}
- **Missing Values**: {df[col].isnull().sum()}
"""

            # Create histogram data
            hist_data = []
            try:
                counts, bins = np.histogram(data, bins=20)
                for i, count in enumerate(counts):
                    hist_data.append({
                        'bin': f"{bins[i]:.1f}-{bins[i+1]:.1f}",
                        'count': int(count)
                    })

                charts.append({
                    'type': 'bar',
                    'title': f'{col.title()} Distribution',
                    'data': hist_data,
                    'xKey': 'bin',
                    'yKeys': ['count'],
                    'colors': ['#8884d8']
                })
            except:
                pass

    if not numeric_cols:
        text += "\n### No Numeric Data Found\n"
        text += "Available columns: " + ", ".join(df.columns.tolist())

    return {
        'text': text,
        'charts': charts,
        'steps': [
            'Data distributions analyzed',
            'Statistical measures calculated',
            'Normality tests performed',
            'Distribution charts created'
        ]
    }

def analyze_summary(df: pd.DataFrame, dataset_info: Dict) -> Dict[str, Any]:
    """Provide dataset summary"""
    text = f"""
## Dataset Summary Report

### Basic Information
- **Total Records**: {dataset_info['rows']:,}
- **Total Columns**: {dataset_info['columns']}
- **Data Types**: {', '.join(set(str(dt) for dt in dataset_info['data_types'].values()))}

### Column Details
"""

    charts = []

    # Column information
    for col, dtype in dataset_info['data_types'].items():
        missing = dataset_info['missing_values'].get(col, 0)
        missing_pct = (missing / dataset_info['rows']) * 100 if dataset_info['rows'] > 0 else 0

        text += f"""
**{col}** ({dtype}):
- Missing values: {missing} ({missing_pct:.1f}%)
- Unique values: {df[col].nunique()}
"""

        # For numeric columns, add basic stats
        if dtype in ['int64', 'float64']:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                text += f"- Mean: {col_data.mean():.2f}, Std: {col_data.std():.2f}, Min: {col_data.min():.2f}, Max: {col_data.max():.2f}\n"

    # Data completeness chart
    completeness_data = []
    for col in df.columns:
        missing_pct = (df[col].isnull().sum() / len(df)) * 100
        completeness_data.append({
            'column': col,
            'completeness': 100 - missing_pct
        })

    charts.append({
        'type': 'bar',
        'title': 'Data Completeness by Column',
        'data': completeness_data,
        'xKey': 'column',
        'yKeys': ['completeness'],
        'colors': ['#8884d8']
    })

    return {
        'text': text,
        'charts': charts,
        'steps': [
            'Dataset structure analyzed',
            'Data quality assessed',
            'Summary statistics calculated',
            'Completeness report generated'
        ]
    }

def analyze_outliers(df: pd.DataFrame, dataset_info: Dict) -> Dict[str, Any]:
    """Analyze outliers in the data"""
    text = f"""
## Outlier Analysis Report

### Dataset Overview
- **Records**: {dataset_info['rows']:,}
- **Variables**: {dataset_info['columns']}

### Outlier Detection Results
"""

    charts = []

    # Analyze numeric columns for outliers
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    outlier_summary = []

    for col in numeric_cols:
        data = df[col].dropna()

        if len(data) > 10:  # Need minimum data points
            # IQR method
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = data[(data < lower_bound) | (data > upper_bound)]
            outlier_count = len(outliers)
            outlier_pct = (outlier_count / len(data)) * 100

            text += f"""
### {col.title()} Outliers
- **Total values**: {len(data)}
- **Outliers detected**: {outlier_count} ({outlier_pct:.1f}%)
- **IQR Range**: {lower_bound:.2f} to {upper_bound:.2f}
"""

            outlier_summary.append({
                'column': col,
                'outlier_count': outlier_count,
                'outlier_percentage': outlier_pct
            })

            # Create box plot data for this column
            stats_data = {
                'column': col,
                'min': float(data.min()),
                'q1': float(Q1),
                'median': float(data.median()),
                'q3': float(Q3),
                'max': float(data.max()),
                'lower_bound': float(lower_bound),
                'upper_bound': float(upper_bound)
            }
            
            charts.append({
                'type': 'boxplot',
                'title': f'{col.title()} Box Plot',
                'data': [stats_data],
                'xKey': 'column',
                'yKeys': ['min', 'q1', 'median', 'q3', 'max'],
                'colors': ['#8884d8']
            })

    if outlier_summary:
        charts.append({
            'type': 'bar',
            'title': 'Outlier Counts by Column',
            'data': outlier_summary,
            'xKey': 'column',
            'yKeys': ['outlier_count'],
            'colors': ['#ff7c7c']
        })

    if not numeric_cols:
        text += "\n### No Numeric Data for Outlier Analysis\n"
        text += "Outlier detection requires numeric columns."

    return {
        'text': text,
        'charts': charts,
        'steps': [
            'Outlier detection algorithms applied',
            'IQR method used for identification',
            'Outlier statistics calculated',
            'Visualization of outlier distribution'
        ]
    }

def analyze_general(df: pd.DataFrame, dataset_info: Dict) -> Dict[str, Any]:
    """General analysis when specific type not determined"""
    text = f"""
## General Data Analysis Report

### Dataset Overview
- **Records**: {dataset_info['rows']:,}
- **Columns**: {dataset_info['columns']}
- **Column Names**: {', '.join(dataset_info['column_names'])}

### Quick Insights
"""

    charts = []

    # Basic statistics
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    text += f"""
- **Numeric Variables**: {len(numeric_cols)}
- **Categorical Variables**: {len(categorical_cols)}
- **Data Completeness**: {((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100):.1f}%
"""

    # Top categories for categorical data
    if categorical_cols:
        text += "\n### Categorical Data Summary:\n"
        for col in categorical_cols[:3]:  # Show top 3 categorical columns
            value_counts = df[col].value_counts().head(5)
            text += f"\n**{col.title()}** (top 5):\n"
            for val, count in value_counts.items():
                pct = (count / len(df)) * 100
                text += f"- {val}: {count} ({pct:.1f}%)\n"

            # Create pie chart for top categories
            if len(value_counts) <= 10:
                pie_data = []
                for val, count in value_counts.items():
                    pie_data.append({
                        'name': str(val),
                        'value': int(count)
                    })

                charts.append({
                    'type': 'pie',
                    'title': f'{col.title()} Distribution',
                    'data': pie_data,
                    'colors': ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8']
                })

    # Basic numeric stats
    if numeric_cols:
        text += "\n### Numeric Data Summary:\n"
        for col in numeric_cols[:3]:  # Show top 3 numeric columns
            data = df[col].dropna()
            if len(data) > 0:
                text += f"""
**{col.title()}**:
- Mean: {data.mean():.2f}
- Median: {data.median():.2f}
- Std Dev: {data.std():.2f}
- Range: {data.min():.2f} to {data.max():.2f}
"""

    return {
        'text': text,
        'charts': charts,
        'steps': [
            'Dataset structure analyzed',
            'Data types identified',
            'Basic statistics calculated',
            'Key insights extracted'
        ]
    }
