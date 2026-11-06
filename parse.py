#All the imports
import re


#Normalize the text
def normalize_text(text: str) -> str:
    """
    Normalize the buyer's RFQ message.

    1. Convert text to lowercase.
    2. Remove unnecessary spaces.
    3. Replace multiple spaces with a single space.
    """

    #Convert all characters to lowercase
    text = text.lower()

    #Remove leading and trailing whitespace
    text = text.strip()

    #Replace multiple spaces, tabs or newlines with one space
    text = re.sub(r"\s+", " ", text)

    return text


def detect_category(text: str):
    """
    Identify the packaging product category from an RFQ message.

    Returns one of the seven supported categories.
    Returns None if no category is recognized.
    """

    # Normalize the message before searching for keywords
    text = normalize_text(text)

    # Define keyword patterns for each packaging category
    category_patterns = {

        # BOPP bags have priority over generic woven bags
        "bopp_bag": [
            r"\bbopp\b",
            r"\bbopp\s*laminated\b"
        ],

        # Cement bags, AD Star bags and woven sacks
        "woven_sack": [
            r"\bcement\s*bags?\b",
            r"\bad[\s-]*star\s*bags?\b",
            r"\bwoven\s*sacks?\b",
            r"\bwoven\s*bags?\b",
            r"\bcement\s+sacks?\b",
        ],

        # Corrugated boxes and plain boxes
        "corrugated_box": [
            r"\bcorrugated\s*boxes?\b",
            r"\bcardboard\s*boxes?\b",
            r"\bplain\s*boxes?\b",
            r"\bbox\b"
        ],

        # Packaging pouches
        "pouch": [
            r"\bpouches?\b",
            r"\bstand[\s-]*up\s*pouches?\b",
            r"\bzip[\s-]*lock\s*pouches?\b"
        ],

        # Shrink film, stretch film and other films
        "film": [
            r"\bshrink\s*wrap\b",
            r"\bshrink\s*films?\b",
            r"\bstretch\s*films?\b",
            r"\bfilms?\b"
        ],

        # Mono cartons
        "mono_carton": [
            r"\bmono[\s-]*cartons?\b",
            r"\bcartons?\b"
        ],

        # Jumbo bags and bulk bags
        "fibc": [
            r"\bjumb[o]?\s*bags?\b",
            r"\bbulk\s*bags?\b",
            r"\bfibc\b"
        ]
    }

    # Check categories in priority order
    for category, patterns in category_patterns.items():

        # Check each keyword pattern
        for pattern in patterns:

            # Search for the pattern in the buyer's message
            if re.search(pattern, text):

                # Return the first matching category
                return category

    # Return None if no category is identified
    return None



def convert_to_number(value: str):
    """
    Convert Indian number formats into standard numeric values.

    Examples:
        40 hazaar  -> 40000
        1 lakh     -> 100000
        20k        -> 20000
        2.5 lac    -> 250000
        1,50,000   -> 150000
    """

    # Convert the expression to lowercase and remove extra spaces
    value = value.lower().strip()

    # Remove commas from Indian number formatting
    value = value.replace(",", "")

    # Match the numerical portion
    match = re.fullmatch(
        r"(\d+(?:\.\d+)?)\s*(k|thousand|hazaar|lakh|lac|lakhs|lacs)?",
        value
    )

    # Return None if the expression is not recognized
    if not match:
        return None

    # Extract the numerical value
    number = float(match.group(1))

    # Extract the multiplier, if present
    multiplier = match.group(2)

    # Apply the appropriate multiplier
    if multiplier == "k" or multiplier == "thousand" or multiplier == "hazaar":
        number *= 1000

    elif multiplier in ("lakh", "lac", "lakhs", "lacs"):
        number *= 100000

    # Return an integer if the result is a whole number
    if number.is_integer():
        return int(number)

    return number



