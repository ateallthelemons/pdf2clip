from setuptools import setup

APP = ["main.py"]
OPTIONS = {
    "argv_emulation": True,
    "packages": ["fitz", "PIL"],
    "iconfile": "icon.icns",
    "plist": {
        "CFBundleName": "pdf2clip",
        "CFBundleIdentifier": "com.mk.pdf2clip",
        "CFBundleShortVersionString": "1.2",
    },
}

setup(
    app=APP,
    name="pdf2clip",
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)


# build:
# 1. source venv/bin/activate
# 2. python setup.py py2app -A
# 3. python setup.py py2app 