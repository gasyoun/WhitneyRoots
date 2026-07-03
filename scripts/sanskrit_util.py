# -*- coding: utf-8 -*-
"""Compatibility shim — the real implementation now lives in the shared `sanskrit-util`
package so this repo no longer carries its own copy of the SLP1/IAST/Devanāgarī logic.

This re-exports the sibling package (GitHub/sanskrit-util) by relative path, so every existing
`from sanskrit_util import to_slp1, from_slp1, to_roman, form_key, norm, nfold` keeps working
unchanged. Implementation, tests and the golden vectors: ../../sanskrit-util/.

If you relocate this repo away from the GitHub-root layout, install the package instead and
delete this shim:  pip install -e <path>/sanskrit-util/py
"""
import importlib.util as _ilu
import os as _os

_here = _os.path.dirname(_os.path.abspath(__file__))
_pkg_init = _os.path.abspath(_os.path.join(_here, '..', '..', 'sanskrit-util', 'py', 'sanskrit_util', '__init__.py'))

if not _os.path.exists(_pkg_init):
    raise ImportError(
        "shared 'sanskrit-util' package not found at %s — restore the sibling repo or run "
        "`pip install -e <path>/sanskrit-util/py` (then you can delete this shim)." % _pkg_init
    )

# Load under a distinct module name so it never shadows / recurses into this shim file.
_spec = _ilu.spec_from_file_location('_sanskrit_util_shared', _pkg_init)
_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

# Re-export the public API (to_slp1, from_slp1, to_roman, deva_to_iast, iast_to_devanagari,
# norm, nfold, form_key, normalize_sanskrit).
globals().update({_k: getattr(_mod, _k) for _k in _mod.__all__})
__all__ = list(_mod.__all__)
__version__ = getattr(_mod, '__version__', None)
