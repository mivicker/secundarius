function miles_to_meters(miles) {
    return miles * 1609.34;
};

// TODO: have this check the census api for the code provided to make sure
// that the tool tip is reporting the right info. Maybe have a secondary explainer
// pop-up that will give details of any aggregation or other data issues.

function print_zcta_deets(zcta) {
return `<p><b>${zcta["NAME20"]}</b></p>
<p>Below 150% of poverty and over 55:</p>
<p>${zcta["below poverty over 55"]}</p>
<p>Total population:</p>
<p>${zcta["population"]}</p>
`
};


const drawDoorDashLimit = (site) => {
    var name = L.divIcon({
        className: "circ-titles",
        html: `<p>${site.name}</p>`
    });
    return L.layerGroup([
        L.marker([site["lat"], site["lng"]], {icon: name}),
        L.circle([site["lat"], site["lng"]], {
            color: 'green',
            fillColor: 'green',
            radius: 50,
            fillOpacity: "1",
        }),
        L.circle([site["lat"], site["lng"]], {
            interactive: false,
            color: 'gold',
            strokeOpacity: 0.5,
            weight: 3,
            stroke: true,
             fillColor: 'yellow',
             fillOpacity: '0',
            radius: miles_to_meters(10)
        }),
        L.circle([site["lat"], site["lng"]], {
            interactive: false,
            color: 'green',
            weight: 3,
            stroke: true,
            fillColor: 'lightgreen',
            fillOpacity: '0',
            radius: miles_to_meters(8)
        }),
    ])
};


var map = L.map('map').setView([42.47, -83.24], 11);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: 'c. OpenSteetMap'
}).addTo(map);


let zctas_obj = d3.json(current_domain + "/zips")
    .then(data => {
        // Pull out all values for use in calculating color scale.
        const V = d3.map(data["features"], item => item["properties"]["below poverty over 55"]);

        const scale = legend({
            color: d3.scaleSequential(d3.extent(V), d3.interpolateViridis),
            title: "Population with income < 150% of federal poverty line and age > 55"
        });

        // 
        const viridis = d3.scaleSequential().domain(d3.extent(V))
            .interpolator(d3.interpolateViridis);

        var zctas = L.geoJSON(data, {
            style: function (feature) {
                let constituents = feature["properties"]["below poverty over 55"];
                return {
                    color: "white",
                    weight: 2,
                    opacity: '0.4',
                    fillColor: viridis(constituents),
                    stroke: true,
                    fillOpacity: '0.4',
                }
            }
        }).bindPopup(function (layer) {
            return print_zcta_deets(layer.feature.properties);
        }).addTo(map).bringToBack();
    });


var control = L.control.layers({},{})

d3.json(current_domain +"/sites")
    .then(data => {
        for (site of data.sites) {
            var name = L.divIcon({html: `<h1>${site.name}</h1>`});
            var circle = drawDoorDashLimit(site);
            control.addOverlay(circle, site.name);
        }
    });

control.addTo(map);
