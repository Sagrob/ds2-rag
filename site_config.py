from weapons import WEAPONS_SITES

SITES_BY_CATEGORY = {
    "Weapons": WEAPONS_SITES,

     }

RESTRICTED_SITES = [site for sites in SITES_BY_CATEGORY.values() for site in sites]

