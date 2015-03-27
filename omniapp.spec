# -*- mode: python -*-
a = Analysis(['.\\omniapp.py'],
             pathex=['C:\\Projects\\omni3d-app'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='omniapp.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False)

data_files = Tree("resources/images", prefix="resources/images") + \
             Tree("omni3dapp/gui/qml", prefix="omni3dapp/gui/qml") + \
             [("CuraEngine/CuraEngine", "CuraEngine/CuraEngine", "DATA")]

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               data_files,
               strip=None,
               upx=True,
               name='omniapp')
