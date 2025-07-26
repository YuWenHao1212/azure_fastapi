# Flexible Input Formats Reference

**Last Updated**: 2025-07-10

## Overview

The Resume Tailoring API accepts multiple input formats for gap analysis fields, making it easy to integrate with various platforms like Bubble.io.

## Quick Reference Table

| Field | Accepted Formats | Example |
|-------|-----------------|---------|
| `core_strengths` | • Multi-line text<br>• Array<br>• HTML list | See below |
| `key_gaps` | • Multi-line text<br>• Array<br>• HTML list | See below |
| `quick_improvements` | • Multi-line text<br>• Array<br>• HTML list | See below |
| `covered_keywords` | • Comma separated<br>• Semicolon separated<br>• Array | See below |
| `missing_keywords` | • Comma separated<br>• Semicolon separated<br>• Array | See below |

## Detailed Format Examples

### Multi-line Text Format

```json
{
  "core_strengths": "Strong Python skills\nMachine learning expertise\nTeam leadership experience"
}
```

**Parsed Result**: `["Strong Python skills", "Machine learning expertise", "Team leadership experience"]`

### HTML List Format

```json
{
  "core_strengths": "<ul><li>Strong Python skills</li><li>Machine learning expertise</li><li>Team leadership experience</li></ul>"
}
```

**Parsed Result**: `["Strong Python skills", "Machine learning expertise", "Team leadership experience"]`

### Numbered List Format

```json
{
  "quick_improvements": "1. Add cloud certifications\n2. Highlight leadership roles\n3. Include metrics in achievements"
}
```

**Parsed Result**: `["Add cloud certifications", "Highlight leadership roles", "Include metrics in achievements"]`

### Comma-Separated Keywords

```json
{
  "covered_keywords": "Python, Machine Learning, Data Analysis, SQL"
}
```

**Parsed Result**: `["Python", "Machine Learning", "Data Analysis", "SQL"]`

### Mixed Separators

```json
{
  "missing_keywords": "AWS;Docker,Kubernetes\nTerraform;CI/CD"
}
```

**Parsed Result**: `["AWS", "Docker", "Kubernetes", "Terraform", "CI/CD"]`

### Array Format (Traditional)

```json
{
  "core_strengths": ["Strong Python skills", "Machine learning expertise", "Team leadership"]
}
```

**Parsed Result**: `["Strong Python skills", "Machine learning expertise", "Team leadership"]`

## Parsing Rules

### Text Item Parsing
1. Split by newlines (`\n`)
2. Remove HTML tags
3. Remove bullet markers (`•`, `·`, `◦`, `-`, `*`)
4. Remove numbering (`1.`, `2)`, etc.)
5. Trim whitespace
6. Filter empty items

### Keyword Parsing
1. Try comma split first
2. If only one item, try semicolon split
3. If still one item, try newline split
4. Handle concatenated keywords (e.g., "Python,Java,C++" → ["Python", "Java", "C++"])
5. Trim whitespace
6. Filter empty items

## Edge Cases Handled

### Empty or Whitespace
```json
{
  "core_strengths": "   \n\n   "
}
```
**Result**: `[]` (empty array)

### Mixed Formatting
```json
{
  "quick_improvements": "• Add certifications\n2) Update summary\n- Include metrics"
}
```
**Result**: `["Add certifications", "Update summary", "Include metrics"]`

### HTML with Nested Tags
```json
{
  "core_strengths": "<ul><li><strong>Python</strong> expertise</li><li>Machine <em>learning</em></li></ul>"
}
```
**Result**: `["Python expertise", "Machine learning"]`

### Keywords Without Spaces
```json
{
  "missing_keywords": "AWS,Docker,Kubernetes,Terraform"
}
```
**Result**: `["AWS", "Docker", "Kubernetes", "Terraform"]`

## Platform-Specific Tips

### Bubble.io
- Use multi-line input elements for strengths/gaps/improvements
- Use single-line input for keywords
- No preprocessing needed - raw values work directly

### Form Builders
- Textarea fields → Multi-line format
- Text inputs → Comma-separated format
- Checkbox groups → Join with commas

### Programmatic Usage
- Arrays are always accepted
- Strings are automatically parsed
- Mix formats as needed

## Testing Your Format

Use this simple test endpoint to verify your format:

```bash
curl -X POST "http://localhost:8000/api/v1/test-parsing" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your text here"
  }'
```

## Common Mistakes to Avoid

1. **Don't double-encode**: Send raw text, not JSON-escaped strings
2. **Don't pre-split**: The API handles splitting automatically
3. **Don't worry about extra spaces**: Trimming is automatic
4. **Don't mix array and string**: Use one format per field

---

*For more details, see the full [API Documentation](./API_RESUME_TAILORING_V1.md)*