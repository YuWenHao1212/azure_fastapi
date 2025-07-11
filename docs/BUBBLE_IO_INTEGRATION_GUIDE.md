# Bubble.io Integration Guide for Resume Tailoring API

**Version**: 1.0  
**Last Updated**: 2025-07-10  
**API Version**: v1

## Overview

This guide provides step-by-step instructions for integrating the Resume Tailoring API with Bubble.io applications. The API has been specifically designed to be compatible with Bubble.io's requirements and data handling.

## Table of Contents
1. [API Compatibility Features](#api-compatibility-features)
2. [Setting Up API Connector](#setting-up-api-connector)
3. [Handling Input Formats](#handling-input-formats)
4. [Processing Responses](#processing-responses)
5. [Common Integration Patterns](#common-integration-patterns)
6. [Troubleshooting](#troubleshooting)

## API Compatibility Features

### Bubble.io Specific Design Choices
- ✅ All responses return HTTP 200 (even for errors)
- ✅ No optional fields - all fields always present
- ✅ Flexible input parsing for various text formats
- ✅ Consistent JSON structure for success and error cases
- ✅ String inputs accepted for array fields

## Setting Up API Connector

### Step 1: Add API Connector Plugin
1. Go to your Bubble.io app's Plugins tab
2. Add the "API Connector" plugin if not already installed

### Step 2: Create New API Connection
1. Click "Add another API"
2. Name it: "Resume Tailoring API"
3. Authentication: None (or add your auth if implemented)

### Step 3: Configure API Call

```
Name: Tailor Resume
Use as: Action
Data type: JSON
Method: POST
URL: https://airesumeadvisor-fastapi.azurewebsites.net/api/v1/tailor-resume
```

### Step 4: Set Headers
```
Content-Type: application/json
```

### Step 5: Configure Body
```json
{
  "job_description": "<job_description>",
  "original_resume": "<original_resume>",
  "gap_analysis": {
    "core_strengths": "<core_strengths>",
    "key_gaps": "<key_gaps>",
    "quick_improvements": "<quick_improvements>",
    "covered_keywords": "<covered_keywords>",
    "missing_keywords": "<missing_keywords>"
  },
  "options": {
    "include_visual_markers": <include_markers>,
    "language": "<language>"
  }
}
```

### Step 6: Initialize Call
Use this test data for initialization:
```json
{
  "job_description": "We are looking for a Senior Software Engineer with expertise in Python, cloud platforms, and machine learning. The ideal candidate should have 5+ years of experience.",
  "original_resume": "<h1>John Doe</h1><p>Software Engineer with 4 years of experience in Python development and data analysis.</p><h2>Skills</h2><ul><li>Python</li><li>Data Analysis</li></ul>",
  "gap_analysis": {
    "core_strengths": "Strong Python programming skills\nData analysis expertise\nProblem-solving abilities",
    "key_gaps": "Limited cloud platform experience\nNo machine learning projects mentioned\nMissing senior-level positioning",
    "quick_improvements": "Add cloud platform certifications\nHighlight any ML-related work\nEmphasize leadership experiences",
    "covered_keywords": "Python, Software Engineer, Data Analysis",
    "missing_keywords": "Senior, Cloud, Machine Learning, AWS, Leadership"
  },
  "options": {
    "include_visual_markers": true,
    "language": "en"
  }
}
```

## Handling Input Formats

### From Bubble.io Multi-line Input

When users enter text in a multi-line input in Bubble.io:

```javascript
// Bubble.io Expression
Multiline Input's value
```

This automatically works with the API's flexible parsing:
- Line breaks are preserved
- No preprocessing needed
- Bullet points are automatically detected

### From Bubble.io Text Input (Keywords)

For comma-separated keywords:
```javascript
// Bubble.io Expression
Input Keywords's value
// User enters: "Python, Machine Learning, Docker"
```

### From Repeating Group Data

If collecting items from a repeating group:
```javascript
// Bubble.io Expression
RepeatingGroup's List of Texts:join with ","
```

### Dynamic Data Formatting

```javascript
// In Bubble.io workflow
// Step 1: Call API - Tailor Resume
job_description = Input Job Description's value
original_resume = Input Resume's value
core_strengths = Multiline Strengths's value
key_gaps = Multiline Gaps's value
quick_improvements = Multiline Improvements's value
covered_keywords = Input Covered Keywords's value
missing_keywords = Input Missing Keywords's value
include_markers = Checkbox Include Markers's value
language = Dropdown Language's value
```

## Processing Responses

### Success Handling

```javascript
// Bubble.io Workflow
When API call returns:
  // Check success
  Only when: Result of Step 1's success is "yes"
  
  // Display optimized resume
  Set state optimized_resume = Result of Step 1's data:optimized_resume
  
  // Show statistics
  Set state sections_modified = Result of Step 1's data:optimization_stats:sections_modified
  Set state keywords_added = Result of Step 1's data:optimization_stats:keywords_added
```

### Error Handling

```javascript
// Bubble.io Workflow
When API call returns:
  // Check for error
  Only when: Result of Step 1's success is "no"
  
  // Display error message
  Show alert: Result of Step 1's error:message
  
  // Log error details
  Set state error_code = Result of Step 1's error:code
  Set state error_details = Result of Step 1's error:details
```

### Displaying the Optimized Resume

#### Option 1: HTML Element
```html
<!-- In HTML element -->
<style>
  .opt-strength { background-color: #e3f2fd; font-weight: bold; }
  .opt-keyword { background-color: #fff3cd; }
  .opt-placeholder { background-color: #f8d7da; font-style: italic; }
  .opt-new { border-left: 3px solid #28a745; padding-left: 10px; }
  .opt-improvement { text-decoration: underline; }
</style>

<!-- Dynamic expression -->
Current Page's optimized_resume
```

#### Option 2: Rich Text Editor
If using Bubble's Rich Text Editor:
1. Set the initial content to the optimized resume
2. The visual markers (CSS classes) will be preserved
3. Users can further edit the optimized content

## Common Integration Patterns

### Pattern 1: Multi-Step Resume Builder

```javascript
// Step 1: Extract keywords from job description
API Call: Extract Keywords
Input: job_description

// Step 2: Perform gap analysis
API Call: Gap Analysis
Inputs: job_description, original_resume, keywords

// Step 3: Tailor resume
API Call: Tailor Resume
Inputs: job_description, original_resume, gap_analysis_result

// Step 4: Display results
Show optimized resume with visual feedback
```

### Pattern 2: Batch Processing

```javascript
// For multiple resumes
Schedule API Workflow on a list:
  List to run on: Search for Resumes
  
  API Call: Tailor Resume
  job_description = Current job posting's description
  original_resume = This Resume's content
  gap_analysis = This Resume's gap_analysis
```

### Pattern 3: Save and Track Changes

```javascript
// After successful optimization
Create a new Optimization Record:
  original_resume = Input Resume's value
  optimized_resume = API Result's data:optimized_resume
  improvements = API Result's data:applied_improvements:join with ", "
  keywords_added = API Result's data:optimization_stats:keywords_added
  timestamp = Current date/time
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Validation Error (422)
**Error**: "String should have at least 50 characters"
```javascript
// Solution: Add validation before API call
Only when: Input Job Description's value:number of characters > 50
AND Input Resume's value:number of characters > 100
```

#### Issue 2: Empty Response Fields
**Problem**: Gap analysis fields showing as empty
```javascript
// Solution: Provide default values
core_strengths = Multiline Strengths's value:defaulting to "No strengths provided"
```

#### Issue 3: Timeout Errors
**Problem**: API call times out
```javascript
// Solution: Increase timeout in API Connector
// Set timeout to 60000ms (60 seconds)
```

#### Issue 4: Formatting Issues
**Problem**: Line breaks not preserved
```javascript
// Solution: Use :formatted as JSON safe
core_strengths = Multiline Input's value:formatted as JSON safe
```

### Debug Checklist

1. **Check Input Lengths**
   - Job description ≥ 50 characters
   - Resume ≥ 100 characters

2. **Verify Data Format**
   - Use Bubble's debugger to inspect actual values sent
   - Check for unexpected null values

3. **Monitor API Logs**
   - Check Bubble.io's API workflow logs
   - Review response details in debugger

4. **Test with Static Data**
   - First test with hardcoded values
   - Then replace with dynamic data

## Best Practices

### 1. Input Validation
```javascript
// Add conditions to check inputs
When Button Optimize is clicked:
  Only when:
    Input Job Description is not empty
    AND Input Resume is not empty
    AND Input Job Description's value:number of characters > 50
```

### 2. Loading States
```javascript
// Show loading indicator
When Button Optimize is clicked:
  Show Loading Popup
  
When API call returns:
  Hide Loading Popup
```

### 3. Error Recovery
```javascript
// Implement retry logic
When API call fails:
  Only when: retry_count < 3
  Schedule API workflow (current workflow) in 2 seconds
  Set state retry_count = retry_count + 1
```

### 4. Data Persistence
```javascript
// Save API responses
Create new API Log:
  request_data = [save input data]
  response_data = Result of API call
  success = Result of API call's success
  timestamp = Current date/time
```

## Example Bubble.io Workflow

### Complete Resume Optimization Flow

1. **Page Load**
   ```
   Set default language = "en"
   Set include_markers = "yes"
   ```

2. **User Inputs Data**
   ```
   Multiline inputs for:
   - Job Description
   - Resume
   - Core Strengths  
   - Key Gaps
   - Quick Improvements
   
   Text inputs for:
   - Covered Keywords (comma-separated)
   - Missing Keywords (comma-separated)
   ```

3. **Optimize Button Click**
   ```
   Show Loading Popup
   
   API Call: Tailor Resume
   [Map all inputs to API parameters]
   ```

4. **Handle Response**
   ```
   When API returns AND success is "yes":
     Hide Loading Popup
     Go to page: Results
     Display data optimized_resume in HTML element
     Show statistics in text elements
   
   When API returns AND success is "no":
     Hide Loading Popup
     Show Alert with error message
   ```

## Support Resources

- **API Documentation**: [API_RESUME_TAILORING_V1.md](./API_RESUME_TAILORING_V1.md)
- **Test Endpoint**: Use Postman or curl to test outside Bubble.io
- **GitHub Issues**: Report integration issues with Bubble.io tag

---

*For additional support, contact: support@airesumeadvisor.com*