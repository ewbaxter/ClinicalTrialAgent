# services/clinicaltrials_api.py
"""
Real ClinicalTrials.gov API integration
API v2 Documentation: https://clinicaltrials.gov/data-api/api
"""

import requests
from typing import Dict, List, Optional
import time


class ClinicalTrialsAPI:
    """
    Client for ClinicalTrials.gov API v2
    Free, no authentication required
    """

    BASE_URL = "https://clinicaltrials.gov/api/v2"

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()

    def _find_best_location(self, locations: List[Dict], patient_location: Optional[str] = None) -> Dict:
        """
        Find the trial location closest to the patient.
        Matches by state first, then city, falling back to the first location.

        Args:
            locations: List of location dicts from the API
            patient_location: Patient's location string (e.g., "Denver, CO")

        Returns:
            The best matching location dict
        """
        if not locations:
            return {}

        if not patient_location:
            return locations[0]

        # Parse patient location into city and state
        parts = [p.strip() for p in patient_location.split(",")]
        patient_city = parts[0].lower() if parts else ""
        patient_state = parts[1].lower() if len(parts) > 1 else parts[0].lower()

        # Score each location: city+state match = 2, state match = 1, no match = 0
        best_score = 0
        best_loc = locations[0]

        for loc in locations:
            score = 0
            loc_state = loc.get("state", "").lower()
            loc_city = loc.get("city", "").lower()

            # Check state match (handle both abbreviation and full name)
            if loc_state and (patient_state in loc_state or loc_state in patient_state):
                score = 1
                # Check city match
                if loc_city and (patient_city in loc_city or loc_city in patient_city):
                    score = 2

            if score > best_score:
                best_score = score
                best_loc = loc

                # Perfect match - stop looking
                if score == 2:
                    break

        return best_loc

    def search_studies(
            self,
            condition: str,
            location: Optional[str] = None,
            recruiting_status: str = "RECRUITING",
            max_results: int = 20
    ) -> Dict:
        """
        Search for clinical trials

        Args:
            condition: Medical condition (e.g., "liver disease", "NAFLD")
            location: Location filter (e.g., "Colorado", "Denver")
            recruiting_status: RECRUITING, NOT_YET_RECRUITING, ACTIVE_NOT_RECRUITING, etc.
            max_results: Max number of results (default 20)

        Returns:
            Dict with trials_found and trials list
        """

        # Build query
        query_parts = [f"AREA[ConditionSearch]{condition}"]

        if location:
            query_parts.append(f"AREA[LocationSearch]{location}")

        # Map our status to API status
        status_map = {
            "recruiting": "RECRUITING",
            "not_yet_recruiting": "NOT_YET_RECRUITING",
            "active": "ACTIVE_NOT_RECRUITING",
            "all": None
        }
        api_status = status_map.get(recruiting_status.lower(), "RECRUITING")

        if api_status:
            query_parts.append(f"AREA[OverallStatus]{api_status}")

        query_string = " AND ".join(query_parts)

        # API parameters
        params = {
            "query.term": query_string,
            "pageSize": min(max_results, 100),  # API max is 100
            "format": "json",
            "fields": "NCTId,BriefTitle,OverallStatus,Phase,LocationCity,LocationState,LocationFacility"
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/studies",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()

            # Parse response
            studies = data.get("studies", [])

            trials = []
            for study in studies:
                protocol = study.get("protocolSection", {})
                id_module = protocol.get("identificationModule", {})
                status_module = protocol.get("statusModule", {})
                design_module = protocol.get("designModule", {})

                # Extract locations
                locations_module = protocol.get("contactsLocationsModule", {})
                locations = locations_module.get("locations", [])

                # Find the best location match for the patient
                location_str = "Location not specified"
                facility_str = ""
                if locations:
                    best_loc = self._find_best_location(locations, location)
                    city = best_loc.get("city", "")
                    state = best_loc.get("state", "")
                    facility = best_loc.get("facility", "")
                    if facility:
                        facility_str = facility
                    if city and state:
                        location_str = f"{city}, {state}"
                    elif state:
                        location_str = state

                trial = {
                    "nct_id": id_module.get("nctId", ""),
                    "title": id_module.get("briefTitle", ""),
                    "status": status_module.get("overallStatus", ""),
                    "phase": ", ".join(design_module.get("phases", ["N/A"])),
                    "location": location_str,
                    "facility": facility_str,
                    "total_sites": len(locations)
                }
                trials.append(trial)

            return {
                "trials_found": len(trials),
                "trials": trials,
                "total_available": data.get("totalCount", 0)
            }

        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "trials_found": 0,
                "trials": []
            }

    def get_study_details(self, nct_id: str) -> Dict:
        """
        Get detailed information about a specific trial

        Args:
            nct_id: NCT identifier (e.g., "NCT04234567")

        Returns:
            Dict with detailed trial information
        """

        params = {
            "query.term": f"AREA[NCTId]{nct_id}",
            "format": "json"
        }

        try:
            response = self.session.get(
                f"{self.BASE_URL}/studies",
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()

            data = response.json()
            studies = data.get("studies", [])

            if not studies:
                return {"error": f"Trial {nct_id} not found"}

            study = studies[0]
            protocol = study.get("protocolSection", {})

            # Extract key sections
            id_module = protocol.get("identificationModule", {})
            description_module = protocol.get("descriptionModule", {})
            eligibility_module = protocol.get("eligibilityModule", {})
            contacts_locations = protocol.get("contactsLocationsModule", {})

            return {
                "nct_id": nct_id,
                "title": id_module.get("briefTitle", ""),
                "description": description_module.get("briefSummary", ""),
                "detailed_description": description_module.get("detailedDescription", ""),
                "eligibility_criteria": eligibility_module.get("eligibilityCriteria", ""),
                "min_age": eligibility_module.get("minimumAge", ""),
                "max_age": eligibility_module.get("maximumAge", ""),
                "gender": eligibility_module.get("sex", "ALL"),
                "locations": contacts_locations.get("locations", []),
                "contacts": contacts_locations.get("centralContacts", [])
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}


# Quick test
if __name__ == "__main__":
    api = ClinicalTrialsAPI()

    print("Testing ClinicalTrials.gov API...")
    print("=" * 60)

    # Test search
    results = api.search_studies(
        condition="NAFLD",
        location="Colorado",
        recruiting_status="recruiting",
        max_results=5
    )

    print(f"\nFound {results['trials_found']} trials")
    print(f"Total available: {results.get('total_available', 'N/A')}")

    for trial in results['trials']:
        print(f"\n{trial['nct_id']}: {trial['title']}")
        print(f"  Status: {trial['status']}")
        print(f"  Phase: {trial['phase']}")
        print(f"  Location: {trial['location']}")