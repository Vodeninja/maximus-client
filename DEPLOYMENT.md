# Deployment Guide for maximus-client

## Pre-Deployment Checklist

### 1. Code Quality
- [ ] All code is tested and working
- [ ] Documentation is up to date
- [ ] Version number is updated in all files
- [ ] No debug prints or test code in production

### 2. Package Configuration
- [ ] `setup.py` has correct package name: `maximus-client`
- [ ] `pyproject.toml` has correct package name: `maximus-client`
- [ ] Author information is correct: `Vodeninja <root@vodeninja.ru>`
- [ ] GitHub URLs point to: `https://github.com/Vodeninja/maximus-client`
- [ ] Version numbers match across all files

### 3. Dependencies
- [ ] `requirements.txt` lists all required packages
- [ ] No unnecessary dependencies
- [ ] Version constraints are appropriate

### 4. Documentation
- [ ] README.md has correct installation instructions
- [ ] API documentation is complete
- [ ] Examples work with current version

## Deployment Methods

### Method 1: Using Deployment Script (Recommended)

```bash
python deploy.py
```

Choose option:
1. **Build and test** - Just build and verify package
2. **Upload to TestPyPI** - Test deployment
3. **Upload to PyPI** - Production deployment
4. **Full deployment** - TestPyPI → PyPI

### Method 2: Manual Commands

```bash
# Clean previous builds
rm -rf build dist *.egg-info

# Install build tools
pip install --upgrade pip build twine

# Build package
python -m build

# Check package
python -m twine check dist/*

# Upload to TestPyPI (test first!)
python -m twine upload --repository testpypi dist/*

# Upload to PyPI (production)
python -m twine upload dist/*
```

### Method 3: GitHub Actions (Automatic)

1. Push code to GitHub
2. Create a new release with version tag (e.g., `v0.1.0`)
3. GitHub Actions will automatically build and publish to PyPI

## Version Management

Update version in these files:
- `setup.py` - line with `version="0.1.0"`
- `pyproject.toml` - line with `version = "0.1.0"`
- `maximus/__init__.py` - line with `__version__ = "0.1.0"`

## PyPI Setup

### For Trusted Publishing (GitHub Actions)
1. Go to https://pypi.org/manage/account/publishing/
2. Add publisher:
   - Owner: `Vodeninja`
   - Repository: `maximus-client`
   - Workflow: `python-publish.yml`
   - Environment: `pypi`

### For Manual Publishing
1. Create PyPI account
2. Generate API token
3. Configure in `~/.pypirc`:
```ini
[pypi]
username = __token__
password = pypi-your-api-token-here
```

## Testing Deployment

### Test on TestPyPI first:
```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation
pip install -i https://test.pypi.org/simple/ maximus-client

# Test import
python -c "import maximus; print('Success!')"
```

### Verify on PyPI:
```bash
# After PyPI upload, test installation
pip install maximus-client

# Test import
python -c "import maximus; print('Success!')"
```

## Post-Deployment

1. **Verify package on PyPI**: https://pypi.org/project/maximus-client/
2. **Test installation**: `pip install maximus-client`
3. **Update documentation** with new version
4. **Create GitHub release** with changelog
5. **Announce** on relevant channels

## Troubleshooting

### Common Issues

**Package name already exists:**
- Use different name or contact PyPI support

**Upload fails:**
- Check credentials
- Verify package format with `twine check`
- Ensure version number is unique

**Import fails after installation:**
- Check package structure
- Verify `__init__.py` exports
- Test in clean environment

**GitHub Actions fails:**
- Check trusted publishing setup
- Verify workflow permissions
- Check environment configuration

## Version History

- `0.1.0` - Initial release
  - Basic MAX messenger client
  - WebSocket communication
  - Event-driven architecture
  - Session management

## Support

For deployment issues:
- Check GitHub Issues: https://github.com/Vodeninja/maximus-client/issues
- Contact: root@vodeninja.ru