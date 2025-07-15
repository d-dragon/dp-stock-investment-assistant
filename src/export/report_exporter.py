"""
Report exporter for generating various output formats.
"""

import os
import json
import csv
from typing import Dict, Any, List
from pathlib import Path
from datetime import datetime


class ReportExporter:
    """Class for exporting analysis reports in various formats."""
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize the report exporter.
        
        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def export_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export data to JSON format.
        
        Args:
            data: Data to export
            filename: Output filename (if None, auto-generated)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_report_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        
        return str(filepath)
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str = None) -> str:
        """Export data to CSV format.
        
        Args:
            data: List of dictionaries to export
            filename: Output filename (if None, auto-generated)
            
        Returns:
            Path to the exported file
        """
        if not data:
            raise ValueError("No data to export")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_data_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        
        # Get field names from first record
        fieldnames = data[0].keys()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return str(filepath)
    
    def export_to_markdown(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export data to Markdown format.
        
        Args:
            data: Data to export
            filename: Output filename (if None, auto-generated)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"stock_report_{timestamp}.md"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Stock Analysis Report\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Write data sections
            for key, value in data.items():
                f.write(f"## {key.replace('_', ' ').title()}\n\n")
                if isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        f.write(f"- **{subkey}**: {subvalue}\n")
                elif isinstance(value, list):
                    for item in value:
                        f.write(f"- {item}\n")
                else:
                    f.write(f"{value}\n")
                f.write("\n")
        
        return str(filepath)
