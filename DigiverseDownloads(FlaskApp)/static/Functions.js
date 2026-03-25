
const colors = ['lightblue', 'lightgreen', 'orange', 'turquoise', 'pink'];
let colorIndex = 0; // Current color index

function changeBackgroundColor() {
  document.body.style.backgroundColor = colors[colorIndex];
  colorIndex = (colorIndex + 1) % colors.length;}

  if (window.location.pathname === '/'){
  setInterval(changeBackgroundColor, 33);}

function changeButtonColor() {
  btnhome.style.backgroundColor = colors[colorIndex];
  btndemos.style.backgroundColor = 'lightblue'
  btnblog.style.backgroundColor = "lightgreen";
  btnstore.style.backgroundColor = "orange";
  btncontact.style.backgroundColor = "turquoise";
  colorIndex = (colorIndex + 1) % colors.length;}
  setInterval(changeButtonColor, 33);

document.addEventListener('DOMContentLoaded', (event) => {
    var toggleVar = 0;
    var iframe = document.getElementById('my-iframe');

    window.toggleMenu = function() {
        toggleVar = toggleVar === 0 ? 1 : 0;
        if (toggleVar === 1) {iframe.style.height = '800px';}
        else {iframe.style.height = '0px';}}});

  function playAudioA() {
  const audio = document.getElementById("AMW");
  audio.play();}

 function playAudioB() {
  const audio = document.getElementById("DDSP");
  audio.play();}

