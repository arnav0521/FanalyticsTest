import pandas as pd
import folium
import json

df = pd.read_csv("geocoded_power4.csv")

school_col = "School"
city_cols = ["City 1", "City 2", "City 3"]

exclude_schools = ["Miami", "Pitt", "Stanford", "Syracuse", "USC"]

archetype_lookup = {
    "Alabama": "National Brand Fanatics",
    "Georgia": "National Brand Fanatics",
    "Ohio State": "National Brand Fanatics",
    "Texas": "National Brand Fanatics",
    "Clemson": "National Brand Fanatics",
    "LSU": "National Brand Fanatics",
    "Oklahoma": "National Brand Fanatics",
    "Texas A&M": "National Brand Fanatics",
    "Florida": "National Brand Fanatics",
    "Michigan": "National Brand Fanatics",
    "Tennessee": "National Brand Fanatics",

    "Arizona State": "Regional Community Loyalists",
    "Florida State": "Regional Community Loyalists",
    "Kansas State": "Regional Community Loyalists",
    "Mississippi State": "Regional Community Loyalists",
    "Oklahoma State": "Regional Community Loyalists",
    "Penn State": "Regional Community Loyalists",
    "UCF": "Regional Community Loyalists",
    "Washington": "Regional Community Loyalists",
    "Cincinnati": "Regional Community Loyalists",
    "Iowa": "Regional Community Loyalists",
    "Louisville": "Regional Community Loyalists",
    "Missouri": "Regional Community Loyalists",
    "Ole Miss": "Regional Community Loyalists",
    "South Carolina": "Regional Community Loyalists",
    "Utah": "Regional Community Loyalists",
    "West Virginia": "Regional Community Loyalists",
    "Colorado": "Regional Community Loyalists",
    "Iowa State": "Regional Community Loyalists",
    "Minnesota": "Regional Community Loyalists",
    "NC State": "Regional Community Loyalists",
    "Oregon": "Regional Community Loyalists",
    "Texas Tech": "Regional Community Loyalists",
    "Virginia Tech": "Regional Community Loyalists",

    "Arizona": "Established Traditionalists",
    "Indiana": "Established Traditionalists",
    "Michigan State": "Established Traditionalists",
    "Purdue": "Established Traditionalists",
    "Arkansas": "Established Traditionalists",
    "Kansas": "Established Traditionalists",
    "Nebraska": "Established Traditionalists",
    "Rutgers": "Established Traditionalists",
    "Auburn": "Established Traditionalists",
    "Kentucky": "Established Traditionalists",
    "North Carolina": "Established Traditionalists",
    "Wisconsin": "Established Traditionalists",

    "California": "Disengaged Fans",
    "UCLA": "Disengaged Fans",

    "Georgia Tech": "Selective Affluents",
    "Virginia": "Selective Affluents",
    "Illinois": "Selective Affluents",
    "Maryland": "Selective Affluents",
}

def get_archetype(school):
    return archetype_lookup.get(str(school).strip(), "Unknown")

m = folium.Map(
    location=[39.5, -98.35],
    zoom_start=4,
    tiles="CartoDB positron"
)

circle_data = []

for _, row in df.iterrows():
    school = str(row[school_col]).strip()

    if school in exclude_schools:
        continue

    archetype = get_archetype(school)

    for i, city_col in enumerate(city_cols):
        lat_col = f"{city_col}_lat"
        lon_col = f"{city_col}_lon"

        if pd.notna(row[lat_col]) and pd.notna(row[lon_col]):
            circle_data.append({
                "school": school,
                "city": str(row[city_col]),
                "lat": float(row[lat_col]),
                "lon": float(row[lon_col]),
                "level": i + 1,
                "archetype": archetype
            })

circle_json = json.dumps(circle_data)

school_options = "".join(
    sorted([
        f'<option value="{school}">{school}</option>'
        for school in df[school_col].dropna().astype(str).str.strip().unique()
        if school not in exclude_schools
    ])
)

