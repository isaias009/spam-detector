// Obtén el formulario y el spinner
var form1 = document.getElementById('form1');
var form2 = document.getElementById('form2');
var spinnerOverlay = document.getElementById('spinner-overlay');

// Agrega un evento 'submit' al formulario
form1.addEventListener('submit', function() {
  mostrarSpinner();
});

form2.addEventListener('submit', function() {
  mostrarSpinner();
});

// Función para mostrar el spinner
function mostrarSpinner() {
  spinnerOverlay.style.display = 'block'; // Muestra el spinner
}

// Función para ocultar el spinner
function ocultarSpinner() {
  spinnerOverlay.style.display = 'none'; // Oculta el spinner
}