def extract_quantity_and_unit(text: str):
    """
    Extract the order quantity and its corresponding unit.

    Both values are selected from the same candidate, preventing
    quantity and unit from referring to different numbers.

    Returns:
        (quantity, unit)

    Examples:
        500 BOPP bags -> (500, "pcs")
        500 kg film -> (500, "kg")
        2 MT film -> (2, "mt")
    """

    # Normalize the buyer's message
    text = normalize_text(text)

    # Pattern for numbers and Indian number multipliers
    number_pattern = re.compile(
        r"(?<![\w.])"
        r"(\d[\d,]*(?:\.\d+)?)"
        r"\s*(k(?!g)|thousand|hazaar|lakh|lac|lakhs|lacs)?",
        re.IGNORECASE
    )

    # Store all valid quantity and unit candidates
    candidates = []

    # Examine every number in the message
    for match in number_pattern.finditer(text):

        # Convert the number into its standard numeric value
        quantity = convert_to_number(match.group(0).strip())

        if quantity is None:
            continue

        # Read the text following the number
        remaining_text = text[match.end():].strip()

        # Ignore GSM and micron specifications
        if re.match(r"^(gsm|mic(?:ron)?s?)\b", remaining_text):
            continue

        # Ignore numbers preceded by GSM or micron
        before_text = text[:match.start()].strip()

        if re.search(r"(gsm|mic(?:ron)?s?)\s*$", before_text):
            continue

        # Identify an explicitly mentioned unit
        unit_match = re.match(
            r"^(pcs?|pieces?|units?|bags?|sacks?|boxes?|"
            r"pouches?|rolls?|kgs?|kilograms?|kg|mt|"
            r"metric\s+tonnes?|tonnes?|tons?|ton)\b",
            remaining_text,
            re.IGNORECASE
        )

        # Extract the unit
        unit = unit_match.group(1).lower() if unit_match else None

        # Read the text after the identified unit
        after_unit = (
            remaining_text[unit_match.end():].strip()
            if unit_match else remaining_text
        )

        # Check whether this number represents capacity
        capacity_context = re.match(
            r"^(capacity|per\s+bag|each|per\s+unit|"
            r"weight\s+of\s+each|filling\s+weight)\b",
            after_unit
        )

        # Check whether KG represents the weight of an individual bag
        per_item_weight = (
            unit in ("kg", "kgs", "kilogram", "kilograms")
            and re.match(r"^bags?\b", after_unit)
        )

        # Exclude capacity and individual bag-weight values
        if capacity_context or per_item_weight:
            continue

        # Define countable units
        count_units = (
            "pc", "pcs", "piece", "pieces", "unit", "units",
            "bag", "bags", "sack", "sacks", "box", "boxes",
            "pouch", "pouches", "roll", "rolls"
        )

        # Convert countable units into pcs
        if unit in count_units:
            standard_unit = "pcs"
            priority = 1

        # Convert kilogram units into kg
        elif unit in ("kg", "kgs", "kilogram", "kilograms"):
            standard_unit = "kg"
            priority = 2

        # Convert metric tonnes into mt
        elif unit in (
            "mt", "ton", "tons", "tonne", "tonnes",
            "metric tonne", "metric tonnes"
        ):
            standard_unit = "mt"
            priority = 2

        else:
            # Search for a countable product name after the number
            count_match = re.search(
                r"\b(bags?|sacks?|boxes?|pouches?|rolls?)\b",
                remaining_text
            )

            if count_match:
                standard_unit = "pcs"
                priority = 1
            else:
                # Use pcs as the fallback unit
                standard_unit = "pcs"
                priority = 3

        # Save quantity and unit together as one candidate
        candidates.append(
            (priority, match.start(), quantity, standard_unit)
        )

    # Return None values if no valid candidate exists
    if not candidates:
        return None, None

    # Prioritize explicit item counts, then weight quantities
    candidates.sort(key=lambda item: (item[0], item[1]))

    # Select one candidate for both quantity and unit
    selected = candidates[0]

    return selected[2], selected[3]


def extract_quantity(text: str):
    """
    Return only the quantity from the shared extraction function.
    """

    quantity, unit = extract_quantity_and_unit(text)

    return quantity


def extract_unit(text: str):
    """
    Return only the unit from the shared extraction function.
    """

    quantity, unit = extract_quantity_and_unit(text)

    return unit




def extract_gsm(text: str):
    """
    Extract GSM specification from the buyer's message.

    Examples:
        65 gsm  -> 65
        80GSM   -> 80
        100 gsm -> 100

    Returns None if GSM is not mentioned.
    """

    # Normalize the buyer's message
    text = normalize_text(text)

    # Find a number followed by the GSM keyword
    match = re.search(
        r"(?<![\w.])(\d+(?:\.\d+)?)\s*gsm\b",
        text,
        re.IGNORECASE
    )

    # Return None if GSM is not found
    if not match:
        return None

    # Convert the extracted value into an integer
    value = float(match.group(1))

    return int(value) if value.is_integer() else value



