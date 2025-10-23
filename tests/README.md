# Theme Format Tests

Automated tests to ensure Looped themes maintain correct format specifications for both Zed and VS Code.

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test class
python -m pytest tests/test_theme_formats.py::TestZedThemeFormat -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html
```

## Test Coverage

### Zed Theme Tests (`TestZedThemeFormat`)
- ✅ File existence
- ✅ Root structure ($schema, name, author, themes)
- ✅ Theme variants (dark/light with appearance)
- ✅ Required UI properties (background, foreground, borders, etc.)
- ✅ Syntax highlighting structure
- ✅ Syntax scope format (no `syntax.` prefix)
- ✅ No VS Code-specific properties leaked
- ✅ Color format validation (hex colors)

### VS Code Theme Tests (`TestVSCodeThemeFormat`)
- ✅ File existence (dark and light variants)
- ✅ Root structure ($schema, name, type, colors, tokenColors)
- ✅ Colors object structure
- ✅ TokenColors array structure
- ✅ No Zed-specific properties leaked
- ✅ Color format validation

### Consistency Tests (`TestThemeConsistency`)
- ✅ Theme names contain "Looped"
- ✅ Primary colors defined across all variants

## What These Tests Catch

1. **Format Errors**: Wrong schema, missing required fields
2. **Cross-contamination**: VS Code properties in Zed themes (and vice versa)
3. **Syntax Issues**: Incorrect scope names, missing color properties
4. **Color Format Issues**: Invalid hex colors, wrong format
5. **Structure Issues**: Missing sections, wrong data types

## Adding New Tests

When adding new theme properties or features:

1. Add validation to the appropriate test class
2. Run tests to ensure existing themes pass
3. Commit tests alongside theme changes

Example:
```python
def test_new_property(self, zed_theme):
    """Test description."""
    for theme in zed_theme["themes"]:
        assert "new.property" in theme["style"], "Missing new property"
```
