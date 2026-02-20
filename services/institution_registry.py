# services/institution_registry.py
"""
Institutional Research Registry Service

Provides lookup of research institutions with clinical trial programs,
organized by location and specialty. Complements ClinicalTrials.gov data
by surfacing local and national research resources.
"""

import json
import os
from typing import Dict, List, Optional


class InstitutionRegistry:
    """
    Registry of research institutions with clinical trial programs.
    Data sourced from curated JSON file.
    """

    # US state abbreviation to full name mapping (for flexible matching)
    STATE_ABBREVIATIONS = {
        "AL": "alabama", "AK": "alaska", "AZ": "arizona", "AR": "arkansas",
        "CA": "california", "CO": "colorado", "CT": "connecticut", "DE": "delaware",
        "FL": "florida", "GA": "georgia", "HI": "hawaii", "ID": "idaho",
        "IL": "illinois", "IN": "indiana", "IA": "iowa", "KS": "kansas",
        "KY": "kentucky", "LA": "louisiana", "ME": "maine", "MD": "maryland",
        "MA": "massachusetts", "MI": "michigan", "MN": "minnesota", "MS": "mississippi",
        "MO": "missouri", "MT": "montana", "NE": "nebraska", "NV": "nevada",
        "NH": "new hampshire", "NJ": "new jersey", "NM": "new mexico", "NY": "new york",
        "NC": "north carolina", "ND": "north dakota", "OH": "ohio", "OK": "oklahoma",
        "OR": "oregon", "PA": "pennsylvania", "RI": "rhode island", "SC": "south carolina",
        "SD": "south dakota", "TN": "tennessee", "TX": "texas", "UT": "utah",
        "VT": "vermont", "VA": "virginia", "WA": "washington", "WV": "west virginia",
        "WI": "wisconsin", "WY": "wyoming", "DC": "district of columbia"
    }

    def __init__(self):
        self.institutions = []
        self._load_registry()

    def _load_registry(self):
        """Load institution data from JSON file"""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "data",
            "institution_registry.json"
        )

        try:
            with open(data_path, "r") as f:
                data = json.load(f)
                self.institutions = data.get("institutions", [])
        except FileNotFoundError:
            print(f"Warning: Institution registry not found at {data_path}")
            self.institutions = []
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in institution registry at {data_path}")
            self.institutions = []

    def _normalize_state(self, state_str: str) -> str:
        """Normalize state input to lowercase full name for matching"""
        state_str = state_str.strip().upper()
        if state_str in self.STATE_ABBREVIATIONS:
            return self.STATE_ABBREVIATIONS[state_str]
        return state_str.lower()

    def _parse_location(self, location: str) -> tuple:
        """Parse 'City, State' into (city, state) tuple"""
        parts = [p.strip() for p in location.split(",")]
        city = parts[0].lower() if parts else ""
        state = self._normalize_state(parts[1]) if len(parts) > 1 else self._normalize_state(parts[0])
        return city, state

    def search_by_location(
            self,
            location: str,
            specialties: Optional[List[str]] = None,
            include_national: bool = True,
            max_results: int = 10
    ) -> Dict:
        """
        Find research institutions near a patient's location.

        Args:
            location: Patient location (e.g., "Denver, CO")
            specialties: Optional list of medical specialties to filter by
            include_national: Whether to include top national institutions
            max_results: Maximum results to return

        Returns:
            Dict with local_institutions, national_institutions, and total_found
        """
        city, state = self._parse_location(location)

        local = []
        national = []

        for inst in self.institutions:
            inst_state = self._normalize_state(inst.get("state", ""))

            # Check specialty match if filter provided
            specialty_match = True
            if specialties:
                inst_specialties = [s.lower() for s in inst.get("specialties", [])]
                specialty_match = any(
                    any(spec.lower() in inst_spec for inst_spec in inst_specialties)
                    for spec in specialties
                )

            if not specialty_match:
                continue

            # Categorize as local or national
            if inst_state == state:
                local.append(self._format_institution(inst, is_local=True))
            elif include_national:
                national.append(self._format_institution(inst, is_local=False))

        # Sort local by type priority (academic > health_system > specialty > others)
        type_priority = {
            "academic_medical_center": 0,
            "health_system": 1,
            "cancer_center": 2,
            "specialty_center": 3,
            "pediatric_center": 4,
            "government_research": 5,
            "va_medical_center": 6,
            "research_network": 7,
            "safety_net_hospital": 8
        }
        local.sort(key=lambda x: type_priority.get(x.get("type", ""), 99))

        # Limit national results
        national = national[:max(0, max_results - len(local))]

        return {
            "patient_location": location,
            "local_institutions": local,
            "national_institutions": national,
            "local_count": len(local),
            "national_count": len(national),
            "total_found": len(local) + len(national),
            "note": "These institutions have active clinical trial programs. "
                    "Visit their trial finder pages for trials that may not yet appear on ClinicalTrials.gov."
        }

    def _format_institution(self, inst: Dict, is_local: bool) -> Dict:
        """Format institution for output"""
        return {
            "name": inst.get("name", ""),
            "short_name": inst.get("short_name", ""),
            "type": inst.get("type", ""),
            "trial_finder_url": inst.get("trial_finder_url", ""),
            "website": inst.get("website", ""),
            "city": inst.get("city", ""),
            "state": inst.get("state", ""),
            "specialties": inst.get("specialties", []),
            "notes": inst.get("notes", ""),
            "is_local": is_local
        }


# Quick test
if __name__ == "__main__":
    registry = InstitutionRegistry()

    print("Testing Institution Registry")
    print("=" * 60)

    # Test Denver search
    results = registry.search_by_location("Denver, CO")
    print(f"\nSearch: Denver, CO")
    print(f"Local institutions: {results['local_count']}")
    for inst in results['local_institutions']:
        print(f"  - {inst['name']} ({inst['type']})")
        print(f"    Trial finder: {inst['trial_finder_url']}")

    print(f"\nNational institutions: {results['national_count']}")
    for inst in results['national_institutions']:
        print(f"  - {inst['name']} ({inst['city']}, {inst['state']})")

    # Test with specialty filter
    print("\n" + "=" * 60)
    results = registry.search_by_location("Denver, CO", specialties=["pulmonary", "respiratory"])
    print(f"\nSearch: Denver, CO (pulmonary/respiratory)")
    print(f"Local: {results['local_count']}")
    for inst in results['local_institutions']:
        print(f"  - {inst['name']}")
