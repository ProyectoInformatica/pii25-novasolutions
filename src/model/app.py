from flask import Flask, request, jsonify
from src.model.basedatos import BaseDatos

app = Flask(__name__)
db = BaseDatos()


@app.route("/ping")
def ping():
    return "pong", 200


@app.route("/registros", methods=["POST"])
def insertar_registro():
    data = request.get_json(silent=True)  # silent=True evita excepcion si el body no es JSON

    if not data:
        print("[Flask] ERROR: body vacio o no es JSON valido")
        return jsonify({"error": "Body no es JSON o esta vacio"}), 400

    if "id_sensor" not in data or "medida" not in data:
        print(f"[Flask] ERROR: faltan campos — recibido: {data}")
        return jsonify({"error": "Faltan campos id_sensor o medida"}), 400

    print(f"[Flask] INSERT → id_sensor={data['id_sensor']}  medida={data['medida']}")

    conexion = db.conectar()
    if not conexion:
        return jsonify({"error": "DB no disponible"}), 503
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "INSERT INTO registros (medida, id_sensor) VALUES (%s, %s)",
            (data["medida"], data["id_sensor"])
        )
        conexion.commit()
        print("[Flask] INSERT OK")
        return jsonify({"ok": True}), 201
    except Exception as e:
        print(f"[Flask] ERROR SQL: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conexion.close()


@app.route("/actuadores/<int:id_sensor>", methods=["GET"])
def estado_actuadores(id_sensor):
    print(f"[Flask] GET actuadores → id_sensor={id_sensor}")
    conexion = db.conectar()
    if not conexion:
        return jsonify([]), 503
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nombre, tipo, estado_actual FROM actuador "
            "WHERE id_sensor_vinculado = %s AND activo = 1",
            (id_sensor,)
        )
        resultado = cursor.fetchall()
        print(f"[Flask] Actuadores encontrados: {resultado}")
        return jsonify(resultado)
    except Exception as e:
        print(f"[Flask] ERROR SQL actuadores: {e}")
        return jsonify([]), 500
    finally:
        conexion.close()


@app.route("/actuadores/<int:id_actuador>/estado", methods=["PUT"])
def actualizar_actuador(id_actuador):
    data = request.get_json(silent=True)
    if not data or "estado" not in data:
        return jsonify({"error": "Falta campo estado"}), 400

    conexion = db.conectar()
    if not conexion:
        return jsonify({"error": "DB no disponible"}), 503
    try:
        cursor = conexion.cursor()
        cursor.execute(
            "UPDATE actuador SET estado_actual = %s WHERE id = %s",
            (1 if data["estado"] else 0, id_actuador)
        )
        conexion.commit()
        print(f"[Flask] UPDATE actuador id={id_actuador} estado={data['estado']}")
        return jsonify({"ok": True})
    except Exception as e:
        print(f"[Flask] ERROR SQL update: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        conexion.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)