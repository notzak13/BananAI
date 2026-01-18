from datetime import datetime, timedelta

# Puerto base
GUAYAQUIL = ("Puerto de Guayaquil", -2.1894, -79.8891, 0)

ROUTES = {
    "USA": [
        GUAYAQUIL,
        ("Océano Pacífico", 2.0, -85.0, 12),
        ("Canal de Panamá", 9.08, -79.68, 24),
        ("Mar Caribe", 18.0, -75.0, 48),
        ("Cerca de Florida", 25.8, -80.1, 72),
        ("Puerto de Miami", 25.77, -80.19, 96),
    ],

    "GERMANY": [
        GUAYAQUIL,
        ("Canal de Panamá", 9.08, -79.68, 24),
        ("Océano Atlántico", 30.0, -40.0, 120),
        ("Puerto de Hamburgo", 53.54, 9.99, 240),
    ],

    "SPAIN": [
        GUAYAQUIL,
        ("Canal de Panamá", 9.08, -79.68, 24),
        ("Océano Atlántico", 25.0, -30.0, 120),
        ("Mar Mediterráneo", 37.0, -5.0, 180),
        ("Puerto de Valencia", 39.45, -0.32, 216),
    ],

    "CHINA": [
        GUAYAQUIL,
        ("Océano Pacífico", -5.0, -110.0, 48),
        ("Océano Pacífico Central", 10.0, 160.0, 240),
        ("Mar de China Meridional", 20.0, 120.0, 360),
        ("Puerto de Shanghái", 31.23, 121.47, 432),
    ],

    "LOCAL": [
        GUAYAQUIL,
        ("Centro de Distribución Nacional", -1.5, -78.0, 6),
    ],
}

def simulate_shipment(start_time: datetime, destination: str):
    route = ROUTES.get(destination.upper())

    if not route:
        return []

    timeline = []
    for name, lat, lon, hours in route:
        timeline.append({
            "location": name,
            "lat": lat,
            "lon": lon,
            "timestamp": start_time + timedelta(hours=hours)
        })

    return timeline
