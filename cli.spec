from pathlib import Path

from PyInstaller.building.build_main import Analysis
from PyInstaller.building.api import PYZ, EXE, COLLECT

import lark

a = Analysis(
	['cli.py'],
	datas = [
	('qry/grammar.lark', 'qry'),
	(Path(lark.__file__).parent / 'grammars', 'lark/grammars'),
	],
)

pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, name = 'qry', console = True)