def extract_micron(text: str):
    """
    Extract micron thickness from the buyer's message.

    Examples:
        25 mic       -> 25
        50 micron    -> 50
        100 microns  -> 100

    Returns None if micron is not mentioned.
    """

    # Normalize the buyer's message
    text = normalize_text(text)

    # Find a number followed by mic, micron or microns
    match = re.search(
        r"(?<![\w.])(\d+(?:\.\d+)?)\s*mic(?:ron)?s?\b",
        text,
        re.IGNORECASE
    )

    # Return None if micron is not found
    if not match:
        return None

    # Convert the extracted value into an integer
    value = float(match.group(1))

    return int(value) if value.is_integer() else value



def extract_location(text: str):
    """
    Extract the delivery or destination location from an RFQ.

    Uses an offline geographical database and contextual patterns.
    Returns None if no location is identified.
    """

    # Normalize the buyer's message
    text = normalize_text(text)
    # Handle important Indian city names and their aliases

    # Handle important Indian city names and their aliases
    location_aliases = {
        # Maharashtra
        "aurangabad": "Chhatrapati Sambhaji Nagar",
        "sambhajinagar": "Chhatrapati Sambhaji Nagar",
        "chhatrapati sambhajinagar": "Chhatrapati Sambhaji Nagar",
        "chhatrapati sambhaji nagar": "Chhatrapati Sambhaji Nagar",
        "rajkot": "Rajkot",

        # Major Indian cities
        "bombay": "Mumbai",
        "bangalore": "Bengaluru",
        "madras": "Chennai",
        "calcutta": "Kolkata",
        "allahabad": "Prayagraj",
        "gurgaon": "Gurugram",
        "baroda": "Vadodara",
        "trivandrum": "Thiruvananthapuram",
        "cochin": "Kochi",
        "mysore": "Mysuru",
        "mangalore": "Mangaluru",
        "belgaum": "Belagavi",
        "pondicherry": "Puducherry",
        "trichy": "Tiruchirappalli",
        "panjim": "Panaji",
        "vizag": "Visakhapatnam",
        "new delhi": "New Delhi",
    }

    # Check the longest aliases first
    for alias, official_name in sorted(
        location_aliases.items(),
        key=lambda item: len(item[0]),
        reverse=True
    ):
        if re.search(r"\b" + re.escape(alias) + r"\b", text):
            return official_name


    # Load the offline geographical database
    import geonamescache

    gc = geonamescache.GeonamesCache()

    # Collect Indian city names
    cities = gc.get_cities()

    indian_cities = {
        city["name"].lower(): city["name"]
        for city in cities.values()
        if city.get("countrycode") == "IN"
    }

    # Indian states and union territories
    indian_states = [
        "andhra pradesh", "arunachal pradesh",
        "assam", "bihar", "chhattisgarh",
        "goa", "gujarat", "haryana",
        "himachal pradesh", "jharkhand",
        "karnataka", "kerala", "madhya pradesh",
        "maharashtra", "manipur", "meghalaya",
        "mizoram", "nagaland", "odisha",
        "punjab", "rajasthan", "sikkim",
        "tamil nadu", "telangana", "tripura",
        "uttar pradesh", "uttarakhand",
        "west bengal",
        "andaman and nicobar islands",
        "chandigarh", "delhi", "jammu and kashmir",
        "ladakh", "lakshadweep",
        "puducherry"
    ]

    # Search for explicitly labelled destinations first
    location_patterns = [
        r"(?:deliver(?:y)?\s+to|ship(?:ping)?\s+to|"
        r"send\s+to|destination\s*[:=]|location\s*[:=]|"
        r"delivery\s+location\s*[:=]|at)\s+"
        r"([a-z][a-z\s.-]*?)"
        r"(?=\s*(?:,|;|$|for\b|with\b|and\b))"
    ]

    for pattern in location_patterns:
        match = re.search(pattern, text)

        if match:
            candidate = match.group(1).strip()

            # Match the extracted phrase against known locations
            if candidate in indian_cities:
                return indian_cities[candidate]

            if candidate in indian_states:
                return candidate.title()

    # Search for Indian states in the message
    for state in sorted(indian_states, key=len, reverse=True):
        if re.search(r"\b" + re.escape(state) + r"\b", text):
            return state.title()

    # Search for Indian cities in the message
    for city in sorted(indian_cities, key=len, reverse=True):
        if re.search(r"\b" + re.escape(city) + r"\b", text):
            return indian_cities[city]

    # No location was recognized
    return None



