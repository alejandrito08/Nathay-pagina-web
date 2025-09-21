from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///citas.db'
db = SQLAlchemy(app)

# MODELO DE CITA
class Cita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100))
    dia = db.Column(db.String(20))
    hora = db.Column(db.String(10))

# PANEL DE ADMINISTRACIÓN
admin = Admin(app, name='Panel de Citas', template_mode='bootstrap4')
admin.add_view(ModelView(Cita, db.session))

# INICIALIZAR BASE DE DATOS
with app.app_context():
    db.create_all()

usuarios = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    nombre = data.get("nombre", "").strip().lower()
    mensaje = data.get("mensaje", "").strip().lower()

    if nombre not in usuarios:
        usuarios[nombre] = {"estado": "inicio", "dia": None, "hora": None}

    estado = usuarios[nombre]["estado"]

    # Paso 1: Saludo inicial
    if estado == "inicio":
        usuarios[nombre]["estado"] = "preguntar_dia"
        return jsonify({"respuesta": f"¡Hola {nombre.capitalize()}! 😊 Qué gusto saludarte. ¿Qué día te viene bien para agendar tu cita?"})

    # Paso 2: Preguntar día
    elif estado == "preguntar_dia":
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado"]
        for d in dias_semana:
            if d in mensaje:
                usuarios[nombre]["dia"] = d.capitalize()
                usuarios[nombre]["estado"] = "preguntar_hora"
                return jsonify({"respuesta": f"Perfecto, el {d}. ¿A qué hora te gustaría? (Ejemplo: 15:30)"})
        return jsonify({"respuesta": "Hmm... no entendí el día 😅. ¿Podrías decirme algo como 'martes' o 'viernes'?"})

    # Paso 3: Preguntar hora
    elif estado == "preguntar_hora":
        hora_match = re.search(r"\b(\d{1,2}:\d{2})\b", mensaje)
        if hora_match:
            hora = hora_match.group(1)
            dia = usuarios[nombre]["dia"]
            cita_existente = Cita.query.filter_by(dia=dia, hora=hora).first()
            if cita_existente:
                return jsonify({"respuesta": f"Uy, el {dia} a las {hora} ya está ocupado 😔. ¿Quieres intentar otra hora?"})
            nueva_cita = Cita(nombre=nombre.capitalize(), dia=dia, hora=hora)
            db.session.add(nueva_cita)
            db.session.commit()
            usuarios[nombre]["estado"] = "completo"
            return jsonify({"respuesta": f"¡Listo! Tu cita está confirmada para el {dia} a las {hora} 🗓️. Si necesitas cambiarla, solo dímelo."})
        return jsonify({"respuesta": "No entendí la hora 😅. ¿Podrías escribirla en formato HH:MM? (Ejemplo: 16:00)"})

    # Paso 4: Conversación post-agenda
    else:
        return jsonify({"respuesta": f"Ya tienes tu cita agendada, {nombre.capitalize()} 😊. ¿Quieres modificarla o agendar otra?"})

@app.route("/disponibilidad/<dia>", methods=["GET"])
def disponibilidad_por_dia(dia):
    citas_dia = Cita.query.filter(Cita.dia.ilike(dia)).all()
    horas_ocupadas = [cita.hora for cita in citas_dia]
    return jsonify(horas_ocupadas)

@app.route("/disponibilidad", methods=["GET"])
def disponibilidad():
    todas = Cita.query.all()
    return jsonify([{"nombre": c.nombre, "dia": c.dia, "hora": c.hora} for c in todas])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)




