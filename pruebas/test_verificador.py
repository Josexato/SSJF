"""
Pruebas del verificador de referencia con vectores reales generados por Navaja.

    pip install cryptography
    python3 -m unittest discover -s pruebas -v

Código de salida esperado: 0 verificada, 1 inválida, 2 válida con advertencias.
"""
import os
import subprocess
import sys
import unittest

AQUI = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(AQUI, "vectores")
SCRIPT = os.path.join(AQUI, "..", "verificar_ssjf.py")


def correr(*args):
    p = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


class Verificador(unittest.TestCase):
    clave = os.path.join(V, "clave.json")

    def pdf(self, nombre, esperado, texto=None):
        rc, out = correr(os.path.join(V, nombre), "--clave", self.clave)
        self.assertEqual(rc, esperado, out)
        if texto:
            self.assertIn(texto, out)

    def test_valida(self):
        self.pdf("valida.pdf", 0, "firma del sello")

    def test_qr_alterado(self):
        self.pdf("qr_alterado.pdf", 1)

    def test_firma_del_sello_alterada(self):
        self.pdf("firma_sello_alterada.pdf", 1)

    def test_qr_reutilizado_con_otro_sello(self):
        # Mismo QR legítimo, otra apariencia/contenido y la firma del sello copiada.
        self.pdf("sello_de_otro_pdf.pdf", 1)

    def test_firma_del_sello_quitada(self):
        # El QR (firmado) lleva r=2: quitar seal_sig no degrada la firma a 1.0.
        self.pdf("sello_quitado.pdf", 1, "falta la firma del sello")

    def test_cambio_posterior_es_advertencia(self):
        self.pdf("cambio_posterior.pdf", 2, "DESPUÉS")

    def test_formato_1_0_es_advertencia(self):
        rc, out = correr(os.path.join(V, "formato_1_0.pdf"))
        self.assertEqual(rc, 2, out)
        self.assertIn("formato antiguo", out)

    def test_historial(self):
        self.assertEqual(correr("--historial", os.path.join(V, "historial.jsonl"))[0], 0)
        self.assertEqual(correr("--historial", os.path.join(V, "historial_alterado.jsonl"))[0], 1)


if __name__ == "__main__":
    unittest.main()
