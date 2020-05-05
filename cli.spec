from pathlib import Path

from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE, COLLECT

import lark

a = Analysis(
	['cli.py'],
	datas = [
	('qry/lang/grammar.lark', 'qry/lang'),
	(Path(lark.__file__).parent / 'grammars', 'lark/grammars'),
	],
	hiddenimports = ['pkg_resources.py2_warn'],
)

pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name = 'qry', console = True)
