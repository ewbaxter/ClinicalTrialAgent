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

                # Get first location for simplicity
                location_str = "Location not specified"
                if locations:
                    loc = locations[0]
                    city = loc.get("city", "")
                    state = loc.get("state", "")
                    if city and state:
                        location_str = f"{city}, {state}"
                    elif state:
                        location_str = state

                trial = {
                    "nct_id": id_module.get("nctId", ""),
                    "title": id_module.get("briefTitle", ""),
                    "status": status_module.get("overallStatus", ""),
                    "phase": ", ".join(design_module.get("phases", ["N/A"])),
                    "location": location_str
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