def parse_rfq(text: str) -> dict:
    """
    Parse a buyer's RFQ message and extract all required fields.

    Returns a dictionary containing exactly six fields:
    category, quantity, unit, gsm, micron and location.
    """

    # Extract the product category
    category = detect_category(text)

    # Extract quantity and its corresponding unit together
    quantity, unit = extract_quantity_and_unit(text)

    # Extract GSM specification
    gsm = extract_gsm(text)

    # Extract micron specification
    micron = extract_micron(text)

    # Extract delivery location
    location = extract_location(text)

    # Return all extracted information
    return {
        "category": category,
        "quantity": quantity,
        "unit": unit,
        "gsm": gsm,
        "micron": micron,
        "location": location
    }
















































if __name__ == "__main__":

    # Test messages covering different RFQ scenarios
    test_messages = [

        # 1. Category and product recognition
        "Need 500 BOPP bags",
        "1000 cement bags required",
        "Need 2000 corrugated boxes",
        "5000 stand-up pouches required",
        "Need shrink wrap film",
        "1000 mono cartons",
        "Need 500 jumbo bags",

        # 2. Quantity and Indian number formats
        "BOPP bags chahiye 40 hazaar",
        "Need 1 lakh cement bags",
        "Order 2.5 lac corrugated boxes",
        "Need 20k pouches",
        "150000 woven sacks required",

        # 3. Quantity and unit recognition
        "Need 500 BOPP bags",
        "Need 500 kg shrink wrap",
        "Require 2 MT packaging film",
        "Need 1000kg stretch film",
        "Need 500 pcs mono cartons",

        # 4. GSM and micron specifications
        "BOPP bags 65 gsm",
        "Need 80GSM cement bags",
        "Need 25 mic shrink wrap",
        "Need 50 micron stretch film",
        "Need 65 gsm and 25 micron BOPP bags",

        # 5. Capacity and individual weight cases
        "Jumbo bag 1000 kg capacity, 500 pcs",
        "1000 kg capacity jumbo bags, 500pcs",
        "25 kg bags, order 2000 pcs",
        "500 bags, 1000 kg capacity",

        # 6. Location extraction
        "Need 500 bags, deliver to Nagpur",
        "Ship 500 boxes to Hyderabad",
        "Need 2000 pouches in Maharashtra",
        "Deliver to Chhatrapati Sambhaji Nagar",
        "Required in Uttar Pradesh, deliver to Lucknow",
        "Delivery: New Delhi",

        # 7. Alternative city names
        "Deliver to Bombay",
        "Ship to Bangalore",
        "Deliver to Baroda",
        "Required in Allahabad",
        "Ship to Vizag",
        "Deliver to Aurangabad",

        # 8. Missing information
        "Need packaging material urgently",
        "Looking for a quotation for bags",
    ]

    # Process each RFQ message
    for message in test_messages:

        # Extract quantity and its corresponding unit
        quantity, unit = extract_quantity_and_unit(message)

        # Extract the remaining RFQ fields
        category = detect_category(message)
        gsm = extract_gsm(message)
        micron = extract_micron(message)
        location = extract_location(message)

        # Display the extracted information
        print("Message:", message)
        print("Category:", category)
        print("Quantity:", quantity)
        print("Unit:", unit)
        print("GSM:", gsm)
        print("Micron:", micron)
        print("Location:", location)

        print("-" * 70)

print("\nFINAL PARSER TEST")
print("=" * 70)

rfq = "bopp bags chahiye 40 hazaar, 65 gsm, Nagpur"
rfq = "We are looking to procure fifty thousand laminated polypropylene sacks for delivery to Nagpur."

result = parse_rfq(rfq)

print("Input:", rfq)
print("Output:", result)
print("-" * 70)










