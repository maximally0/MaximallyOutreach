# Maximally Outreach Dashboard

## Overview

This is a Flask-based web application designed for educational outreach campaigns. The system allows users to upload school data, manage email templates, and send personalized outreach emails to educational institutions. It features template management, A/B testing capabilities, and email tracking functionality. The application is fully operational with Resend API integration configured for sending emails from hello@maximally.in.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology**: Traditional server-side rendered HTML with Bootstrap CSS framework
- **Styling**: Bootstrap with dark theme and Bootstrap Icons
- **JavaScript**: Vanilla JavaScript for client-side interactions
- **Templates**: Jinja2 templating engine for dynamic content rendering

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Monolithic application with single `app.py` file
- **Session Management**: Flask's built-in session handling with secret key
- **Entry Point**: `main.py` serves as the application runner

### Data Storage Solutions
- **Primary Storage**: JSON files for persistent data storage
- **File Structure**:
  - `data/schools.json` - School contact information
  - `data/templates.json` - Email templates with placeholders
  - `data/logs.json` - Email sending activity logs
- **File Uploads**: CSV processing for bulk school data import

### Authentication and Authorization
- **Current State**: No authentication system implemented
- **Session Security**: Basic session secret key configuration
- **Access Control**: Open access to all functionality

## Key Components

### Data Management
- **School Data**: CSV upload and JSON storage system for school information (name, email, contact person, city)
- **Template System**: Pre-defined email templates with variable placeholders ({{school_name}}, {{contact_person}}, {{city}})
- **Template Management**: Full CRUD operations - create, edit, delete, and customize email templates through web interface
- **Logging**: Activity tracking for sent emails and system events

### Email System
- **Provider**: Resend API integration for email delivery from hello@maximally.in
- **Features**: Template-based personalized emails with variable substitution
- **Custom Emails**: Send emails without templates using custom subject and content
- **Auto-Remove Feature**: Automatically removes schools from the list after successfully sending emails to prevent duplicate outreach
- **HTML Support**: Rich email formatting with image support via HTML content
- **A/B Testing**: Support for testing multiple templates simultaneously
- **Test Email**: Send current form content to rishulchanana36@gmail.com with sample school data for validation
- **Dual Format**: Support for both plain text and HTML emails with automatic fallback

### User Interface
- **Dashboard**: Single-page interface with multiple functional sections
- **File Upload**: CSV import functionality for bulk school data  
- **Template Management**: Interface for creating, editing, deleting, and selecting email templates
- **Custom Email Composer**: Rich text and HTML email composition with image support
- **Test Email System**: Send current email content to rishulchanana36@gmail.com for validation
- **Four Email Options**: Preview, Test, Custom Send, and Template Send with clear explanations
- **Bulk Operations**: Select all/individual school targeting options
- **Preview System**: Preview emails with personalized content before sending
- **Help Integration**: Tooltip explanations and info alerts for all features

## Data Flow

1. **Data Import**: Users upload CSV files containing school information
2. **Template Management**: Users create, edit, or delete email templates as needed
3. **Email Composition**: Users can use templates, create custom emails, or send tests
4. **Content Options**: Support for plain text, HTML with images, or both formats
5. **Target Selection**: Users select specific schools or all schools for outreach
6. **Validation**: Preview and test email functionality before sending to schools
7. **Email Processing**: System personalizes content with school-specific data
8. **Email Delivery**: Resend API handles email transmission with dual format support
9. **Activity Logging**: System records all email activities including tests and custom emails

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **Pandas**: CSV data processing and manipulation
- **Resend**: Email delivery service integration

### Frontend Dependencies
- **Bootstrap CSS**: UI framework with dark theme
- **Bootstrap Icons**: Icon library for user interface elements

### Environment Variables
- **RESEND_API_KEY**: Email service authentication (configured and active)
- **SESSION_SECRET**: Flask session security key

## Deployment Strategy

### Current Configuration
- **Development**: Flask development server on port 5000
- **Host Binding**: Configured for 0.0.0.0 (all interfaces)
- **Debug Mode**: Enabled for development environment

### File System Requirements
- **Data Directory**: Auto-created 'data' folder for JSON storage
- **Template Initialization**: Automatic creation of default email templates
- **Error Handling**: JSON file loading with fallback mechanisms

### Environment Setup
- **Python Environment**: Requires Flask, Pandas, and Resend libraries
- **File Permissions**: Write access needed for data directory
- **API Configuration**: Resend API key must be configured for email functionality

The application is designed as a simple, self-contained system suitable for small to medium-scale educational outreach campaigns, with room for future enhancements like user authentication, database integration, and advanced analytics.

## Recent Changes

### July 23, 2025 - Complete HTML Template System Implementation + Auto-Remove Feature
- **Fixed HTML Template Editor**: Resolved ID conflicts between plain text and HTML content areas with separate storage fields
- **Updated Test Email System**: Test emails now use actual template content with proper HTML/text format detection
- **Enhanced Preview System**: Added professional email-like styling with clean white background and blue links for previews
- **Improved Template Management**: Separate storage for content_text and content_html with proper form submission handling
- **Email Delivery Enhancement**: Updated email sending to properly handle HTML content for both test emails and school outreach
- **Template Syntax Fix**: Resolved Jinja2 template conflicts with JavaScript template literals
- **Preview Modal Integration**: Added complete email preview modal with HTML rendering and proper typography
- **Auto-Remove Schools Feature**: Implemented automatic removal of schools from list after successfully sending emails to prevent duplicate outreach