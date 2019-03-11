# -*- mode: python -*-

block_cipher = None


a = Analysis(['workoutjournal.py'],
             pathex=['/Users/iverhakonsen/Documents/Skole/2.vår/Datamodellering og databasesystemer/Databaseprosjekt/src'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='workoutjournal',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )

a.datas += [
    ("/Users/iverhakonsen/Documents/Skole/2.vår/Datamodellering og databasesystemer/Databaseprosjekt/src/SQL/maketables.sql", "SQL/maketables.sql", "DATA")
]
