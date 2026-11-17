"""
Refugio Digital
 
Es un proyecto educativo desarrollado para entrenar a los usuarios
en la identificación de fraudes digitales, perfiles falsos y ataques
de phishing presentes en redes sociales
 
El jugador debe analizar perfiles sospechosos, seleccionar la respuesta
correcta y mantener la temperatura de seguridad para completar todos
los niveles del simulador
 
 Requisitos:
  py -m pip install flask requests
"""

from flask import Flask, render_template_string, request, redirect, url_for, session, jsonify
import subprocess
import sys

app = Flask(__name__)
app.secret_key = 'refugio_digital_secret_key'

# Base de datos simulada del juego
# Cada nivel representa un caso distinto de fraude digital
# Se almacena la información visual del perfil, la pregunta
# las posibles respuestas y los datos mostrados por el escáner
NIVELES = [
    {
        "titulo": "Nivel 1",
        "perfil": "@ana_oficial_vip",
        "bio": " Influencer y modelo | Colaboraciones por DM 📩",
        "datos": "📍 Mty,Mx | 📊 12.5K Seguidores • 2 Seguidos • 0 Publicaciones (Creada hace 3 días)",
        "url_imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ3J6Cl7rX0e1WOIo4LTI58hSFybUVo09CM-qy1KbLmipk9UNy_KG7gh6-k&s=10",
        "pregunta": "¿Qué tipo de fraude representa este perfil?",
        "opciones": [
            "A) Venta de artículos falsificados mediante mensajes directos",
            "B) Extorsión utilizando imágenes personales",
            "C) Creación de una cuenta falsa con bots para simular una popularidad inexistente",
            "D) Robo de identidad directa a una persona real de la región"
        ],
        "correcta": 2,
        "escanner": {
            "IP_Origen": "Servidor Proxy Desconocido",
            "Fecha_Creacion": "Hace 3 días",
            "Dispositivo": "API Automatizada de Bots",
            "Reputacion": "Muy Baja - Alto riesgo de cuenta falsa"
        }
    },
    {
        "titulo": "Nivel 2",
        "perfil": "@soporte_banco_oficial",
        "bio": "🔒 Atención al cliente oficial 24/7. ¡Resuelve tus bloqueos aquí!",
        "datos": "📍 Global | 📊 45 Seguidores • 1,200 Seguidos • 1 Publicación",
        "url_imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTeWzIV9S0fcqqUTEmY51k62so9qtA_p2r678A0KMaQnA&s",
        "pregunta": "¿Qué elemento delata que es un fraude de suplantación?",
        "opciones": [
            "A) Ofrecer un horario de atención al cliente abierto durante las 24 horas del día",
            "B) Utilizar un logotipo con un diseño monocromático",
            "C) Emplear un tono de comunicación formal al redactar los mensajes",
            "D) Ser una cuenta institucional con muy pocos seguidores"
        ],
        "correcta": 3,
        "escanner": {
            "IP_Origen": "Dominio Externo No Oficial (.xyz)",
            "Fecha_Creacion": "Hace 5 días",
            "Certificado_SSL": "Falso / No verificado",
            "Reputacion": "Phishing detectado (Robo de credenciales)"
        }
    },
    {
        "titulo": "Nivel 3",
        "perfil": "@sorteos_apple_global_2026",
        "bio": "📱 ¡Gana un iPhone 17 Pro gratis comentando y registrándote en el link!   https://citibanamex-soporte-actualizacion-segura.xyz/login-token",
        "datos": "📍 EE.UU. | 📊 3 Seguidores • 5,000 Seguidos • 2 Publicaciones",
        "url_imagen": "https://img.magnific.com/vector-gratis/diseno-banner-compras-realista_23-2150277680.jpg?semt=ais_hybrid&w=740&q=80",
        "pregunta": "¿Qué es lo que se quiere lograr con este tipo de ataque?",
        "opciones": [
            "A) Atraer a las víctimas con un premio para robar sus datos personales y credenciales",
            "B) Distribuir premios de tecnología reales para ganar seguidores orgánicos",
            "C) Promover una campaña publicitaria oficial y autorizada por la marca",
            "D) Fomentar la interacción social y comentarios masivos en la plataforma"
        ],
        "correcta": 0,
        "escanner": {
            "IP_Origen": "Servidor de redirección maliciosa",
            "Fecha_Creacion": "Hace 1 semana",
            "Seguidores_Inactivos": "99.8% cuentas falsas / bots",
            "Reputacion": "Gancho de estafa comercial"
        }
    },
    {
        "titulo": "Nivel 4",
        "perfil": "@fatima_perez_nueva",
        "bio": "Hola, perdí mi cuenta principal, sigan esta plis.",
        "datos": "📍 México | 📊 100 Seguidores • 95 Seguidos • 1 Publicación",
        "url_imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR6--jMh1PXVV7piZFEy9jnTR2EwtKX-qk5fS-2UV8mN8XCbU-xOiq2E40o&s=10",
        "pregunta": "¿Qué característica de este perfil delata que se trata de una cuenta clonada?",
        "opciones": [
            "A) Tener una fotografía de perfil donde la persona aparece sonriendo a la cámara.",
            "B) Indicar que su ubicación actual se encuentra dentro del país",
            "C) Utilizar un nombre con la palabra 'nueva' y pedir que la agreguen de nuevo",
            "D) Contar con un número bajo de publicaciones en su historial"
        ],
        "correcta": 2,
        "escanner": {
            "IP_Origen": "Dispositivo diferente al usuario original",
            "Fecha_Creacion": "Hace 2 horas",
            "Coincidencia_Imagen": "98% similitud con cuenta real (Foto robada)",
            "Reputacion": "Suplantación de identidad personal"
        }
    },
    {
        "titulo": "Nivel 5",
        "perfil": "@alertas_urgentes_noticias",
        "bio": "⚠️ ¡URGENTE! Abre el link para ver el video prohibido que la TV oculta.   https://www.youtube.com/watch?v=video-falso",
        "datos": "📍 Global | 📊 2 Seguidores • 0 Seguidos • 50 Publicaciones",
        "url_imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSoJE1-bglCbz_BzrPHTY-ZUon7OB-EeVEaovl-TXVSng&s=10",
        "pregunta": "¿Qué busca este perfil con ganchos alarmistas?",
        "opciones": [
            "A) Compartir información de interés general verificada por agencias",
            "B) Vender suscripciones digitales para portales de noticias independientes",
            "C) Publicar videos multimedia con restricciones de edad para mayores",
            "D) Utilizar titulares alarmistas y sensacionalistas para forzar clics en un enlace externo"
        ],
        "correcta": 3,
        "escanner": {
            "IP_Origen": "Red de distribución de clickbait",
            "Fecha_Creacion": "Hace 1 mes",
            "Enlaces_Ocultos": "Redirección a troyanos / malware",
            "Reputacion": "Alto riesgo de infección digital"
        }
    },
    {
        "titulo": "Nivel 6",
        "perfil": "@empleo_remoto_facil",
        "bio": "💵 Gana $500 USD diarios sin experiencia previa. ¡Cupos limitados!",
        "datos": "📍 Guanajuato | 📊 12 Seguidores • 4,000 Seguidos • 0 Publicaciones",
        "url_imagen": "https://empleate.sinaloa.gob.mx/assets/images/busco-empleo.jpg",
        "pregunta": "¿Por qué es una estafa típica de suplantación y fraude?",
        "opciones": [
            "A) Ofrece oportunidades laborales que se pueden realizar de manera remota",
            "B) Promete un salario exagerado sin pedir experiencia ni requisitos laborales",
            "C) Realiza transacciones financieras en moneda extranjera como dólares",
            "D) Limita la contratación de personal únicamente a ciertas regiones"
        ],
        "correcta": 1,
        "escanner": {
            "IP_Origen": "Dominio de recolección de datos fraudulentos",
            "Fecha_Creacion": "Hace 4 días",
            "Patron_Fraude": "Solicitud de pago por 'kit de inicio'",
            "Reputacion": "Estafa laboral simulada"
        }
    },
    {
        "titulo": "Nivel 7",
        "perfil": "@verificacion_badge_support",
        "bio": "Obtén tu insignia de verificación azul oficial aquí en 5 minutos. https://paypai.com",
        "datos": "📍 Soporte | 📊 150 Seguidores • 800 Seguidos • 1 Publicación  ",
        "url_imagen": "https://img.magnific.com/vector-premium/icono-insignia-verificacion-azul-simbolo-marca-verificacion-marca-comprobacion-vector-estrella-circular_789916-8858.jpg?semt=ais_hybrid&w=740&q=80",
        "pregunta": "¿Cuál es el riesgo de este falso perfil de soporte?",
        "opciones": [
            "A) Cobra una tarifa económica por realizar el trámite de validación de identidad",
            "B) Carece de un historial previo de videos en el perfil de la plataforma",
            "C) Finge ser soporte técnico oficial para robar tus datos y la contraseña de tu cuenta",
            "D) Utiliza colores azules similares a los de las insignias reales de verificación"
        ],
        "correcta": 2,
        "escanner": {
            "IP_Origen": "Formulario externo no seguro",
            "Fecha_Creacion": "Hace 1 día",
            "Vector_Ataque": "Robo directo de cookies y contraseñas",
            "Reputacion": "Phishing de suplantación de soporte"
        }
    },
    {
        "titulo": "Nivel 8",
        "perfil": "@crypto_master_ganancias_vip",
        "bio": "📈 Duplica tu dinero en 24 horas con mi método infalible de inversión.",
        "datos": "📍 Dubai | 📊 89k Seguidores • 3 Seguidos • 4 Publicaciones",
        "url_imagen": "https://images.unsplash.com/photo-1621416894569-0f39ed31d247?w=150&h=150&fit=crop&crop=faces",
        "pregunta": "¿Qué patrón delata la estafa en este perfil?",
        "opciones": [
            "A) Enfoca todas sus publicaciones en la compra y venta de activos digitales",
            "B) Tiene su sede principal en una ciudad financiera internacional",
            "C) Muestra capturas de pantalla de supuestas operaciones bursátiles exitosas",
            "D) Promete ganancias exageradas, fáciles y seguras en muy poco tiempo"
        ],
        "correcta": 3,
        "escanner": {
            "IP_Origen": "Granja de bots financieros",
            "Fecha_Creacion": "Hace 2 semanas",
            "Patron_Financiero": "Esquema Ponzi / Cripto-estafa conocida",
            "Reputacion": "Alto riesgo de pérdida patrimonial"
        }
    },
    {
        "titulo": "Nivel 9",
        "perfil": "@premios_consumidor_oficial",
        "bio": "🎁 Responde nuestra encuesta rápida y llévate una tarjeta de regalo de $1000.",
        "datos": "📍 Tienda | 📊 22 Seguidores • 150 Seguidos • 2 Publicaciones",
        "url_imagen": "https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=150&h=150&fit=crop&crop=faces",
        "pregunta": "¿Cuál es la trampa detrás de estas encuestas falsas?",
        "opciones": [
            "A) Ofrecer tarjetas de regalo atractivas a cambio de robar tus datos personales y bancarios",
            "B) Realizar estudios de mercado enfocados en conocer los gustos de los consumidores",
            "C) Solicitar un registro previo obligatorio para verificar la identidad del usuario",
            "D) Utilizar marcas comerciales famosas en el diseño visual de sus publicaciones"
        ],
        "correcta": 0,
        "escanner": {
            "IP_Origen": "Servidor de recolección de leads (Phishing)",
            "Fecha_Creacion": "Hace 3 días",
            "Riesgo_Datos": "Extracción de información bancaria y personal",
            "Reputacion": "Fraude de recompensas falsas"
        }
    },
    {
        "titulo": "Nivel 10",
        "perfil": "@soporte_seguridad_net_247",
        "bio": "Aviso importante de seguridad en tu cuenta. Verifícate ahora mismo.  https://paypai.com",
        "datos": " 📊 0 Seguidores • 100 Seguidos • 0 Publicaciones",
        "url_imagen": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSiDTMLg0AxxFWqla3Byk0T7gAvoEVPrilgsfvcX8Yzag&s",
        "pregunta": "¿Qué combinación de factores confirma que es un ataque de phishing definitivo?",
        "opciones": [
            "A) Utilizar elementos gráficos oscuros en el diseño de la foto de perfil",
            "B) Emplear palabras clave relacionadas con la ciberseguridad y la protección de datos",
            "C) Crear un falso sentido de urgencia, usar un perfil vacío y un enlace externo sospechoso",
            "D) Seguir a un grupo reducido de cuentas dentro de la misma plataforma web"
        ],
        "correcta": 2,
        "escanner": {
            "IP_Origen": "Infraestructura maliciosa dedicada (C2)",
            "Fecha_Creacion": "Hace 6 horas",
            "Payload": "Script avanzado de robo de sesión y cookies",
            "Reputacion": "Crítico - Amenaza total de suplantación"
        }
    }
]

