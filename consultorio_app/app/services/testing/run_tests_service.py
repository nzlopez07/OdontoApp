import threading
import subprocess
import logging
import os
import sys


class RunTestsService:
    """
    Servicio para ejecutar la suite de tests y volcar los resultados en logs.

    Reglas:
    - No bloquea la petición HTTP: corre en un hilo en background.
    - Captura stdout/stderr de pytest y los escribe línea a línea en logs/app.log.
    - Usa el intérprete actual para garantizar el mismo entorno (paquetes/venv).
    """

    @staticmethod
    def ejecutar_todos():
        logger = logging.getLogger('app.services.testing')
        logger.info('⏱️ Iniciando ejecución de tests...')

        thread = threading.Thread(target=RunTestsService._run_pytest, daemon=True)
        thread.start()

        return 'Test run started'

    @staticmethod
    def _run_pytest():
        logger = logging.getLogger('app.services.testing')

        try:
            # Directorio donde viven los tests
            # Asumimos que el CWD es el root de consultorio_app
            tests_dir = os.path.join(os.getcwd(), 'tests')
            if not os.path.isdir(tests_dir):
                logger.warning(f'Tests directory no encontrado: {tests_dir}')

            # Comando: usar el mismo intérprete de Python
            cmd = [sys.executable, '-m', 'pytest', 'tests']
            logger.info(f'Ejecutando: {" ".join(cmd)} (cwd={os.getcwd()})')

            # Ejecutar y capturar salida
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=os.getcwd(),
                text=True,
                bufsize=1
            )

            # Volcar salida línea a línea al log
            for line in process.stdout:
                logger.info(line.rstrip())

            return_code = process.wait()
            if return_code == 0:
                logger.info('✅ Tests completados con éxito (exit=0)')
            else:
                logger.error(f'❌ Tests fallaron (exit={return_code})')

        except Exception as e:
            logger.exception(f'Error ejecutando tests: {e}')
