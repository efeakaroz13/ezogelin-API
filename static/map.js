var map = L.map('map');
map.setView([39.478, 34.349], 6);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '<a href="https://github.com/efeakaroz13">Efe Akaröz</a> <img src="https://avatars.githubusercontent.com/u/69296379?v=4" width="10">'
}).addTo(map);

var map2 = L.map('minMap');

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '<a href="https://github.com/efeakaroz13">Efe Akaröz</a> <img src="https://avatars.githubusercontent.com/u/69296379?v=4" width="10">'
}).addTo(map2);


//Current location with geolocation API
const options = {
  enableHighAccuracy: true,
  timeout: 5000,
  maximumAge: 0,
};
var greenIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
function success(pos) {
  const crd = pos.coords;

  console.log("Your current position is:");
  console.log(`Latitude : ${crd.latitude}`);
  console.log(`Longitude: ${crd.longitude}`);
  console.log(`More or less ${crd.accuracy} meters.`);
    L.marker([crd.latitude,crd.longitude],{icon:greenIcon}).addTo(map)
    .bindPopup("Mevcut Konum")
    .openPopup();
  logit(crd.latitude,crd.longitude,"Mevcut Konum");
}

function error(err) {
  console.warn(`ERROR(${err.code}): ${err.message}`);
}

navigator.geolocation.getCurrentPosition(success, error, options);





function logit(lat,lng,name){
    lat = parseFloat(lat)
    lng = parseFloat(lng)
    document.getElementById("log").innerHTML = document.getElementById("log").innerHTML+"<li class='list-group-item'>"+name+"<i style='color:gray;font-size:15px' >"+lat+","+lng+"</i>"+ "<button onclick='checkA("+lat+","+lng+")' class='btn btn light'>Sorgula</button><button class='btn btn-light' onclick='findInMap("+lat+","+lng+")'>Haritada göster</button></li>" 
}
function findInMap(lat,lng){
    map.setView([lat,lng],18);
}
function find_on_map(){
    entry = document.getElementById("entry").value
    $.getJSON("/get_coordinates?q="+entry,function(data){
        console.log(data)
        lat = parseFloat(data.lat);
        lon = parseFloat(data.lng);
        map.setView([lat,lon],12);
        L.marker([lat,lon]).addTo(map)
            .bindPopup(data.admin_name+","+data.city)
            .openPopup();
        logit(lat,lon,data.admin_name+","+data.city)
    })
}
function find_on_map_coordinates(){
    query = document.getElementById("latlong").value;
    lat = parseFloat(query.split(",")[0])
    lng = parseFloat(query.split(",")[1])
    map.setView([lat,lng],15)
    L.marker([lat,lng]).addTo(map)
        .bindPopup(lat+","+lng+" Özel Konum")
        .openPopup();
    logit(lat,lng,"Özel Konum")
}

outputData = {}

