// Obtener los parámetros de la URL
const urlParams = new URLSearchParams(window.location.search);

// Obtener el valor del parámetro "page"
const page = urlParams.get('page');

// Función para cargar el contenido según la página seleccionada
function loadPageContent(page) {
  // Lógica para cargar el contenido según la página
  let div;
  let link;
  switch (page) {
    case 'home':
      div = document.getElementById('contendor-home');
      link = document.getElementById('link-home');
      link.classList.add('active');
      div.style.display = "block";
      break;
    case 'msg':
      div = document.getElementById('contendor-app');
      link = document.getElementById('link-msg');
      link.classList.add('active');
      div.style.display = "flex";
      break;
    case 'collection':
      div = document.getElementById('contendor-mensajes');
      link = document.getElementById('link-collection');
      link.classList.add('active');
      div.style.display = "flex";
      break;

    case 'data':
      div = document.getElementById('contendor-data');
      link = document.getElementById('link-data');
      link.classList.add('active');
      div.style.display = "flex";
      break;
    default:
      contentDiv.textContent = 'Page not found';
    break;
  }
}

// Cargar el contenido inicial según el parámetro "page" actual
loadPageContent(page);
