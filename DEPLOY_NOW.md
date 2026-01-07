# 🚀 Ready to Deploy: maximus-client

## ✅ Everything is Prepared!

Your package is ready for deployment to PyPI with the name `maximus-client`.

### Package Details
- **Name**: `maximus-client`
- **Version**: `0.1.0`
- **Author**: `Vodeninja <root@vodeninja.ru>`
- **Repository**: `https://github.com/Vodeninja/maximus-client`

### Quick Deploy Commands

#### Option 1: Use the deployment script (Recommended)
```bash
python deploy.py
```

#### Option 2: Manual deployment
```bash
# Install build tools
pip install --upgrade pip build twine

# Clean and build
rm -rf build dist *.egg-info
python -m build

# Check package
python -m twine check dist/*

# Test on TestPyPI first
python -m twine upload --repository testpypi dist/*

# Deploy to PyPI
python -m twine upload dist/*
```

#### Option 3: Windows users
```cmd
deploy.bat
```

### After Deployment

Users will install your package with:
```bash
pip install maximus-client
```

And use it like:
```python
from maximus import MaxClient

client = MaxClient()
# ... your code
```

### Files Updated for Deployment

✅ `setup.py` - Package name changed to `maximus-client`
✅ `pyproject.toml` - Package name and author info updated  
✅ `README.md` - Installation instructions updated
✅ `.github/workflows/python-publish.yml` - GitHub Actions configured
✅ `deploy.py` - Deployment script created
✅ `DEPLOYMENT.md` - Complete deployment guide created

### Ready to Go! 🎉

Your package is fully prepared for PyPI deployment. Just run `python deploy.py` and follow the prompts!