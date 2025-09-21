let nombre = null;
let estado = "inicio";

// CHAT CON IA
function enviarMensaje() {
  const input = document.getElementById("chat-message");
  const mensaje = input.value.trim();
  if (!mensaje) return;

  agregarMensaje("usuario", mensaje);
  input.value = "";

  if (!nombre) {
    nombre = mensaje;
    agregarMensaje("bot", `¡Hola ${nombre}! 😊 ¿Qué día te gustaría agendar tu cita?`);
    estado = "preguntar_dia";
    return;
  }

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre, mensaje })
  })
  .then(res => res.json())
  .then(data => {
    agregarMensaje("bot", data.respuesta);
  });
}

function agregarMensaje(tipo, texto) {
  const div = document.createElement("div");
  div.className = `mensaje ${tipo}`;
  div.innerText = texto;
  document.getElementById("chat-window").appendChild(div);
  document.getElementById("chat-window").scrollTop = document.getElementById("chat-window").scrollHeight;
}

// CALENDARIO MENSUAL VISUAL
const semanaHeader = document.getElementById("semana-header");
const mesContainer = document.getElementById("mes-container");
const horasContainer = document.getElementById("horas-container");

function generarEncabezadoSemana() {
  const diasSemana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
  diasSemana.forEach(dia => {
    const div = document.createElement("div");
    div.className = "encabezado-dia";
    div.innerText = dia;
    semanaHeader.appendChild(div);
  });
}

function generarCalendarioMes() {
  const hoy = new Date();
  const año = hoy.getFullYear();
  const mes = hoy.getMonth(); // 0 = enero

  const primerDia = new Date(año, mes, 1);
  const ultimoDia = new Date(año, mes + 1, 0);
  const diasEnMes = ultimoDia.getDate();

  const diaSemanaInicio = primerDia.getDay(); // 0 = domingo
  const offset = diaSemanaInicio === 0 ? 6 : diaSemanaInicio - 1;

  for (let i = 0; i < offset; i++) {
    const div = document.createElement("div");
    div.className = "dia-mes invisible";
    mesContainer.appendChild(div);
  }

  for (let i = 1; i <= diasEnMes; i++) {
    const fecha = new Date(año, mes, i);
    const nombreDia = fecha.toLocaleDateString("es-ES", { weekday: "long" });

    const div = document.createElement("div");
    div.className = "dia-mes";
    div.innerText = i;
    div.onclick = () => mostrarHoras(nombreDia.toLowerCase(), i);
    mesContainer.appendChild(div);
  }
}

function mostrarHoras(diaNombre, diaNumero) {
  horasContainer.innerHTML = "";
  horasContainer.classList.remove("oculto");

  fetch(`/disponibilidad/${diaNombre}`)
    .then(res => res.json())
    .then(ocupadas => {
      const horas = generarHoras("8", "11");
      horas.forEach(hora => {
        const horaTexto = `${hora}:00`;
        const div = document.createElement("div");
        div.className = "hora " + (ocupadas.includes(horaTexto) ? "ocupada" : "libre");
        div.innerText = horaTexto;
        horasContainer.appendChild(div);
      });
    });
}

// GENERADOR DE HORAS POR BLOQUES DE 1 HORA
function generarHoras(inicio, fin) {
  const resultado = [];
  let h = parseInt(inicio);
  const hf = parseInt(fin);
  while (h <= hf) {
    resultado.push(`${h}`);
    h += 1;
  }
  return resultado;
}

// LISTA DE CITAS AGENDADAS
function cargarCitas() {
  fetch("/disponibilidad")
    .then(res => res.json())
    .then(citas => {
      const lista = document.getElementById("citas-lista");
      if (!lista) return;
      lista.innerHTML = "";
      citas.forEach(cita => {
        const item = document.createElement("li");
        item.innerText = `${cita.nombre} — ${cita.dia} a las ${cita.hora}`;
        lista.appendChild(item);
      });
    });
}

document.addEventListener("DOMContentLoaded", () => {
  generarEncabezadoSemana();
  generarCalendarioMes();
  cargarCitas();
});

