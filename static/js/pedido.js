// =============================
// 🛒 MODAL PRODUCTOS (TU CÓDIGO)
// =============================
function abrirModal(nombre) {
    const modal = document.getElementById('pedidoModal');
    const productoNombre = document.getElementById('productoNombre');
    const productoInput = document.getElementById('productoInput');
    const cantidadInput = document.getElementById('cantidad');
    
    productoNombre.innerText = nombre;
    productoInput.value = nombre;

    if (cantidadInput) {
        cantidadInput.value = 1;
    }

    modal.style.display = 'block';

    setTimeout(() => {
        if (cantidadInput) {
            cantidadInput.focus();
            cantidadInput.select();
        }
    }, 100);
}

function cerrarModal() {
    const modal = document.getElementById('pedidoModal');
    modal.style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('pedidoModal');
    if (event.target === modal) {
        cerrarModal();
    }
}

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        cerrarModal();
    }
});


// =============================
// 🎬 ANIMACIONES (TU CÓDIGO)
// =============================
document.addEventListener('DOMContentLoaded', function() {
    animarProductos();
});

function animarProductos() {
    const productos = document.querySelectorAll('.producto');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });

    productos.forEach(producto => {
        producto.style.opacity = '0';
        producto.style.transform = 'translateY(20px)';
        producto.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(producto);
    });
}


// =============================
// 🤖 LUNA CHATBOT
// =============================

let chatAbierto = false;

// Abrir / cerrar chat
function toggleChat() {
    const chat = document.getElementById("chatLuna");

    chatAbierto = !chatAbierto;
    chat.style.display = chatAbierto ? "flex" : "none";

    // mensaje inicial
    if (chatAbierto && document.getElementById("chatBody").innerHTML === "") {
        agregarMensaje("LUNA", "👋 Hola soy LUNA, dime qué buscas por categoria y precio y te ayudaré 💙");
    }
}


// Agregar mensajes al chat
function agregarMensaje(usuario, mensaje) {
    const chat = document.getElementById("chatBody");

    chat.innerHTML += `
        <div class="mensaje">
            <b>${usuario}:</b> ${mensaje}
        </div>
    `;

    chat.scrollTop = chat.scrollHeight;
}


// Enviar mensaje
function enviarMensaje() {
    const input = document.getElementById("inputLuna");
    const mensaje = input.value.trim();

    if (mensaje === "") return;

    agregarMensaje("Tú", mensaje);

    fetch('/luna', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mensaje: mensaje })
    })
    .then(res => res.json())
    .then(data => {
        agregarMensaje("LUNA", data.respuesta);

        if (data.productos) {
            actualizarProductos(data.productos);
        }
    });

    input.value = "";
}


// =============================
// 🔥 FILTRAR PRODUCTOS EN PANTALLA
// =============================
function actualizarProductos(productos) {
    const contenedor = document.querySelector(".productos");

    contenedor.innerHTML = "";

    productos.forEach(p => {
        contenedor.innerHTML += `
        <div class="producto fade-in-up">

            <div class="producto-image-container">
                ${p.imagen 
                    ? `<img src="/static/uploads/${p.imagen}">`
                    : `<img src="/static/img/default.png">`
                }
            </div>

            <h4>${p.nombre}</h4>
            <p>${p.descripcion || ''}</p>
            <p class="precio">💰 $${p.precio}</p>

            <button onclick="abrirModal('${p.nombre}')">
                🛒 Seleccionar
            </button>

        </div>
        `;
    });

    // volver a aplicar animación
    animarProductos();
}


// =============================
// ⌨️ ENTER PARA ENVIAR MENSAJE
// =============================
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("inputLuna");

    if (input) {
        input.addEventListener("keypress", function(e) {
            if (e.key === "Enter") {
                enviarMensaje();
            }
        });
    }
});