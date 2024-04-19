
const webSocketPico = new WebSocket("ws://192.168.1.140/ws")
const webSocketRas = new WebSocket("ws://192.168.1.169:8765");


webSocketPico.addEventListener('message', messageWebSocketPico)
webSocketRas.addEventListener('message', messageWebSocketRas)



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


  
//tar i mot beskjed fra raspberry
function messageWebSocketRas(ev){
  console.log('<<< ' + ev.data);
  switch (ev.data) {
    case 'ras_say_the_plate_is_off':
      document.getElementById("light-indicator3").style.backgroundColor = "grey"; 

  }
}

document.addEventListener('DOMContentLoaded', function() {
    var checkbox = document.querySelector('input[name="checkboxPlate"]');
    checkbox.addEventListener('change', function() {
        if (checkbox.checked) {
            console.log("Checkbox er avkrysset");
            sendCommandPico('CHARGING_PLATE_ON');
            sendCommandRas('CHARGING_PLATE_ON')
        } else {
          sendCommandPico('CHARGING_PLATE_OFF'); 
          sendCommandRas('CHARGING_PLATE_OFF')
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

//sender beskjed til raspberry
function sendCommandRas(command) {
  console.log("Sending messageras", command);
  
  webSocketRas.send(command);
}



function callBack(){
  document.getElementById("light-indicator1").style.backgroundColor = setButtonRandomColor();
  sendCommandPico(''); 
  sendCommandRas('');
 
}
setInterval(callBack, 1000)


//Battery system
let battery_state1 = 20;
const progress1 = document.querySelector('.progress_done1');

progress1.style.width = battery_state1 + "%";

document.getElementById('battery_state_bar1').innerHTML = battery_state1 + "%";

let battery_state2 = 40;
const progress2 = document.querySelector('.progress_done2');

progress2.style.width = battery_state2 + "%";

document.getElementById('battery_state_bar2').innerHTML = battery_state2 + "%";

let battery_state3 = 60;
const progress3 = document.querySelector('.progress_done3');

progress3.style.width = battery_state3 + "%";

document.getElementById('battery_state_bar3').innerHTML = battery_state3 + "%";

let battery_state4 = 80;
const progress4 = document.querySelector('.progress_done4');

progress4.style.width = battery_state4 + "%";

document.getElementById('battery_state_bar4').innerHTML = battery_state4 + "%";