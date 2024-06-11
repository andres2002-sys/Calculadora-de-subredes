from flask import Flask, render_template, request, jsonify
import ipaddress

app = Flask(__name__)

def obtener_clase(ip):
    octeto = int(ip.split('.')[0])
    if 0 <= octeto <= 127:
        return 'A', 8
    elif 128 <= octeto <= 191:
        return 'B', 16
    elif 192 <= octeto <= 223:
        return 'C', 24
    else:
        return None, None

def mascara_binario(mascara):
    return ''.join(f'{int(octeto):08b}' for octeto in mascara.split('.'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calcular_subredes', methods=['POST'])
def calcular_subredes():
    try:
        ip_str = request.form['ip']
        num_subredes = int(request.form['num_subredes'])

        ip = ipaddress.IPv4Address(ip_str)
        clase, prefixlen = obtener_clase(ip_str)
        if clase is None:
            raise ValueError("Dirección IP fuera de rango de Clase A, B o C.")

        if num_subredes <= 0:
            raise ValueError("El número de subredes debe ser mayor que cero.")

        network = ipaddress.IPv4Network(f"{ip_str}/{prefixlen}", strict=False)
        new_prefix = prefixlen + (num_subredes - 1).bit_length()

        if new_prefix > 30:
            raise ValueError("El número de subredes es demasiado grande para esta clase de red.")

        subredes = list(network.subnets(new_prefix=new_prefix))[:num_subredes]

        resultados = []
        for i, subnet in enumerate(subredes):
            num_hosts = subnet.num_addresses - 2
            mascara_bin = mascara_binario(str(subnet.netmask))
            resultados.append({
                "subred": f"Subred {i + 1}",
                "ip_inicial": str(subnet.network_address),
                "ip_final": str(subnet.broadcast_address),
                "mascara": str(subnet.netmask),
                "mascara_binario": mascara_bin,
                "num_hosts": num_hosts,
                "clase": clase
            })

        return jsonify(resultados)
    except ValueError as e:
        return jsonify({"error": str(e)})

@app.route('/identificar_red', methods=['POST'])
def identificar_red():
    try:
        subred = request.form['subred']
        cidr = int(request.form['cidr'])

        objeto_subred = ipaddress.ip_network(f"{subred}/{cidr}", strict=False)
        red = str(objeto_subred.network_address)
        mascara_decimal = str(objeto_subred.netmask)
        mascara_bin = mascara_binario(mascara_decimal)
        num_hosts = objeto_subred.num_addresses - 2

        clase, _ = obtener_clase(str(objeto_subred.network_address))

        resultados = [{
            "red": red,
            "cidr": cidr,
            "ip_inicial": str(objeto_subred.network_address),
            "ip_final": str(objeto_subred.broadcast_address),
            "mascara_decimal": mascara_decimal,
            "mascara_binario": mascara_bin,
            "num_hosts": num_hosts,
            "clase": clase
        }]

        return jsonify(resultados)
    except ValueError as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
