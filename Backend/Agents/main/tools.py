import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from pathlib import Path
from Backend.data_analyzer import analyze_dataset, load_dataset
from Backend.agent_service import _profile_dataset, _clean_dataset, _build_overview_charts, _build_narrative, _answer_direct_question

UPLOAD_DIR = Path("Backend/uploads")

def inspect_data(filename: str) -> Dict[str, Any]:
    """
    Profiles the dataset to understand its structure, types, and missing values.
    
    Args:
        filename: The name of the dataset file in the uploads directory.
        
    Returns:
        A dictionary containing the dataset profile.
    """
    df = load_dataset(filename)
    return _profile_dataset(df)

def clean_data(filename: str) -> Dict[str, Any]:
    """
    Cleans the dataset by removing duplicates and standardizing placeholder values.
    Saves the cleaned data to a new file and returns cleaning notes.
    
    Args:
        filename: The name of the dataset file in the uploads directory.
        
    Returns:
        A dictionary with cleaning notes and the name of the cleaned file.
    """
    df = load_dataset(filename)
    cleaned_df, notes = _clean_dataset(df)
    
    cleaned_filename = f"cleaned_{filename}"
    cleaned_path = UPLOAD_DIR / cleaned_filename
    
    if cleaned_filename.endswith('.csv'):
        cleaned_df.to_csv(cleaned_path, index=False)
    elif cleaned_filename.endswith(('.xlsx', '.xls')):
        cleaned_df.to_excel(cleaned_path, index=False)
    else:
        cleaned_df.to_json(cleaned_path)
        
    return {
        "notes": notes,
        "cleaned_filename": cleaned_filename,
        "original_rows": len(df),
        "cleaned_rows": len(cleaned_df)
    }

def analyze_data(filename: str, query: str) -> Dict[str, Any]:
    """
    Performs exploratory data analysis (EDA) and statistical analysis based on a query.
    
    Args:
        filename: The name of the dataset file.
        query: The user's analysis question.
        
    Returns:
        A dictionary with analysis text and chart configurations.
    """
    df = load_dataset(filename)
    return analyze_dataset(df, query)

def generate_final_report(filename: str, query: str, profile: Dict, cleaning_notes: List[str], analysis: Dict) -> str:
    """
    Generates a comprehensive human-readable report.
    
    Args:
        filename: Dataset name.
        query: User question.
        profile: Dataset profile.
        cleaning_notes: List of cleaning actions taken.
        analysis: Analysis results including text and charts.
        
    Returns:
        A markdown-formatted report string.
    """
    df = load_dataset(filename)
    direct_answer = _answer_direct_question(df, query)
    return _build_narrative(query, filename, profile, cleaning_notes, analysis, direct_answer)

def get_overview_charts(filename: str, profile: Dict) -> List[Dict[str, Any]]:
    """
    Generates standard overview charts for a dataset.
    
    Args:
        filename: Dataset name.
        profile: Dataset profile.
        
    Returns:
        A list of chart configurations.
    """
    df = load_dataset(filename)
    return _build_overview_charts(df, profile)

def apply_action(filename: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies a specific data transformation or cleaning action to the dataset.
    
    Args:
        filename: The name of the dataset file.
        action: The type of action (e.g., 'fill_na', 'drop_na', 'drop_columns', 'rename_columns').
        parameters: A dictionary of parameters for the action (e.g., {'column': 'age', 'value': 0}).
        
    Returns:
        A dictionary with the result of the action and the new filename.
    """
    df = load_dataset(filename)
    original_shape = df.shape
    
    if action == 'fill_na':
        column = parameters.get('column')
        method = parameters.get('method', 'constant')
        value = parameters.get('value')
        if method == 'mean':
            df[column] = df[column].fillna(df[column].mean())
        elif method == 'median':
            df[column] = df[column].fillna(df[column].median())
        elif method == 'mode':
            df[column] = df[column].fillna(df[column].mode()[0])
        else:
            df[column] = df[column].fillna(value)
            
    elif action == 'drop_na':
        column = parameters.get('column')
        if column:
            df = df.dropna(subset=[column])
        else:
            df = df.dropna()
            
    elif action == 'drop_columns':
        columns = parameters.get('columns', [])
        df = df.drop(columns=columns)
        
    elif action == 'rename_columns':
        mapping = parameters.get('mapping', {})
        df = df.rename(columns=mapping)
        
    # Save the modified dataset
    modified_filename = f"mod_{filename}"
    modified_path = UPLOAD_DIR / modified_filename
    df.to_csv(modified_path, index=False)
    
    return {
        "status": "success",
        "action_taken": action,
        "original_shape": original_shape,
        "new_shape": df.shape,
        "modified_filename": modified_filename,
        "message": f"Successfully applied {action} to {filename}."
    }