function checkA(lat,lng){
    dataname = lat+""+lng;
    document.getElementById("sonuc").innerHTML = ""
    if (outputData.dataname != undefined)
    {
        allp = outputData.dataname
        
        allpKeys = Object.keys(allp)
        for (var i = allpKeys.length - 1; i >= 0; i--) {
            current = allpKeys[i]
            sonuc = document.getElementById("sonuc")

            sonuc.innerHTML = sonuc.innerHTML + "<p>"+current+":"+allp[current]+"</p><hr>"

        }

    }else{
        $.getJSON("/parsel_sorgu?lat="+lat+"&"+"long="+lng,function(data){
            allp = data.properties
            
            outputData.dataname = allp;
            allpKeys = Object.keys(allp)
            coordinates = data.geometry["coordinates"][0]
            coordinates2 = []
            for (let c = 0; c < coordinates.length; c++) {
                const element = coordinates[c];
                elem2 = element.reverse();
                coordinates2.push(elem2);
                
            }
            var polygon = L.polygon([
                coordinates
            ]).addTo(map);

            

            findInMap(lat,lng)
            for (var i = allpKeys.length - 1; i >= 0; i--) {
                current = allpKeys[i]
                sonuc = document.getElementById("sonuc")

                sonuc.innerHTML = sonuc.innerHTML + "<p>"+current+":"+allp[current]+"</p><hr>"

            }
        })
    }
    
    
    
}
function checkB() {
    id_ = document.getElementById("nh").value
    ada = document.getElementById("ada").value;
    parsel = document.getElementById("parsel").value;

    dataname = id_+""+ada+parsel;
    document.getElementById("sonucText").innerHTML = ""
    if (outputData.dataname != undefined)
    {
        allp = outputData.dataname
        
        allpKeys = Object.keys(allp)
        for (var i = allpKeys.length - 1; i >= 0; i--) {
            current = allpKeys[i]
            sonuc = document.getElementById("sonucText")

            sonuc.innerHTML = sonuc.innerHTML + "<p>"+current+":"+allp[current]+"</p><hr>"

        }

    }else{
        $.getJSON("/idari/"+id_+"/"+ada+"/"+parsel,function(data){
            allp = data.properties
            
            outputData.dataname = allp;
            allpKeys = Object.keys(allp)
            coordinates = data.geometry["coordinates"][0]
            coordinates2 = []
            for (let c = 0; c < coordinates.length; c++) {
                const element = coordinates[c];
                elem2 = element.reverse();
                coordinates2.push(elem2);
                
            }
            var polygon = L.polygon([
                coordinates
            ]).addTo(map);
            try{
                findInMap(coordinates2[0])
                map2.setView(coordinates2[0], 15);
                console.log(coordinates2[0]);
            }catch{
                try{
                    findInMap(coordinates2[1])
                    map2.setView(coordinates2[1], 15);
                    console.log(coordinates2[1]);
                }catch{
                    null
                }
                
            }
            

            
            

            
            var polygon = L.polygon([
                coordinates
            ]).addTo(map2);

            openPopup()
            for (var i = allpKeys.length - 1; i >= 0; i--) {
                current = allpKeys[i]
                sonuc = document.getElementById("sonucText")

                sonuc.innerHTML = sonuc.innerHTML + "<p>"+current+":"+allp[current]+"</p><hr>"

            }
        })
    }
}

function LoadCities(){
    $.getJSON("/get_cities",function(data){
        document.getElementById("cities").innerHTML = ""
        for (let d = 0; d < data.length; d++) {
            const element = data[d];
            document.getElementById("cities").innerHTML= document.getElementById("cities").innerHTML+"<option value='"+element.id+"' id='"+element.id+"'>"+element.text+"</option>"
            
        }
    })
}
LoadCities()
city = ""
function getDistricts(){
    city1 = document.getElementById("cities")

    document.getElementById("districts").innerHTML = ""
    $.getJSON("/getDistricts/"+city1.value,function(districts){
        city = document.getElementById(document.getElementById("cities").value).innerHTML;
        entry = city+","+city;
        for (let district = 0; district < districts.length; district++) {
            const element = districts[district];
            document.getElementById("districts").innerHTML = document.getElementById("districts").innerHTML +"<option value='"+element.id+"' id='"+element.id+"'>"+element.text+"</option>"
            
        }
        getnh();
        $.getJSON("/get_coordinates?q="+entry,function(data){
            
            lat = parseFloat(data.lat);
            lon = parseFloat(data.lng);
            map.setView([lat,lon],12);

            
        })
    })
}
function getnh(){

    document.getElementById("nh").innerHTML = ""
    district1 = document.getElementById("districts")

    $.getJSON("/nh/"+district1.value,function(districts){

        district = document.getElementById(document.getElementById("districts").value).innerHTML
        entry = city+","+district;
        console.log()
        for (let district = 0; district < districts.length; district++) {
            const element = districts[district];
            document.getElementById("nh").innerHTML = document.getElementById("nh").innerHTML +"<option value='"+element.id+"' id='"+element.id+"'>"+element.text+"</option>"
            
        }
        console.log(entry)
        $.getJSON("/get_coordinates?q="+entry,function(data){
            
            lat = parseFloat(data.lat);
            lon = parseFloat(data.lng);
            map.setView([lat,lon],12);
            
        })
    })
}

opened_popup = 0
function openPopup(){
    if (opened_popup==0) {
        document.getElementById("sonuc").style.display = "";
        opened_popup = 1;
        document.getElementById("map").style.display = "none";
    }else{
        document.getElementById("sonuc").style.display = "none";
        opened_popup = 0;
        document.getElementById("map").style.display = "";
    }

}
/*
L.marker([51.5, -0.09]).addTo(map)
    .bindPopup('A pretty CSS3 popup.<br> Easily customizable.')
    .openPopup();
*/