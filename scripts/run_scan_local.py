import sys
import os
import json

# Agregamos la carpeta lambda al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lambda')))

import handler  # El módulo de Lambda

if __name__ == '__main__':
    print("🔍 Ejecutando CostKiller en modo local...\n")
    result = handler.lambda_handler({}, {})

    report_data = json.loads(result['body'])

    output_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'cost-report.json')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"✅ Reporte generado: {output_path}")
    print(f"💸 Recursos ociosos detectados: {len(report_data['unused_resources'])}")
