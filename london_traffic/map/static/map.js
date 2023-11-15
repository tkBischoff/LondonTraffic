// Initialize and add the map
let map;
let markers = [];


async function initMap() {
  // The location of Uluru
  const position = { lat: 51.509865, lng: -0.118092 };
  // Request needed libraries.
  //@ts-ignore
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerView } = await google.maps.importLibrary("marker");

  // The map, centered at Uluru
  map = new Map(document.getElementById("map"), {
    zoom: 11,
    center: position,
    mapId: "DEMO_MAP_ID",
  });

  // The marker, positioned at Uluru
  const marker = new AdvancedMarkerView({
    map: map,
    position: position,
    title: "Uluru",
  });
}


function getTraffic(){
  $.ajax({url: "/traffic/", success: function(result){
    var traffic_list = result['traffic_list'];
    var cam_list = result['jam_cams'];
    var heatMapData = [];

    for (var cam of traffic_list){
      heatMapData.push({location: new google.maps.LatLng(cam[0], cam[1]), weight: cam[2]});
    }

    for (var cam of cam_list){

      const marker = new google.maps.Marker({
        position: { lat: cam[0], lng: cam[1] },
        map,
      });

      marker.metadata = {'video_url': cam[2] };
      markers.push(marker);

      /*
      marker.addEventListener("click", function (e) {
        var video_url = e.target.metadata['video_url'];
        var video = new google.maps.InfoWindow({
          content: '<video controls="" style="width:200px;height:200px;">' +
          `<source src="${cam[2]}" type="video/webm;">` +
          '</video>'
        });
        video.open(map, marker);
      });
      */

      marker.addListener("click", (e) => {
        var video_url = marker.metadata['video_url'];
        var video = new google.maps.InfoWindow({
          content: '<video controls="" style="width:200px;height:200px;">' +
          `<source src="${video_url}" type="video/webm;">` +
          '</video>'
        });
        video.open(map, marker);
      });
    }

    var heatmap = new google.maps.visualization.HeatmapLayer({
      data: heatMapData,
      dissipating: true,
      radius: 120,
      opacity: 0.25
    });
    heatmap.setMap(map)
  }});
}

function addClickEvents(){
  console.log(markers);
  /*
  for (var marker of markers) {
    console.log("Adding click");
    marker.addEventListener("click", function (e) {
      var video_url = e.target.metadata['video_url'];
      var video = new google.maps.InfoWindow({
        content: '<video controls="" style="width:200px;height:200px;">' +
        `<source src="${video}" type="video/webm;">` +
        '</video>'
      });
      video.open(map, marker);
    });
  }
  */

  markers.forEach((cam, index) => {
    console.log("Adding click");
  });
}
