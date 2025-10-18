"""
Targeted Maveric Documentation Ingestion
Based on actual lf-connectivity/maveric repository structure
"""

import os
import requests
from pathlib import Path
from typing import List, Dict, Any
import json
from datetime import datetime


class MavericDocIngestion:
    """
    Ingests full Maveric RADP documentation from GitHub
    """
    
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
    REPO_OWNER = "lf-connectivity"
    REPO_NAME = "maveric"
    BRANCH = "main"
    
    # Actual documentation files from Maveric repo
    TARGET_DOCS = [
        # Core documentation
        "README.md",
        "README-DEV.md",
        "README-NOTEBOOKS.md",
        "LICENSE",
        "CONTRIBUTING.md",
        
        # Example data and apps
        "apps/example/ue_training_data.csv",
        "apps/example/topology.csv",
        "apps/example/ue_data.csv",
        "apps/example/example_app.py",
        "apps/coverage_capacity_optimization/cco_example_app.py",
        
        # Docker and config files
        ".env-prod",
        "dc.yml",
        "dc-prod.yml",
        "dc-cuda.yml",
        
        # Requirements files
        "radp/client/requirements.txt",
        "apps/requirements.txt",
    ]
    
    def __init__(self, output_dir: str = "examples/maveric/docs"):
        """Initialize document ingestion"""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.headers = {}
        
        if self.github_token:
            self.headers["Authorization"] = f"token {self.github_token}"
            print("✓ Using GitHub token for API requests")
        else:
            print("⚠ No GitHub token - using public access")
    
    def fetch_file_content(self, file_path: str) -> tuple:
        """
        Fetch file content from GitHub
        
        Returns:
            Tuple of (content, success, status_code)
        """
        url = f"{self.GITHUB_RAW_BASE}/{self.REPO_OWNER}/{self.REPO_NAME}/{self.BRANCH}/{file_path}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.text, True, 200
            else:
                return "", False, response.status_code
                
        except requests.RequestException as e:
            return "", False, 0
    
    def ingest_documentation(self) -> Dict[str, Any]:
        """Ingest Maveric documentation"""
        
        print("\n" + "="*70)
        print("MAVERIC RADP TARGETED DOCUMENTATION INGESTION")
        print("="*70)
        print(f"Repository: {self.REPO_OWNER}/{self.REPO_NAME}")
        print(f"Branch: {self.BRANCH}")
        print("-"*70)
        
        stats = {
            "files_attempted": len(self.TARGET_DOCS),
            "files_downloaded": 0,
            "files_not_found": 0,
            "files_failed": 0,
            "total_size": 0,
            "file_list": []
        }
        
        print(f"\n📥 Fetching {len(self.TARGET_DOCS)} documentation files...\n")
        
        for idx, file_path in enumerate(self.TARGET_DOCS, 1):
            print(f"[{idx:2d}/{len(self.TARGET_DOCS)}] {file_path:<50}", end=" ")
            
            content, success, status_code = self.fetch_file_content(file_path)
            
            if success and content:
                # Create sanitized filename
                safe_filename = file_path.replace("/", "_").replace("\\", "_")
                self._save_document(safe_filename, content)
                
                stats["files_downloaded"] += 1
                stats["total_size"] += len(content)
                stats["file_list"].append({
                    "original_path": file_path,
                    "saved_as": safe_filename,
                    "size": len(content)
                })
                
                size_kb = len(content) / 1024
                print(f"✓ {size_kb:6.1f} KB")
            
            elif status_code == 404:
                stats["files_not_found"] += 1
                print(f"⊘ Not found")
            
            elif status_code == 403:
                stats["files_failed"] += 1
                print(f"✗ Rate limited")
            
            else:
                stats["files_failed"] += 1
                print(f"✗ Error ({status_code})")
        
        # Save metadata
        self._save_metadata(stats)
        
        print("\n" + "="*70)
        print("INGESTION SUMMARY")
        print("="*70)
        print(f"  Files attempted:  {stats['files_attempted']}")
        print(f"  ✓ Downloaded:     {stats['files_downloaded']}")
        print(f"  ⊘ Not found:      {stats['files_not_found']}")
        print(f"  ✗ Failed:         {stats['files_failed']}")
        print(f"  Total size:       {stats['total_size']:,} bytes ({stats['total_size']/1024:.1f} KB)")
        print(f"  Output dir:       {self.output_dir.absolute()}")
        print("="*70 + "\n")
        
        return stats
    
    def _save_document(self, filename: str, content: str):
        """Save document to output directory"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _save_metadata(self, stats: Dict[str, Any]):
        """Save ingestion metadata"""
        metadata = {
            "repository": f"{self.REPO_OWNER}/{self.REPO_NAME}",
            "branch": self.BRANCH,
            "ingestion_method": "targeted_fetch",
            "statistics": {
                "files_attempted": stats["files_attempted"],
                "files_downloaded": stats["files_downloaded"],
                "files_not_found": stats["files_not_found"],
                "files_failed": stats["files_failed"],
                "total_size": stats["total_size"]
            },
            "file_list": stats["file_list"],
            "timestamp": datetime.now().isoformat(),
            "version": "2.0"
        }
        
        metadata_path = self.output_dir / "ingestion_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"✓ Metadata saved: {metadata_path.name}")


def main():
    """Main execution"""
    print("\n🚀 Maveric RADP Documentation Ingestion")
    print("   Targeting actual repository files\n")
    
    ingestion = MavericDocIngestion()
    stats = ingestion.ingest_documentation()
    
    if stats["files_downloaded"] > 0:
        print("\n✅ SUCCESS! Documentation ready for RAG engine.")
    else:
        print("\n❌ FAILED! No files downloaded.")


if __name__ == "__main__":
    main()