dropdown_html = f"""
<div style="
    position: fixed;
    top: 20px;
    left: 50px;
    z-index: 9999;
    background: white;
    padding: 10px;
    border: 2px solid gray;
    border-radius: 5px;
">
    <label><b>Select School:</b></label><br>
    <select id="schoolSelect" style="width: 240px;">
        <option value="all">All Schools</option>
        {school_options}
    </select>
</div>

<script>
document.addEventListener("DOMContentLoaded", function() {{

    var mapObj = {m.get_name()};
    var circles = [];
    var cityData = {circle_json};

    function getColor(archetype) {{
        if (archetype === "National Brand Fanatics") return "#d73027";
        if (archetype === "Regional Community Loyalists") return "#1a9850";
        if (archetype === "Established Traditionalists") return "#4575b4";
        if (archetype === "Disengaged Fans") return "#984ea3";
        if (archetype === "Selective Affluents") return "#fdae61";
        return "#999999";
    }}

    function getRadius(level) {{
        if (level === 1) return 120000;
        if (level === 2) return 80000;
        return 50000;
    }}

    function getOpacity(level) {{
        if (level === 1) return 0.45;
        if (level === 2) return 0.30;
        return 0.18;
    }}

    function drawCircles(selectedSchool) {{
        circles.forEach(function(circle) {{
            mapObj.removeLayer(circle);
        }});
        circles = [];

        cityData.forEach(function(item) {{
            if (selectedSchool === "all" || item.school === selectedSchool) {{
                var color = getColor(item.archetype);

                var circle = L.circle([item.lat, item.lon], {{
                    radius: getRadius(item.level),
                    color: color,
                    fillColor: color,
                    fillOpacity: getOpacity(item.level),
                    weight: 2
                }}).addTo(mapObj);

                circle.bindTooltip(
                    item.school + " - " + item.city + " - " + item.archetype
                );

                circles.push(circle);
            }}
        }});
    }}

    document.getElementById("schoolSelect").addEventListener("change", function() {{
        drawCircles(this.value);
    }});

    setTimeout(function() {{
        drawCircles("all");
    }}, 500);

    var legend = L.control({{position: 'bottomright'}});
    legend.onAdd = function () {{
        var div = L.DomUtil.create('div', 'info legend');

        div.style.background = "white";
        div.style.padding = "12px";
        div.style.border = "2px solid gray";
        div.style.borderRadius = "6px";
        div.style.fontSize = "13px";
        div.style.lineHeight = "20px";

        div.innerHTML += "<b>Fanbase Archetypes</b><br>";
        div.innerHTML += "<i style='background:#d73027;width:12px;height:12px;display:inline-block;margin-right:6px;'></i> National Brand Fanatics<br>";
        div.innerHTML += "<i style='background:#1a9850;width:12px;height:12px;display:inline-block;margin-right:6px;'></i> Regional Community Loyalists<br>";
        div.innerHTML += "<i style='background:#4575b4;width:12px;height:12px;display:inline-block;margin-right:6px;'></i> Established Traditionalists<br>";
        div.innerHTML += "<i style='background:#984ea3;width:12px;height:12px;display:inline-block;margin-right:6px;'></i> Disengaged Fans<br>";
        div.innerHTML += "<i style='background:#fdae61;width:12px;height:12px;display:inline-block;margin-right:6px;'></i> Selective Affluents<br>";
        div.innerHTML += "<hr>";
        div.innerHTML += "<b>City Rank Radius</b><br>";
        div.innerHTML += "City 1 = largest/darkest<br>";
        div.innerHTML += "City 2 = medium<br>";
        div.innerHTML += "City 3 = smallest/lightest<br>";

        return div;
    }};
    legend.addTo(mapObj);

}});
</script>
"""

m.get_root().html.add_child(folium.Element(dropdown_html))

print("Number of circles:", len(circle_data))

unknown_schools = sorted([
    s for s in df[school_col].dropna().astype(str).str.strip().unique()
    if s not in archetype_lookup and s not in exclude_schools
])

print("Unknown schools:", unknown_schools)

m.save("school_city_radius_map_improved.html")

print("Done! Saved as school_city_radius_map_improved.html")