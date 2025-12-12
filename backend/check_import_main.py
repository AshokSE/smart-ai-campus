import importlib, traceback

try:
    importlib.import_module('main')
    print('IMPORT_OK')
except Exception:
    print('IMPORT_ERROR')
    traceback.print_exc()
