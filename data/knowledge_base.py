"""
Small curated knowledge base standing in for a production content database.
Destinations are grouped into cost tiers matching model/train_model.py so the
ML cost prediction and the rule-based itinerary generator agree with each other.
"""

DESTINATIONS = {
    "goa":        {"tier": "beach",    "label": "Goa"},
    "manali":     {"tier": "hill",     "label": "Manali"},
    "jaipur":     {"tier": "tier2",    "label": "Jaipur"},
    "mumbai":     {"tier": "metro",    "label": "Mumbai"},
    "agra":       {"tier": "heritage", "label": "Agra"},
    "munnar":     {"tier": "hill",     "label": "Munnar"},
    "pondicherry":{"tier": "beach",    "label": "Pondicherry"},
    "varanasi":   {"tier": "heritage", "label": "Varanasi"},
    "udaipur":    {"tier": "tier2",    "label": "Udaipur"},
    "darjeeling": {"tier": "hill",     "label": "Darjeeling"},
}

# Budget split templates (% of total budget) by travel style
BUDGET_SPLIT = {
    "relaxed": {"hotel": 0.38, "food": 0.22, "transport": 0.16, "activities": 0.16, "buffer": 0.08},
    "active":  {"hotel": 0.28, "food": 0.20, "transport": 0.22, "activities": 0.24, "buffer": 0.06},
    "family":  {"hotel": 0.35, "food": 0.24, "transport": 0.18, "activities": 0.15, "buffer": 0.08},
}

# Activity pools by tier + style, used to compose day-by-day plans
ACTIVITY_POOL = {
    "beach": {
        "relaxed": ["a slow sunrise walk on the beach", "a beachfront cafe brunch", "a sunset boat cruise", "a spa & wellness session"],
        "active":  ["parasailing at the main beach", "a scooter ride to a hidden cove", "scuba diving taster session", "a night market crawl"],
        "family":  ["a shallow-water beach morning", "a dolphin-spotting boat trip", "a visit to the local fort", "a kid-friendly water park"],
    },
    "hill": {
        "relaxed": ["a cafe-hopping walk through the town", "a viewpoint sunrise stop", "a tea/coffee estate tour", "a quiet lakeside evening"],
        "active":  ["a guided day trek", "paragliding (weather permitting)", "river crossing / zip-line activity", "a summit viewpoint hike"],
        "family":  ["a toy-train or cable-car ride", "a nature park visit", "a local market stroll", "a picnic by the valley viewpoint"],
    },
    "tier2": {
        "relaxed": ["a heritage haveli walking tour", "a rooftop-cafe evening", "a textile/craft market visit", "a slow palace-grounds stroll"],
        "active":  ["a walled-city cycling tour", "a step-well & fort trek", "a street-food tasting trail", "a hot-air-balloon sunrise ride"],
        "family":  ["a palace & museum visit", "a puppet-show / cultural evening", "an elephant/animal sanctuary visit", "a local market shopping stop"],
    },
    "metro": {
        "relaxed": ["a heritage-district walking tour", "a seafront promenade evening", "a museum & art-gallery visit", "a rooftop dinner"],
        "active":  ["a local train + market crawl", "a street-food trail", "a live-music / nightlife stop", "a bay cruise"],
        "family":  ["a science/city museum visit", "a promenade & amusement park stop", "a planetarium visit", "a mall + food-court evening"],
    },
    "heritage": {
        "relaxed": ["a sunrise monument visit (beat the crowds)", "a riverside evening walk", "a local craft workshop visit", "a heritage-hotel high tea"],
        "active":  ["a full monument-complex exploration", "a cycle-rickshaw old-town tour", "a river boat ride at dawn", "a food-trail walking tour"],
        "family":  ["a guided monument tour with a storyteller", "a boat ride on the river", "a local sweets tasting stop", "a cultural evening show"],
    },
}

DAY_THEME_TEMPLATES = [
    "Arrival & First Impressions",
    "Signature Sights",
    "Local Culture & Flavours",
    "Adventure & Nature",
    "Markets & Downtime",
    "Hidden Gems",
    "Departure Day",
]