# Plantilla principal de la aplicación
# Contiene toda la interfaz HTML, CSS y JavaScript utilizada
# para mostrar el menú, los niveles, el sistema de ayuda
# el termómetro y los efectos visuales del juego
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Refugio Digital</title>
    <style>
        /*Var para el tema oscuro*/
        :root {
            --bg-color: #18181b;
            --text-color: #ffffff;
            --panel-bg: #27272a;
            --card-bg: rgba(255, 255, 255, 0.03);
            --card-border: rgba(255, 255, 255, 0.08);
            --text-muted: #a1a1aa;
            --text-sub: #d4d4d8;
            --map-bg: rgba(0, 0, 0, 0.25);
            --term-bg: #18181b;
            --term-border: #71717a;
        }
        /*Var para el tema claro*/
        [modo="claro"] {
            --bg-color: #f0f2f5;
            --text-color: #18181b;
            --panel-bg: #ffffff;
            --card-bg: rgba(0, 0, 0, 0.02);
            --card-border: rgba(0, 0, 0, 0.08);
            --text-muted: #52525b;
            --text-sub: #3f3f46;
            --map-bg: rgba(0, 0, 0, 0.04);
            --term-bg: #e4e4e7;
            --term-border: #d4d4d8;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 15px;
            height: 100vh;
            box-sizing: border-box;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            transition: background-color 0.3s ease, color 0.3s ease;
        }

        /* Contenedor interruptor modo claro/oscuro */
        .barra-superior {
            width: 100%;
            max-width: 1050px;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            margin-bottom: 10px;
            padding: 0 5px;
        }
        
        /* Contenedor interruptor modo claro/oscuro */
        .selector-tema {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 14px;
            background: var(--panel-bg);
            padding: 6px 14px;
            border-radius: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 1px solid var(--card-border);
        }
        /* Diseño y animación del boton de cambio de tema*/
        .switch {
            position: relative;
            display: inline-block;
            width: 44px;
            height: 22px;
        }
        .switch input { 
            opacity: 0;
            width: 0;
            height: 0;
        }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0; left: 0; right: 0; bottom: 0;
            background-color: #71717a;
            transition: .3s;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 3px;
            bottom: 3px;
            background-color: white;
            transition: .3s;
        }
        input:checked + .slider {
            background-color: #0072ff;
        }
        input:checked + .slider:before {
            transform: translateX(22px);
        }
        .slider.round {
            border-radius: 34px;
        }
        .slider.round:before {
            border-radius: 50%;
        }

        
        .container {
            width: 100%;
            max-width: 1050px;
            display: flex;
            gap: 20px;
            max-height: 88vh;
        }
        
        button:focus-visible, input:focus-visible, label:focus-within {
            outline: 3px solid #38bdf8 !important;
            outline-offset: 2px;
        }

        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .main-content {
            flex: 3;
            background-color: var(--panel-bg);
            color: var(--text-color);
            padding: 25px;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            overflow-y: auto;
            max-height: 85vh;
            animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        .sidebar {
            flex: 1;
            background-color: var(--panel-bg);
            color: var(--text-color);
            padding: 20px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            max-height: 85vh;
            animation: fadeInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            transition: background-color 0.3s ease, color 0.3s ease;
        }
        
        /* Animación Victoria */
        @keyframes brillo-victoria {
            0% { box-shadow: 0 0 30px rgba(74, 222, 128, 0.3); border: 2px solid rgba(74, 222, 128, 0.5); }
            50% { box-shadow: 0 0 60px rgba(74, 222, 128, 0.8); border: 2px solid rgba(74, 222, 128, 1); }
            100% { box-shadow: 0 0 30px rgba(74, 222, 128, 0.3); border: 2px solid rgba(74, 222, 128, 0.5); }
        }
        .victory-effect {
            animation: brillo-victoria 1.5s infinite;
        }
        
        /* Animación derrota */
        @keyframes sacudida-derrota {
            0% { transform: translate(1px, 1px); }
            20% { transform: translate(-3px, 0px); }
            40% { transform: translate(3px, 2px); }
            60% { transform: translate(-1px, -1px); }
            80% { transform: translate(2px, -2px); }
            100% { transform: translate(0px, 0px); }
        }
        .efecto-derrota {
            animation: sacudida-derrota 0.3s infinite;
            box-shadow: 0 0 40px rgba(248, 113, 113, 0.7) !important;
            border: 2px solid #f43f5e!important;
        }

        /* Progreso niveles */
        .mapa-progreso {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            background: var(--map-bg);
            padding: 10px 14px;
            border-radius: 12px;
            border: 1px solid var(--card-border);
        }
        .nodo {
            width: 26px;
            height: 26px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: bold;
            background: var(--card-border);
            color: var(--text-muted);
            transition: all 0.3s ease;
        }
        .nodo.completado {
            background: #10b981;
            color: #fff;
            box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
        }
        .nodo.actual {
            background: #0072ff;
            color: #fff;
            transform: scale(1.15);
            box-shadow: 0 0 12px rgba(0, 114, 255, 0.7);
        }

        h1, h2, h3 { margin-top: 0; }
        /*Diseño y animación de los botones*/
        .btn {
            background: linear-gradient(135deg, #0072ff 0%, #0052cc 100%);
            color: white;
            font-size: 15px;
            font-weight: 700;
            padding: 12px 20px;
            border-radius: 14px;
            border: none;
            width: 100%;
            cursor: pointer;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 6px 20px rgba(0, 114, 255, 0.35);
            margin-top: 10px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            box-sizing: border-box;
        }
        .btn:hover {
            transform: translateY(-2px) scale(1.01);
            background: linear-gradient(135deg, #1a82ff 0%, #0060df 100%);
        }
        .btn-secundario {
            background: #52525b !important;
            box-shadow: none !important;
        }
        .btn-sniffer {
            background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
            box-shadow: 0 6px 20px rgba(124, 58, 237, 0.35) !important;
        }
        
        /*Diseño de las tarjetas de perfiles*/
        .tarjeta-perfil {
            background-color: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }
        
        .imagen-perfil {
            width: 75px;
            height: 75px;
            border-radius: 50%;
            object-fit: cover;
            border: 2px solid var(--card-border);
        }
        
        .cuadricula-guia {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        .tarjeta-guia {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 16px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex;
            align-items: flex-start;
            gap: 14px;
        }
        .tarjeta-guia:hover {
            transform: translateY(-3px);
            background: rgba(0, 114, 255, 0.08);
            border-color: rgba(0, 114, 255, 0.4);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
        }
        .icono-guia {
            font-size: 32px;
            background: rgba(0, 114, 255, 0.15);
            width: 52px;
            height: 52px;
            min-width: 52px;
            border-radius: 14px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 1px solid rgba(0, 114, 255, 0.3);
        }
        .tarjeta-guia h4 {
            margin: 0 0 6px 0;
            font-size: 16px;
            color: #38bdf8;
        }
        .tarjeta-guia p {
            margin: 0;
            font-size: 14px;
            color: var(--text-sub);
            line-height: 1.5;
        }
        
        /*Opciones de respuesta*/
        .radio-label {
            display: block;
            background: var(--card-bg);
            padding: 10px 14px;
            border-radius: 10px;
            margin-bottom: 6px;
            cursor: pointer;
            border: 1px solid var(--card-border);
            font-size: 14px;
            transition: all 0.2s ease-in-out;
        }
        .radio-label:hover {
            background: rgba(0, 114, 255, 0.06);
            transform: translateX(4px);
            border-color: rgba(0, 114, 255, 0.3);
        }
        input[type="radio"] {
            margin-right: 10px;
            transform: scale(1.1);
        }
        .sniffer-box {
            background-color: #2e1065;
            border: 1px solid #7c3aed;
            padding: 15px;
            border-radius: 12px;
            margin-bottom: 15px;
            color: #ffffff;
        }
        
        .term-bar-container {
            background-color: var(--term-bg);
            width: 32px;
            height: 190px;
            border-radius: 14px;
            margin: 8px auto;
            position: relative;
            border: 2px solid var(--term-border);
            overflow: hidden;
        }
        .term-fill {
            position: absolute;
            bottom: 0;
            width: 100%;
            border-radius: 10px;
            transition: height 0.4s ease;
        }
        
        .emoji {
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 14px;
            padding: 10px;
            margin-top: 6px;
        }

        /* Boton para asistente IA */
        .gemini-fab {
            position: fixed;
            bottom: 25px;
            right: 25px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background-color: #e0e0e0;
            border: 2px solid #ccc;
            color: #333;
            font-size: 24px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            transition: transform 0.2s, background-color 0.2s;
            z-index: 1000;
        }
        .gemini-fab:hover {
            background-color: #d0d0d0;
            transform: scale(1.05);
        }
    </style>
    
    <!-- Efectos de sonido corregidos con desbloqueo automático -->
    <script>
        let audioCtx = null;

        function obtenerAudioContext() {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            if (audioCtx.state === 'suspended') {
                audioCtx.resume();
            }
            return audioCtx;
        }

        function reproducirSonido(tipo) {
            try {
                const contextoAudio = obtenerAudioContext();
                
                if (tipo === 'click') {
                    const oscilador = contextoAudio.createOscillator();
                    const ganancia = contextoAudio.createGain();
                    oscilador.connect(ganancia);
                    ganancia.connect(contextoAudio.destination);
                    oscilador.frequency.setValueAtTime(440, contextoAudio.currentTime);
                    ganancia.gain.setValueAtTime(0.05, contextoAudio.currentTime);
                    ganancia.gain.exponentialRampToValueAtTime(0.001, contextoAudio.currentTime + 0.1);
                    oscilador.start(); 
                    oscilador.stop(contextoAudio.currentTime + 0.1);
                } 
                else if (tipo === 'hot') {
                    [523.25, 659.25, 783.99, 1046.50].forEach((frecuencia, indice) => {
                        const oscilador = contextoAudio.createOscillator();
                        const ganancia = contextoAudio.createGain();
                        oscilador.type = 'sine';
                        oscilador.frequency.setValueAtTime(frecuencia, contextoAudio.currentTime + indice * 0.07);
                        ganancia.gain.setValueAtTime(0.05, contextoAudio.currentTime + indice * 0.07);
                        ganancia.gain.exponentialRampToValueAtTime(0.001, contextoAudio.currentTime + indice * 0.07 + 0.25);
                        oscilador.connect(ganancia);
                        ganancia.connect(contextoAudio.destination);
                        oscilador.start(contextoAudio.currentTime + indice * 0.07);
                        oscilador.stop(contextoAudio.currentTime + indice * 0.07 + 0.25);
                    });
                } 
                else if (tipo === 'cold') {
                    const oscilador = contextoAudio.createOscillator();
                    const ganancia = contextoAudio.createGain();
                    oscilador.type = 'triangle';
                    oscilador.frequency.setValueAtTime(350, contextoAudio.currentTime);
                    oscilador.frequency.exponentialRampToValueAtTime(100, contextoAudio.currentTime + 0.35);
                    ganancia.gain.setValueAtTime(0.08, contextoAudio.currentTime);
                    ganancia.gain.exponentialRampToValueAtTime(0.001, contextoAudio.currentTime + 0.35);
                    oscilador.connect(ganancia);
                    ganancia.connect(contextoAudio.destination);
                    oscilador.start();
                    oscilador.stop(contextoAudio.currentTime + 0.35);
                } 
                else if (tipo === 'bell') {
                    const oscilador = contextoAudio.createOscillator();
                    const ganancia = contextoAudio.createGain();
                    oscilador.type = 'sine';
                    oscilador.frequency.setValueAtTime(880, contextoAudio.currentTime);
                    ganancia.gain.setValueAtTime(0.08, contextoAudio.currentTime);
                    ganancia.gain.exponentialRampToValueAtTime(0.0001, contextoAudio.currentTime + 1.0);
                    oscilador.connect(ganancia);
                    ganancia.connect(contextoAudio.destination);
                    oscilador.start();
                    oscilador.stop(contextoAudio.currentTime + 1.0);
                }
            } catch (error) {
                console.error("Error al reproducir sonido:", error);
            }
        }

        window.addEventListener('click', () => {
            obtenerAudioContext();
        }, { once: true });

        window.addEventListener('DOMContentLoaded', () => {
            const sonidoServidor = "{{ efecto_sonido | default('') }}";
            if (sonidoServidor) {
                setTimeout(() => {
                    reproducirSonido(sonidoServidor);
                }, 100);
            }
        });
    </script>
</head>
<body modo="{{ tema }}">
    
    <!-- Tema claro/oscuro  -->
    
    <div class="barra-superior">
        <div class="selector-tema">
            <span>☀️</span>
            <form action="/cambiar-tema" method="POST" style="margin: 0; display: flex; align-items: center;">
                <label class="switch">
                    <input type="checkbox" name="interruptor_tema" onchange="this.form.submit()" {% if tema == 'oscuro' %}checked{% endif %}>
                    <span class="slider round"></span>
                </label>
            </form>
            <span>🌙</span>
        </div>
    </div>

    <!-- Pantalla principal  -->
    <div class="container">
        {% if fase == 'inicio' %}
            <div class="main-content" style="flex: 1; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; padding: 40px; background: radial-gradient(circle at center, rgba(56, 189, 248, 0.05) 0%, transparent 70%);">
                
                <!-- Tarjeta contenedora principal con efecto elegante -->
                <div style="background: var(--card-bg, rgba(255, 255, 255, 0.03)); border: 1px solid var(--border-color, rgba(56, 189, 248, 0.2)); padding: 50px 40px; border-radius: 24px; box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15); max-width: 600px; width: 100%; backdrop-filter: blur(10px);">
                    
                    <!-- Icono con animación de brillo o flotación sutil -->
                    <div style="font-size: 72px; margin-bottom: 20px; filter: drop-shadow(0 4px 12px rgba(56, 189, 248, 0.3));" aria-hidden="true">🛡️</div>
                    
                    <!-- Título principal -->
                    <h1 style="font-size: 38px; font-weight: 800; margin-bottom: 12px; color: #38bdf8; letter-spacing: -0.5px;">Refugio Digital</h1>
                    
                    <!-- Descripción clara -->
                    <p style="color: var(--text-sub); font-size: 16px; line-height: 1.7; margin-bottom: 35px;">
                        Entrena tus habilidades en ciberseguridad, aprende a identificar fraudes digitales, perfiles falsos y ataques de phishing de forma interactiva y segura.
                    </p>
                    
                    <!-- Boton de acción con estilo mejorado -->
                    <form action="/ir-menu" method="POST">
                        <button type="submit" class="btn" style="font-size: 18px; font-weight: 600; padding: 16px 36px; border-radius: 12px; background: linear-gradient(135deg, #38bdf8 0%, #0284c7 100%); color: white; border: none; cursor: pointer; box-shadow: 0 8px 20px rgba(56, 189, 248, 0.35); transition: all 0.3s ease;" 
                            onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 12px 24px rgba(56, 189, 248, 0.5)';" 
                            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 8px 20px rgba(56, 189, 248, 0.35)';"
                            onclick="reproducirSonido('click')">
                            Empieza a entrenar
                        </button>
                    </form>
                    
                </div>
            </div>
        {% elif fase == 'menu' %}
            <div class="main-content" style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 14px; margin-bottom: 14px;">
                    <span style="font-size: 38px;" aria-hidden="true"></span>
                    <div>
                        <h1 style="font-size: 24px; margin: 0;">🛡️ REFUGIO DIGITAL: Guía de Amenazas</h1>
                    </div>
                </div>
                
                <p style="color: var(--text-sub); font-size: 15px; line-height: 1.6; margin-bottom: 15px;">
                    Este es un simulador interactivo. Para poder pasar los niveles analiza con cuidado los escenarios de suplantación de identidad y estafas en redes sociales que aprenderás a detectar:
                </p>

                <div class="cuadricula-guia">
                    <div class="tarjeta-guia">
                        <div class="icono-guia" aria-hidden="true">🤖</div>
                        <div>
                            <h4 style= "color : #00A2E8">1. Bots e Influencers Fantasmas</h4>
                            <p>Son perfiles con miles de seguidores pero que no tienen publicaciones o han sido creado hace pocos días.</p>
                        </div>
                    </div>

                    <div class="tarjeta-guia">
                        <div class="icono-guia" aria-hidden="true">🏦</div>
                        <div>
                            <h4 style="color: #f43f5e;">2. Falsos Soporte / Bancarios</h4>
                            <p>Son cuentas que simulan ser organizaciones oficiales para robar tus credenciales.</p>
                        </div>
                    </div>

                    <div class="tarjeta-guia">
                        <div class="icono-guia" aria-hidden="true">🎁</div>
                        <div>
                            <h4 style="color: #34d399;">3. Sorteos y Premios Gancho</h4>
                            <p>Utilizan ganchos (como dinero y premios) que piden datos personales.</p>
                        </div>
                    </div>

                    <div class="tarjeta-guia">
                        <div class="icono-guia" aria-hidden="true">👤</div>
                        <div>
                            <h4 style="color: #fbbf24;">4. Amigos Clonados</h4>
                            <p>Son estafadores que roban la foto y nombre de algún conocido para pedir dinero o favores.</p>
                        </div>
                    </div>

                    <div class="tarjeta-guia" style="grid-column: span 2;">
                        <div class="icono-guia" aria-hidden="true">🚨</div>
                        <div>
                            <h4 style="color: #a78bfa;">5. Noticias Alarmistas y Empleos Falsos</h4>
                            <p>Son ofertas exageradas o noticias de pánico que estan diseñadas para hacer caer enlaces trampa y malware.</p>
                        </div>
                    </div>
                </div>

                <h3 style="font-size: 18px; margin: 25px 0 12px 0; border-bottom: 2px solid var(--card-border); padding-bottom: 6px;">¿Cómo Jugar?</h3>
                <div class="cuadricula-guia" style="margin-bottom: 20px;">
                    <div class="tarjeta-guia">
                        <div class="icono-guia" aria-hidden="true">🔍</div>
                        <div>
                            <h4 style="color: #38bdf8;">1. Analiza el Perfil</h4>
                            <p>Revisa con atención la foto, biografía y datos de cada nivel para detectar anomalías.</p>
                        </div>
                    </div>

                    <div class="tarjeta-guia">
                        <div class="icono-guia" aria-hidden="true">✅</div>
                        <div>
                            <h4 style="color: #4ade80;">2. Elige una Opción</h4>
                            <p>Selecciona una respuesta (A, B, C o D) .</p>
                        </div>
                    </div>

                    <div class="tarjeta-guia">
                        <div class="icono-guia" aria-hidden="true">🌡️</div>
                        <div>
                            <h4 style="color: #fb923c;">3. Cuida la Temperatura</h4>
                            <p>Elige la opción correcta para aumentar la temperatura y llegar a 100°C (Victoria). No te equivoques y evita llegar a 0°C (Derrota).</p>
                        </div>
                    </div>

                    <div class="tarjeta-guia">
                        <div class="icono-guia" aria-hidden="true">📡</div>
                        <div>
                            <h4 style="color: #c084fc;">4. Usa el Escáner Sniffer</h4>
                            <p>Si no sabes la respuesta activa el modo ayuda (Botón Sniffer) para revelar pistas del servidor y la respuesta.</p>
                        </div>
                    </div>
                </div>

                <form action="/comenzar" method="POST">
                    <button type="submit" class="btn" style="font-size: 16px; padding: 14px;" onclick="reproducirSonido('click')">Comienza a jugar</button>
                </form>
            </div>
        {% else %}
            <div class="main-content {% if temperatura >= 100 %}victory-effect{% elif temperatura <= 0 %}efecto-derrota{% endif %}">
                {% if nivel <= 10 and temperatura > 0 and temperatura < 100 %}
                <div class="mapa-progreso" aria-label="Mapa de progreso de niveles">
                    {% for i in range(1, 11) %}
                        <div class="nodo {% if i < nivel %}completado{% elif i == nivel %}actual{% endif %}">
                            {{ i }}
                        </div>
                    {% endfor %}
                </div>
                {% endif %}

                {% if temperatura >= 100 %}
                    <h1 style="color: #4ade80; text-align: center; margin-top: 40px;">🎉 ¡VICTORIA! 🎉</h1>
                    <p style="font-size: 18px; text-align: center; color: var(--text-sub);">El termómetro llegó al 100%. ¡Demostraste que eres un experto detectando suplantaciones y amenazas digitales! Sigue practicando para que seas aún mejor</p>
                    <form action="/reiniciar" method="POST"><button type="submit" class="btn" style="margin-top: 30px;" onclick="reproducirSonido('click')">🔄 Jugar de nuevo</button></form>
                {% elif temperatura <= 0 %}
                    <h1 style="color: #f87171; text-align: center; margin-top: 40px;">⚠️ ¡DERROTA! ⚠️</h1>
                    <p style="font-size: 18px; text-align: center; color: var(--text-sub);">El termómetro llegó al 0%. ¡Las estafas lograron engañarte! Necesitas volver a estudiar</p>
                    <form action="/reiniciar" method="POST"><button type="submit" class="btn" style="margin-top: 30px; background: linear-gradient(135deg, #ef4444 0%, #b91c1c 100%);" onclick="reproducirSonido('click')">🔄 Intentar de nuevo</button></form>
                {% elif nivel > 10 %}
                    <h1 style="color: #4ade80; text-align: center; margin-top: 40px;">🏆 ¡TERMINASTE LOS NIVELES! 🏆</h1>
                    <p style="font-size: 18px; text-align: center; color: var(--text-sub);">Pasaste los niveles con {{ temperatura }}°C. No perdiste ni ganaste, intenta de nuevo para obtener la Victoria</p>
                    <form action="/reiniciar" method="POST"><button type="submit" class="btn" style="margin-top: 30px;" onclick="reproducirSonido('click')">🔄 Volver a Jugar</button></form>
                {% else %}
                    <h2 style="font-size: 20px; margin-bottom: 5px;">{{ nivel_actual.titulo }} <span style="font-size: 14px; color: var(--text-muted);">(Nivel {{ nivel }}/10)</span></h2>
                    <p style="color: var(--text-muted); margin-bottom: 12px; font-size: 14px;">Analiza este perfil y descubre que está mal:</p>

                    <div class="tarjeta-perfil">
                        <img src="{{ nivel_actual.url_imagen }}" class="imagen-perfil" alt="Conectate a internet para ver la foto">
                        <div>
                            <h3 style="margin-bottom: 4px; font-size: 16px;">{{ nivel_actual.perfil }}</h3>
                            <p style="margin: 0 0 4px 0; color: var(--text-sub); font-size: 14px;">{{ nivel_actual.bio }}</p>
                            <p style="margin: 0; color: var(--text-muted); font-size: 12px;">{{ nivel_actual.datos }}</p>
                        </div>
                    </div>

                    {% if ayuda_activa %}
                        <div class="sniffer-box" aria-live="polite">
                            <h3 style="color: #c084fc; margin-bottom: 8px; font-size: 15px;">Modo Ayuda (Escáner Sniffer)</h3>
                            {% for clave, valor in nivel_actual.escanner.items() %}
                                <p style="margin: 3px 0; font-size: 13px; color: #e9d5ff;">• <strong>{{ clave.replace('_', ' ').title() }}:</strong> {{ valor }}</p>
                            {% endfor %}
                            <p style="margin-top: 10px; font-size: 14px; color: #4ade80;"><strong>💡 Respuesta Correcta:</strong>{{ nivel_actual.opciones[nivel_actual.correcta] }}</p>
                        </div>
                        <form action="/siguiente" method="POST">
                            <button type="submit" class="btn" style="background: linear-gradient(135deg, #9333ea 0%, #7e22ce 100%);" onclick="reproducirSonido('click')">➡️ Avanzar al siguiente nivel</button>
                        </form>
                    {% else %}
                        <form action="/sniffer" method="POST" style="margin-bottom: 12px;">
                            <button type="submit" class="btn btn-sniffer" onclick="reproducirSonido('click')"> Ayuda (Escáner Sniffer)</button>
                        </form>

                        <p style="font-size: 15px; font-weight: bold; margin-bottom: 10px;">{{ nivel_actual.pregunta }}</p>

                        <form action="/responder" method="POST">
                            {% for indice, opcion in enumerate(nivel_actual.opciones) %}
                                <label class="radio-label">
                                    <input type="radio" name="opcion" value="{{ indice }}" required onclick="reproducirSonido('click')">
                                    {{ opcion }}
                                </label>
                            {% endfor %}
                            <button type="submit" class="btn" onclick="reproducirSonido('click')">Comprueba tu respuesta y continúa</button>
                        </form>
                    {% endif %}
                {% endif %}
            </div>

            <!--Barra del termometro-->
            <div class="sidebar {% if temperatura >= 100 %}victory-effect{% elif temperatura <= 0 %}efecto-derrota{% endif %}" aria-live="polite">
                <div>
                    <h3 style="font-size: 14px; margin-bottom: 2px;">Temperatura</h3>
                    <div style="font-size: 17px; font-weight: bold; color: {% if temperatura > 50 %}#ff944d{% elif temperatura < 50 %}#00d2ff{% else %}#10B981{% endif %};">
                        {{ temperatura }}°C
                    </div>

                    <div class="term-bar-container" aria-label="Termómetro de seguridad del sistema">
                        <div class="term-fill" style="height: {{ (temperatura / 100) * 100 }}%; background-color: {% if temperatura > 50 %}#ff4d4d{% elif temperatura < 50 %}#00d2ff{% else %}#10B981{% endif %};"></div>
                    </div>

                    
                </div>

                <div class="emoji">
                    <div style="font-size: 52px; line-height: 1.1;" aria-hidden="true">{{ emoji_mascota }}</div>
                    <div style="font-size: 12px; font-weight: bold; color: var(--text-sub); margin-top: 4px;">{{ mensaje_mascota }}</div>
                </div>

                <form action="/menu" method="POST" style="margin-top: 2px;">
                    <button type="submit" class="btn btn-secundario" style="font-size: 12px; padding: 6px;" onclick="reproducirSonido('click')">⬅️ Vuelve a la guía</button>
                </form>
            </div>
        {% endif %}
    </div>

    <!-- Boton api Gemini -->
    
    <button id="open-gemini-btn" class="gemini-fab" title="Abrir Asistente Gemini">
        <span>?</span>
    </button>

    <!--Boton con la ruta del flask-->
    <script>
        document.getElementById('open-gemini-btn').addEventListener('click', async () => {
            try {
                const respuesta = await fetch('/launch-gemini', {
                    method: 'POST'
                });
                const datos = await respuesta.json();
                if (!respuesta.ok) {
                    console.error("No se pudo abrir la ventana:", datos.message);
                } else {
                    console.log("Asistente lanzado correctamente.");
                }
            } catch (error) {
                console.error("Error de conexión con el servidor Flask:", error);
            }
        });
    </script>
</body>
</html>
"""

# Ruta principal del sistema
# Inicializa la sesión del jugador, recupera el estado actual
# de la partida y envía la información necesaria a la interfaz
@app.route('/')
def inicio():
    if 'nivel' not in session:
        session['nivel'] = 1
        session['temperatura'] = 50
        session['fase'] = 'inicio'
        session['ayuda_usada'] = {}
        session['tema'] = 'oscuro'

    indice_nivel = session['nivel'] - 1
    nivel_actual = NIVELES[indice_nivel] if 0 <= indice_nivel < len(NIVELES) else None
    
    diccionario_ayuda = session.get('ayuda_usada', {})
    ayuda_activa = diccionario_ayuda.get(str(session['nivel']), False)
    
    efecto_sonido = session.pop('efecto_sonido', None)
    temperatura_actual = session.get('temperatura', 50)
    tema_actual = session.get('tema', 'oscuro')

    # Selecciona la mascota y el mensaje visual que verá el usuario
    # según los resultados obtenidos durante la partida
    if temperatura_actual >= 100:
        emoji_mascota = "🥳"
        mensaje_mascota = "Buen trabajo "
    elif temperatura_actual <= 0:
        emoji_mascota = "💀"
        mensaje_mascota = "Oh no"
    elif efecto_sonido == 'hot':
        emoji_mascota = "😎"
        mensaje_mascota = "Tu puedes"
    elif efecto_sonido == 'cold':
        emoji_mascota = "🥶"
        mensaje_mascota = " Ups "
    elif efecto_sonido == 'bell':
        emoji_mascota = "🧐"
        mensaje_mascota = "Ayuda Activada"
    else:
        emoji_mascota = "🤖"
        mensaje_mascota = "Empieza a jugar"

    return render_template_string(
        HTML_TEMPLATE,
        fase=session['fase'],
        nivel=session['nivel'],
        temperatura=temperatura_actual,
        nivel_actual=nivel_actual,
        ayuda_activa=ayuda_activa,
        efecto_sonido=efecto_sonido,
        emoji_mascota=emoji_mascota,
        mensaje_mascota=mensaje_mascota,
        tema=tema_actual,
        enumerate=enumerate
    )
    
# Inicia una nueva partida
# Reinicia nivel, temperatura y ayudas utilizadas
@app.route('/comenzar', methods=['POST'])
def comenzar():
    session['fase'] = 'juego'
    session['nivel'] = 1
    session['temperatura'] = 50
    session['ayuda_usada'] = {}
    return redirect(url_for('inicio'))

# Pasa de la pantalla de inicio a la guía/menú principal
@app.route('/ir-menu', methods=['POST'])
def ir_menu():
    session['fase'] = 'menu'
    return redirect(url_for('inicio'))

# Regresa al menú principal de la aplicación
@app.route('/menu', methods=['POST'])
def volver_menu():
    session['fase'] = 'menu'
    return redirect(url_for('inicio'))

# Permite alternar entre modo oscuro y modo claro
# La preferencia se almacena dentro de la sesión
@app.route('/cambiar-tema', methods=['POST'])
def cambiar_tema():
    es_oscuro = 'interruptor_tema' in request.form
    session['tema'] = 'oscuro' if es_oscuro else 'claro'
    return redirect(url_for('inicio'))

# Activa el modo ayuda para el nivel actual
# Muestra pistas adicionales mediante el escáner
@app.route('/sniffer', methods=['POST'])
def activar_escanner():
    diccionario_ayuda = session.get('ayuda_usada', {})
    diccionario_ayuda[str(session['nivel'])] = True
    session['ayuda_usada'] = diccionario_ayuda
    session.modified = True
    session['efecto_sonido'] = 'bell'
    return redirect(url_for('inicio'))

# Evalúa la respuesta seleccionada por el jugador
# Si acierta aumenta la temperatura del sistema
# si falla la disminuye. También avanza al nivel siguiente
@app.route('/responder', methods=['POST'])
def responder():
    try:
        seleccion = int(request.form.get('opcion', 0))
    except ValueError:
        seleccion = 0

    indice_nivel = session['nivel'] - 1
    nivel_actual = NIVELES[indice_nivel]
    correcta = nivel_actual['correcta']

    if seleccion == correcta:
        session['temperatura'] = min(100, session['temperatura'] + 10)
        session['efecto_sonido'] = 'hot'
    else:
        session['temperatura'] = max(0, session['temperatura'] - 10)
        session['efecto_sonido'] = 'cold'

    session['nivel'] += 1
    return redirect(url_for('inicio'))

# Permite continuar al siguiente nivel después
# de utilizar el modo ayuda
@app.route('/siguiente', methods=['POST'])
def siguiente_ayuda():
    session['nivel'] += 1
    return redirect(url_for('inicio'))

# Restablece completamente los datos de la partida
# y devuelve al jugador al menú principal
@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    session['nivel'] = 1
    session['temperatura'] = 50
    session['fase'] = 'inicio'
    session['ayuda_usada'] = {}
    return redirect(url_for('inicio'))

# Ejecuta el asistente externo basado en Gemini
# utilizando un proceso independiente del servidor Flask
@app.route('/launch-gemini', methods=['POST'])
def lanzar_gemini():
    try:
        subprocess.Popen([sys.executable, "consulta_gemini.py"])
        return jsonify({'status': 'success', 'message': 'Ventana abierta con éxito'})
    except Exception as error_ejecucion:
        return jsonify({'status': 'error', 'message': str(error_ejecucion)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)