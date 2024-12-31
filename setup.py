from setuptools import setup, Extension
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        [
            Extension(
                "app.routes.research",  # Module name (use the dotted module path)
                ["app/routes/research.py"],  # Path to the .py file
            )
        ],
        compiler_directives={"language_level": "3"},  # Use Python 3 syntax
    ),
)
