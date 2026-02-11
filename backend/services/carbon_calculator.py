"""
Carbon emission calculation engine
"""
import json
import os
from typing import Dict, Optional, Tuple
from pathlib import Path


class CarbonCalculator:
    """Calculate carbon emissions based on consumption data and emission factors"""

    def __init__(self, emission_factors_path: Optional[str] = None):
        if emission_factors_path is None:
            # Default to data directory
            base_path = Path(__file__).parent.parent.parent / "data" / "emission-factors"
            emission_factors_path = str(base_path)

        self.emission_factors_path = emission_factors_path
        self.factors = self._load_emission_factors()

    def _load_emission_factors(self) -> Dict:
        """Load all emission factor databases"""
        factors = {}
        factor_files = ["electricity.json", "fuel.json", "water.json", "waste.json"]

        for file_name in factor_files:
            file_path = os.path.join(self.emission_factors_path, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    category = file_name.replace(".json", "")
                    factors[category] = json.load(f)

        return factors

    def get_electricity_factor(self, country: str, region: Optional[str] = None) -> Tuple[float, str]:
        """
        Get emission factor for electricity

        Returns:
            Tuple of (emission_factor, source_description)
        """
        electricity_factors = self.factors.get("electricity", {}).get("factors", {})

        # Try to get country-specific factor
        if country in electricity_factors.get("countries", {}):
            country_data = electricity_factors["countries"][country]

            # Try to get region-specific factor
            if region and "regions" in country_data:
                if region in country_data["regions"]:
                    factor = country_data["regions"][region]
                    source = f"{country} - {region} grid"
                    return factor, source

            # Fall back to national grid
            if "national_grid" in country_data:
                factor = country_data["national_grid"]
                source = f"{country} national grid"
                return factor, source

        # Fall back to global average
        factor = electricity_factors.get("global_average", 0.475)
        source = "Global average"
        return factor, source

    def get_fuel_factor(self, fuel_type: str) -> Tuple[float, str, str]:
        """
        Get emission factor for fuel

        Returns:
            Tuple of (emission_factor, unit, source_description)
        """
        fuel_factors = self.factors.get("fuel", {}).get("factors", {})

        fuel_type_normalized = fuel_type.lower().replace(" ", "_")

        if fuel_type_normalized in fuel_factors:
            fuel_data = fuel_factors[fuel_type_normalized]
            factor = fuel_data.get("value", 0)
            unit = fuel_data.get("unit", "kg CO2e per unit")
            source = f"EPA/IPCC - {fuel_type}"
            return factor, unit, source

        # Default factor for unknown fuel types
        return 2.5, "kg CO2e per liter", "Default estimate"

    def get_water_factor(self, water_type: str = "water_supply") -> Tuple[float, str]:
        """
        Get emission factor for water

        Returns:
            Tuple of (emission_factor, source_description)
        """
        water_factors = self.factors.get("water", {}).get("factors", {})

        if water_type in water_factors:
            water_data = water_factors[water_type]
            factor = water_data.get("value", 0)
            description = water_data.get("description", water_type)
            return factor, description

        # Default to water supply
        default_data = water_factors.get("water_supply", {})
        factor = default_data.get("value", 0.344)
        description = default_data.get("description", "Water supply default")
        return factor, description

    def get_waste_factor(self, waste_type: str, disposal_method: str) -> Tuple[float, str]:
        """
        Get emission factor for waste

        Returns:
            Tuple of (emission_factor, source_description)
        """
        waste_factors = self.factors.get("waste", {}).get("factors", {}).get("disposal_methods", {})

        disposal_method_normalized = disposal_method.lower().replace(" ", "_")
        waste_type_normalized = waste_type.lower().replace(" ", "_")

        if disposal_method_normalized in waste_factors:
            method_data = waste_factors[disposal_method_normalized]

            if waste_type_normalized in method_data:
                factor = method_data[waste_type_normalized]
                source = f"{disposal_method} - {waste_type}"
                return factor, source

        # Default to mixed waste in landfill
        factor = waste_factors.get("landfill", {}).get("mixed_waste", 583)
        source = "Landfill - mixed waste (default)"
        return factor, source

    def calculate_electricity_emissions(
        self,
        consumption_kwh: float,
        country: str,
        region: Optional[str] = None
    ) -> Dict:
        """
        Calculate CO2 emissions from electricity consumption

        Args:
            consumption_kwh: Electricity consumption in kWh
            country: Country name
            region: Optional region within country

        Returns:
            Dict with calculation results
        """
        emission_factor, source = self.get_electricity_factor(country, region)
        total_co2e = consumption_kwh * emission_factor

        return {
            "consumption_amount": consumption_kwh,
            "consumption_unit": "kWh",
            "emission_factor": emission_factor,
            "emission_factor_unit": "kg CO2e per kWh",
            "emission_factor_source": source,
            "total_co2e": total_co2e,
            "total_co2e_tonnes": total_co2e / 1000,
            "category": "Scope 2",
            "source_type": "electricity"
        }

    def calculate_fuel_emissions(
        self,
        consumption_amount: float,
        fuel_type: str,
        unit: Optional[str] = None
    ) -> Dict:
        """
        Calculate CO2 emissions from fuel consumption

        Args:
            consumption_amount: Amount of fuel consumed
            fuel_type: Type of fuel (e.g., "diesel", "natural_gas")
            unit: Optional unit override

        Returns:
            Dict with calculation results
        """
        emission_factor, factor_unit, source = self.get_fuel_factor(fuel_type)
        total_co2e = consumption_amount * emission_factor

        return {
            "consumption_amount": consumption_amount,
            "consumption_unit": unit or factor_unit,
            "emission_factor": emission_factor,
            "emission_factor_unit": factor_unit,
            "emission_factor_source": source,
            "total_co2e": total_co2e,
            "total_co2e_tonnes": total_co2e / 1000,
            "category": "Scope 1",
            "source_type": "fuel"
        }

    def calculate_water_emissions(
        self,
        consumption_m3: float,
        water_type: str = "water_supply"
    ) -> Dict:
        """
        Calculate CO2 emissions from water consumption

        Args:
            consumption_m3: Water consumption in cubic meters
            water_type: Type of water service

        Returns:
            Dict with calculation results
        """
        emission_factor, source = self.get_water_factor(water_type)
        total_co2e = consumption_m3 * emission_factor

        return {
            "consumption_amount": consumption_m3,
            "consumption_unit": "m³",
            "emission_factor": emission_factor,
            "emission_factor_unit": "kg CO2e per m³",
            "emission_factor_source": source,
            "total_co2e": total_co2e,
            "total_co2e_tonnes": total_co2e / 1000,
            "category": "Scope 3",
            "source_type": "water"
        }

    def calculate_waste_emissions(
        self,
        waste_tonnes: float,
        waste_type: str,
        disposal_method: str
    ) -> Dict:
        """
        Calculate CO2 emissions from waste

        Args:
            waste_tonnes: Amount of waste in tonnes
            waste_type: Type of waste
            disposal_method: How waste is disposed

        Returns:
            Dict with calculation results
        """
        emission_factor, source = self.get_waste_factor(waste_type, disposal_method)
        total_co2e = waste_tonnes * emission_factor

        return {
            "consumption_amount": waste_tonnes,
            "consumption_unit": "tonnes",
            "emission_factor": emission_factor,
            "emission_factor_unit": "kg CO2e per tonne",
            "emission_factor_source": source,
            "total_co2e": total_co2e,
            "total_co2e_tonnes": total_co2e / 1000,
            "category": "Scope 3",
            "source_type": "waste"
        }

    def calculate_emissions(
        self,
        bill_type: str,
        consumption_amount: float,
        consumption_unit: str,
        country: str = "global",
        region: Optional[str] = None,
        fuel_type: Optional[str] = None,
        water_type: Optional[str] = "water_supply",
        waste_type: Optional[str] = "mixed_waste",
        disposal_method: Optional[str] = "landfill"
    ) -> Dict:
        """
        Generic emission calculation based on bill type

        Args:
            bill_type: Type of bill (electricity, fuel, water, waste)
            consumption_amount: Amount consumed
            consumption_unit: Unit of consumption
            country: Country for location-specific factors
            region: Optional region
            fuel_type: Type of fuel (if applicable)
            water_type: Type of water service (if applicable)
            waste_type: Type of waste (if applicable)
            disposal_method: Waste disposal method (if applicable)

        Returns:
            Dict with calculation results
        """
        bill_type_lower = bill_type.lower()

        if bill_type_lower == "electricity":
            # Convert to kWh if needed
            if consumption_unit.lower() in ["kwh", "kilowatt-hour", "kilowatt hour"]:
                consumption_kwh = consumption_amount
            else:
                # Assume it's already in kWh
                consumption_kwh = consumption_amount

            return self.calculate_electricity_emissions(consumption_kwh, country, region)

        elif bill_type_lower in ["fuel", "gas"]:
            if not fuel_type:
                fuel_type = "natural_gas" if bill_type_lower == "gas" else "diesel"

            return self.calculate_fuel_emissions(consumption_amount, fuel_type, consumption_unit)

        elif bill_type_lower == "water":
            # Convert to m³ if needed
            if consumption_unit.lower() in ["m3", "m³", "cubic meter", "cubic metre"]:
                consumption_m3 = consumption_amount
            elif consumption_unit.lower() in ["l", "liter", "litre"]:
                consumption_m3 = consumption_amount / 1000
            else:
                consumption_m3 = consumption_amount

            return self.calculate_water_emissions(consumption_m3, water_type)

        elif bill_type_lower == "waste":
            # Convert to tonnes if needed
            if consumption_unit.lower() in ["kg", "kilogram"]:
                waste_tonnes = consumption_amount / 1000
            elif consumption_unit.lower() in ["t", "tonne", "ton"]:
                waste_tonnes = consumption_amount
            else:
                waste_tonnes = consumption_amount

            return self.calculate_waste_emissions(waste_tonnes, waste_type, disposal_method)

        else:
            raise ValueError(f"Unsupported bill type: {bill_type}")


# Singleton instance
_calculator = None


def get_calculator() -> CarbonCalculator:
    """Get singleton instance of carbon calculator"""
    global _calculator
    if _calculator is None:
        _calculator = CarbonCalculator()
    return _calculator
