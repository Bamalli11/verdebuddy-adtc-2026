# Hausa response templates - VerdeBuddy
# Pre-written, verified Hausa answers to avoid LLM hallucination/repetition loops
# Placeholders filled from knowledge base facts extracted deterministically

# Seasonal vocabulary reference
SEASONS = {
    "dry_season": "Lokacin rani",       # October to May
    "rainy_season": "Damina",           # June to September
    "harvest_season": "Lokacin kaka",   # Late September to November
    "cold_season": "Lokacin hunturu",   # December to February
    "spring": "Lokacin bazara"
}

HAUSA_TEMPLATES = {
    "crop_planting": "Za ka iya shuka {crop} a watannin {season}. Mafi kyawun kasa na shuka {crop} shine {soil}. Yana daukar kwanaki {maturity} kafin girbi. Jinsunan da aka ba da shawara sun hada da: {varieties}.",

    "crop_fertilizer": "Don {crop}, yi amfani da taki NPK. Sanya taki a lokacin shuka, sannan a kara da taki na biyu bayan makonni shida. Kada ka wuce gona da iri wajen amfani da taki.",

    "crop_disease": "Cutar da take shafar {crop} sun hada da: {diseases}. Idan ka ga ganyen suna chanza kala/kamanni, ka nemi shawarar likitan noma nan take. Rage bada ruwa mai yawa na iya taimakawa.",

    "soil_acidic": "Idan kasarka tana da yawan acid (pH kasa da 5.5), ka sanya Farar Kasa (agricultural lime stone) tan biyu zuwa hudu a kowace hectare. Bada kwanaki 28 zuwa 42 kafin shukawa domin Farar Kasa ya narke sosai a cikin kasa.",

    "soil_test": "Don gwada pH na kasarka: ka dauka kasa daga wurare dabam-dabam a gonarka, hade su tare, sannan ka kai zuwa dakin gwaje-gwaje na Ma'aikatar Aikin Gona ta Jiha. Za su ba ka sakamako da shawarar da za ka bi.",

    "weather_season": "A yankin Arewa ta Najeriya, damina takan fara a watan {north_start}. A yankin Kudu kuma, damina takan fara a watan {south_start}.",

    "weather_drought": "Idan aka samu fari, ka rage yawan shuka a wurin da ba shi da ruwa sosai. Ka yi amfani da ciyawa (mulch) domin adana danshin kasa. Ka zabi jinsunan shuka wadanda ke jure fari kamar gero da dawa.",

    "market_price": "Farashin {crop} yakan bambanta gwargwadon lokaci. Farashi yakan yi kasa a lokacin girbi, ya kuma hau kafin girbi na gaba. Ka tuntubi kasuwar {market} domin sabon farashi.",

    "market_sell_timing": "Mafi kyawun lokacin sayarwa shine kafin girbi na gaba lokacin da kayan suka yi karanci a kasuwa. Idan za ka iya ajiye {crop}, jira watanni kadan bayan girbi domin samun riba mai kyau.",

    "investment_roi": "Amfanin gona da ke da riba mai kyau a Najeriya sun hada da shinkafa, ganyayyaki, sesame, cashew, da koko. Wadannan amfanin gona suna da bukata mai yawa a kasashen waje kuma suna samun kudi mai kyau.",

    "investment_land": "Don samun fili na noma, ka tuntubi Ma'aikatar Filaye ta Jiha domin samun Takardar Mallakar Fili (Certificate of Occupancy). Wannan yana kare hakkinka a kan filin.",

    "default": "Ina nan don taimaka maka game da noma da kasuwanci a Najeriya. Ka tambaye ni game da shuka, kasa, yanayi, ko farashin kasuwa, kuma zan yi kokarin bayar da amsa daidai."
}

def classify_hausa_topic(query_lower, has_crop, has_soil, has_weather, has_market, has_investment):
    """Return the best template key based on already-detected topic flags."""
    if has_crop:
        if any(w in query_lower for w in ["taki", "npk", "fertilizer"]):
            return "crop_fertilizer"
        if any(w in query_lower for w in ["cuta", "rashin lafiya", "disease"]):
            return "crop_disease"
        return "crop_planting"
    if has_soil:
        if any(w in query_lower for w in ["acid", "acidic", "pH"]):
            return "soil_acidic"
        return "soil_test"
    if has_weather:
        if any(w in query_lower for w in ["fari", "drought"]):
            return "weather_drought"
        return "weather_season"
    if has_market:
        if any(w in query_lower for w in ["yaushe", "lokacin sayarwa", "when to sell"]):
            return "market_sell_timing"
        return "market_price"
    if has_investment:
        if any(w in query_lower for w in ["fili", "land"]):
            return "investment_land"
        return "investment_roi"
    return "default"
