
const webSocketPico = new WebSocket("ws://192.168.0.140/ws"); //  ws://192.168.1.140/
const webSocketRas = new WebSocket("ws://192.168.0.166:8765"); //"ws://192.168.1.169:8765"

webSocketRas.addEventListener('message', messageWebSocketRas)
webSocketPico.addEventListener('message', messageWebSocketPico)




function messageWebSocketPico(ev) {
    console.log('<<< ' + ev.data);
    switch (ev.data) {
        case 'INDICATOR_LIGHT':
          setButtonRandomColor()
          break;
        case 'CHARGING_ON':
          document.getElementById("light-indicator2").style.backgroundColor = "yellow"; 
          break;
        case 'CHARGING_OFF': 
          document.getElementById("light-indicator2").style.backgroundColor = "grey";
          break;
        case ev.data.startsWith("CHARGER_VOLTAGE:"):  
          break;

        default:
          console.log("");

    if (ev.data.startsWith("CHARGER_VOLTAGE:")){
      var CHARGER_VOLTAGE = ev.data.split(":")[1];
      document.getElementById("charger-voltage-plate").innerHTML = CHARGER_VOLTAGE + "A";
      }
  } };


let BATTERY_VOLTAGE_CELL1;
let BATTERY_VOLTAGE_CELL2;
let BATTERY_VOLTAGE_CELL3;
let BATTERY_VOLTAGE_CELL4;

  
//tar i mot beskjed fra raspberry
function messageWebSocketRas(ev){
  console.log('<<< ' + ev.data);
  switch (ev.data) {
    case 'ras_say_the_plate_is_off':
      document.getElementById("light-indicator3").style.backgroundColor = "grey"; 
      break;   
    default:
      console.log("");
    if (ev.data.startsWith("BATTERY_VOLTAGE_CELL0:")){
      BATTERY_VOLTAGE_CELL1 = ev.data.split(":")[1];
      document.getElementById("battery-cell1").innerHTML = BATTERY_VOLTAGE_CELL1 + "V";
      console.log(BATTERY_VOLTAGE_CELL1) = parseInt(BATTERY_VOLTAGE_CELL1, 10) +10;
      
    }
    else if (ev.data.startsWith("BATTERY_VOLTAGE_CELL1:")){
      BATTERY_VOLTAGE_CELL2 = ev.data.split(":")[1];
      document.getElementById("battery-cell2").innerHTML = BATTERY_VOLTAGE_CELL2 + "V";
      } 
    else if (ev.data.startsWith("BATTERY_VOLTAGE_CELL2:")){
      BATTERY_VOLTAGE_CELL3 = ev.data.split(":")[1];
      document.getElementById("battery-cell3").innerHTML = BATTERY_VOLTAGE_CELL3 + "V";
      } 
    else if (ev.data.startsWith("BATTERY_VOLTAGE_CELL3:")){
      BATTERY_VOLTAGE_CELL4 = ev.data.split(":")[1];
      document.getElementById("battery-cell4").innerHTML = BATTERY_VOLTAGE_CELL4 + "V";
      }

      } 

  }
  console.log(BATTERY_VOLTAGE_CELL1);
  battery_voltage_to_percent = 0.004;
  Battery_percents1 = (( BATTERY_VOLTAGE_CELL1-3.8) / battery_voltage_to_percent);
  let battery_state1 = (Battery_percents1.toFixed(0));
  const progress1 = document.querySelector('.progress_done1');

  progress1.style.width = battery_state1 + "%";
  
  document.getElementById('battery_state_bar1').innerHTML = battery_state1 + "%";




  console.log(BATTERY_VOLTAGE_CELL2)
  battery_voltage_to_percent = 0.004;
  Battery_percents2 = (( BATTERY_VOLTAGE_CELL2-3.8) / battery_voltage_to_percent);
  let battery_state2 = (Battery_percents2.toFixed(0));
  const progress2 = document.querySelector('.progress_done2');

  progress2.style.width = battery_state2 + "%";
  
  document.getElementById('battery_state_bar2').innerHTML = battery_state2 + "%";




  console.log(BATTERY_VOLTAGE_CELL3)
  battery_voltage_to_percent = 0.004;
  Battery_percents3 = (( BATTERY_VOLTAGE_CELL3-3.8) / battery_voltage_to_percent);
  let battery_state3 = (Battery_percents3.toFixed(0));
  const progress3 = document.querySelector('.progress_done3');

  progress3.style.width = battery_state3 + "%";
  
  document.getElementById('battery_state_bar3').innerHTML = battery_state3 + "%";

  console.log(BATTERY_VOLTAGE_CELL4)
  battery_voltage_to_percent = 0.004;
  Battery_percents4 = (( BATTERY_VOLTAGE_CELL4-3.8) / battery_voltage_to_percent);
  let battery_state4 = (Battery_percents4.toFixed(0));
  const progress4 = document.querySelector('.progress_done4');

  progress4.style.width = battery_state4 + "%";
  
  document.getElementById('battery_state_bar4').innerHTML = battery_state4 + "%";

  //Total battery
  battery_total_voltage_to_percent = 0.02;
  Battery_total_voltage = parseFloat(BATTERY_VOLTAGE_CELL1) + parseFloat(BATTERY_VOLTAGE_CELL2) + parseFloat(BATTERY_VOLTAGE_CELL3) + parseFloat(BATTERY_VOLTAGE_CELL4) 
  console.log(Battery_total_voltage)
  Battery_percents_total = ((Battery_total_voltage-15.2) / battery_total_voltage_to_percent);
  console.log(Battery_percents_total)

  let battery_state_total = Battery_percents_total.toFixed(0);
  const progress_total = document.querySelector('.progress_done_side_total');
  
  progress_total.style.width = battery_state_total + "%";
  
  document.getElementById('battery_state_bar_side_total').innerHTML = battery_state_total + "%";

  document.getElementById("battery-cell_total").innerHTML = Battery_total_voltage.toFixed(2) + "V"


document.addEventListener('DOMContentLoaded', function() {
    var checkbox = document.querySelector('input[name="checkboxPlate"]');
    checkbox.addEventListener('change', function() {
        if (checkbox.checked) {
            console.log("Checkbox er avkrysset");
            sendCommandPico('CHARGING_PLATE_ON');
            sendCommandRas('CHARGING_PLATE_ON')
        } else {
          sendCommandPico('CHARGING_PLATE_OFF'); 
          sendCommandRas('CHARGING_PLATE_OFF');
        }
        
    });
});



function setButtonRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    document.getElementById("light-indicator1").style.backgroundColor = color;
  }




function sendCommandPico(command) {
    console.log("Sending message", command);
    webSocketPico.send(command);
}


//få opp kommunikasjon med Raspberry pi
function sendCommandRas(command) {
  console.log("Sending message to Raspberry Pi:", command);

  webSocketRas.send(command);
}

function callBack(){
  document.getElementById("light-indicator1").style.backgroundColor = setButtonRandomColor();
  sendCommandPico(''); 
  //sendCommandRas('');
  sendCommandRas('BATTERY_STATS');
}
setInterval(callBack, 1000);



const socket = new WebSocket('ws://192.168.0.165:8765'); //ip to raspberry pi 192.168.0.165 localhost
  socket.onmessage = function (event) {
      let parts = event.data.split(';');
      const imageElement = document.getElementById('videoFrame');
      const detailsElement = document.getElementById('objectDetails');
      
      imageElement.src = 'data:image/jpeg;base64,' + parts[0];
      detailsElement.textContent = parts[1];  // Display object details
  };

  socket.onerror = function (error) {
      console.error('WebSocket error:', error);
  };